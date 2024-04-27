from owrx.config import Config
from owrx.property import PropertyManager, PropertyDeleted, PropertyDelegator, PropertyLayer, PropertyReadOnly
from owrx.feature import FeatureDetector, UnknownFeatureException
from owrx.source import SdrSource, SdrSourceEventClient
from functools import partial

import logging

logger = logging.getLogger(__name__)


class MappedSdrSources(PropertyDelegator):
    def __init__(self, pm: PropertyManager):
        self.subscriptions = {}
        super().__init__(PropertyLayer())
        for key, value in pm.items():
            self._addSource(key, value)
        pm.wire(self.handleSdrDeviceChange)

    def handleSdrDeviceChange(self, changes):
        for key, value in changes.items():
            if value is PropertyDeleted:
                if key in self:
                    del self[key]
            else:
                if key not in self:
                    self._addSource(key, value)

    def handleDeviceUpdate(self, key, value, *args):
        if key not in self and self.isDeviceValid(value):
            self[key] = self.buildNewSource(key, value)
        elif key in self and not self.isDeviceValid(value):
            del self[key]

    def _addSource(self, key, value):
        self.handleDeviceUpdate(key, value)
        updateMethod = partial(self.handleDeviceUpdate, key, value)
        self.subscriptions[key] = [
            value.filter("type", "profiles").wire(updateMethod),
            value["profiles"].wire(updateMethod)
        ]

    def isDeviceValid(self, device):
        return self._sdrTypeAvailable(device) and self._hasProfiles(device)

    def _hasProfiles(self, device):
        return "profiles" in device and device["profiles"] and len(device["profiles"]) > 0

    def _sdrTypeAvailable(self, value):
        featureDetector = FeatureDetector()
        try:
            if not featureDetector.is_available(value["type"]):
                logger.error(
                    'The SDR source type "{0}" is not available. please check the feature report for details.'.format(
                        value["type"]
                    )
                )
                return False
            return True
        except UnknownFeatureException:
            logger.error(
                'The SDR source type "{0}" is invalid. Please check your configuration'.format(value["type"])
            )
            return False

    def buildNewSource(self, id, props):
        sdrType = props["type"]
        className = "".join(x for x in sdrType.title() if x.isalnum()) + "Source"
        module = __import__("owrx.source.{0}".format(sdrType), fromlist=[className])
        cls = getattr(module, className)
        return cls(id, props)

    def _removeSource(self, key, source):
        source.shutdown()
        for sub in self.subscriptions[key]:
            sub.cancel()
        del self.subscriptions[key]

    def __setitem__(self, key, value):
        source = self[key] if key in self else None
        if source is value:
            return
        super().__setitem__(key, value)
        if source is not None:
            self._removeSource(key, source)

    def __delitem__(self, key):
        source = self[key] if key in self else None
        super().__delitem__(key)
        if source is not None:
            self._removeSource(key, source)


class SourceStateHandler(SdrSourceEventClient):
    def __init__(self, pm, key, source: SdrSource):
        self.pm = pm
        self.key = key
        self.source = source

    def selfDestruct(self):
        self.source.removeClient(self)

    def onFail(self):
        pass

    def onDisable(self):
        del self.pm[self.key]

    def onEnable(self):
        self.pm[self.key] = self.source

    def onShutdown(self):
        del self.pm[self.key]


class ActiveSdrSources(PropertyReadOnly):
    def __init__(self, pm: PropertyManager):
        self.handlers = {}
        self._layer = PropertyLayer()
        super().__init__(self._layer)
        for key, value in pm.items():
            self._addSource(key, value)
        pm.wire(self.handleSdrDeviceChange)

    def handleSdrDeviceChange(self, changes):
        for key, value in changes.items():
            if value is PropertyDeleted:
                self._removeSource(key)
            else:
                self._addSource(key, value)

    def isAvailable(self, source: SdrSource):
        return source.isEnabled() and not source.isFailed()

    def _addSource(self, key, source: SdrSource):
        if self.isAvailable(source):
            self._layer[key] = source
        self.handlers[key] = SourceStateHandler(self._layer, key, source)
        source.addClient(self.handlers[key])

    def _removeSource(self, key):
        self.handlers[key].selfDestruct()
        del self.handlers[key]
        if key in self._layer:
            del self._layer[key]


class AvailableProfiles(PropertyReadOnly):
    def __init__(self, pm: PropertyManager):
        self.subscriptions = {}
        self.profileSubscriptions = {}
        self._layer = PropertyLayer()
        super().__init__(self._layer)
        for key, value in pm.items():
            self._addSource(key, value)
        pm.wire(self.handleSdrDeviceChange)

    def handleSdrDeviceChange(self, changes):
        for key, value in changes.items():
            if value is PropertyDeleted:
                self._removeSource(key)
            else:
                self._addSource(key, value)

    def handleSdrNameChange(self, s_id, source, name):
        profiles = source.getProfiles()
        for p_id in list(self._layer.keys()):
            source_id, profile_id = p_id.split("|")
            if source_id == s_id:
                profile = profiles[profile_id]
                self._layer[p_id] = "{} {}".format(name, profile["name"])

    def handleProfileChange(self, source_id, source: SdrSource, changes):
        for key, value in changes.items():
            if value is PropertyDeleted:
                self._removeProfile(source_id, key)
            else:
                self._addProfile(source_id, source, key, value)

    def handleProfileNameChange(self, s_id, source: SdrSource, p_id, name):
        for concat_p_id in list(self._layer.keys()):
            source_id, profile_id = concat_p_id.split("|")
            if source_id == s_id and profile_id == p_id:
                self._layer[concat_p_id] = "{} {}".format(source.getName(), name)

    def _addSource(self, key, source: SdrSource):
        for p_id, p in source.getProfiles().items():
            self._addProfile(key, source, p_id, p)
        self.subscriptions[key] = [
            source.getProps().wireProperty("name", partial(self.handleSdrNameChange, key, source)),
            source.getProfiles().wire(partial(self.handleProfileChange, key, source)),
        ]

    def _addProfile(self, s_id, source: SdrSource, p_id, profile):
        self._layer["{}|{}".format(s_id, p_id)] = "{} {}".format(source.getName(), profile["name"])
        if s_id not in self.profileSubscriptions:
            self.profileSubscriptions[s_id] = {}
        self.profileSubscriptions[s_id][p_id] = profile.wireProperty("name", partial(self.handleProfileNameChange, s_id, source, p_id))

    def _removeSource(self, key):
        for profile_id in list(self._layer.keys()):
            if profile_id.startswith("{}|".format(key)):
                del self._layer[profile_id]
        if key in self.subscriptions:
            while self.subscriptions[key]:
                self.subscriptions[key].pop().cancel()
            del self.subscriptions[key]
        if key in self.profileSubscriptions:
            for p_id in self.profileSubscriptions[key].keys():
                self.profileSubscriptions[key][p_id].cancel()
            del self.profileSubscriptions[key]

    def _removeProfile(self, s_id, p_id):
        for concat_p_id in list(self._layer.keys()):
            source_id, profile_id = concat_p_id.split("|")
            if source_id == s_id and profile_id == p_id:
                del self._layer[concat_p_id]
        if s_id in self.profileSubscriptions and p_id in self.profileSubscriptions[s_id]:
            self.profileSubscriptions[s_id][p_id].cancel()
            del self.profileSubscriptions[s_id][p_id]


class SdrService(object):
    sources = None
    activeSources = None
    availableProfiles = None

    @staticmethod
    def getFirstSource():
        sources = SdrService.getActiveSources()
        if not sources:
            return None
        # TODO: configure default sdr in config? right now it will pick the first one off the list.
        return sources[list(sources.keys())[0]]

    @staticmethod
    def getSource(id):
        sources = SdrService.getActiveSources()
        if not sources:
            return None
        if id not in sources:
            return None
        return sources[id]

    @staticmethod
    def getAllSources():
        if SdrService.sources is None:
            SdrService.sources = MappedSdrSources(Config.get()["sdrs"])
        return SdrService.sources

    @staticmethod
    def getActiveSources():
        if SdrService.activeSources is None:
            SdrService.activeSources = ActiveSdrSources(SdrService.getAllSources())
        return SdrService.activeSources

    @staticmethod
    def getAvailableProfiles():
        if SdrService.availableProfiles is None:
            SdrService.availableProfiles = AvailableProfiles(SdrService.getActiveSources())
        return SdrService.availableProfiles

    @staticmethod
    def stopAllSources():
        for source in SdrService.getAllSources().values():
            source.stop()
