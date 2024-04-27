from owrx.details import ReceiverDetails
from owrx.dsp import DspManager
from owrx.cpu import CpuUsageThread
from owrx.sdr import SdrService
from owrx.source import SdrSourceState, SdrClientClass, SdrSourceEventClient
from owrx.client import ClientRegistry, TooManyClientsException
from owrx.feature import FeatureDetector
from owrx.version import openwebrx_version
from owrx.bands import Bandplan
from owrx.bookmarks import Bookmarks
from owrx.property import PropertyStack, PropertyDeleted
from owrx.modes import Modes, DigitalMode
from owrx.config import Config
from owrx.waterfall import WaterfallOptions
from owrx.websocket import Handler
from queue import Queue, Full, Empty
from abc import ABCMeta, abstractmethod
import json
import threading
import struct

import logging

logger = logging.getLogger(__name__)

PoisonPill = object()


class Client(Handler, metaclass=ABCMeta):
    def __init__(self, conn):
        self.conn = conn
        self.multithreadingQueue = Queue(100)

        def mp_passthru():
            run = True
            while run:
                try:
                    data = self.multithreadingQueue.get()
                    if data is PoisonPill:
                        run = False
                    else:
                        self.send(data)
                    self.multithreadingQueue.task_done()
                except (EOFError, OSError, ValueError):
                    run = False
                except Exception:
                    logger.exception("Exception on client multithreading queue")

            self.multithreadingQueue = None

        threading.Thread(target=mp_passthru, name="connection_mp_passthru").start()

    def send(self, data):
        try:
            self.conn.send(data)
        except IOError:
            logger.exception("error in Client::send()")
            self.close(error=True)

    def close(self, error: bool = False):
        if self.multithreadingQueue is not None:
            while True:
                try:
                    self.multithreadingQueue.get(block=False)
                except Empty:
                    break
            try:
                self.multithreadingQueue.put(PoisonPill, block=False)
            except Full:
                logger.exception("impossible queue state: Full after Empty")
        self.conn.close(socketError=error)

    def mp_send(self, data):
        if self.multithreadingQueue is None:
            return
        try:
            self.multithreadingQueue.put(data, block=False)
        except Full:
            self.close(error=True)

    @abstractmethod
    def handleTextMessage(self, conn, message):
        pass

    def handleBinaryMessage(self, conn, data):
        logger.error("unsupported binary message, discarding")

    def handleClose(self):
        self.close()


class OpenWebRxClient(Client, metaclass=ABCMeta):
    def __init__(self, conn):
        super().__init__(conn)
    
    def close(self, error: bool = False):
        super().close(error)


class OpenWebRxReceiverClient(OpenWebRxClient, SdrSourceEventClient):
    sdr_config_keys = [
        "waterfall_levels",
        "samp_rate",
        "start_mod",
        "start_freq",
        "center_freq",
        "initial_squelch_level",
        "sdr_id",
        "profile_id",
        "squelch_auto_margin",
    ]

    global_config_keys = [
        "waterfall_scheme",
        "waterfall_colors",
        "waterfall_auto_levels",
        "waterfall_auto_min_range",
        "fft_size",
        "audio_compression",
        "fft_compression",
        "max_clients",
        "tuning_precision",
    ]

    def __init__(self, conn):
        super().__init__(conn)

        self.dsp = None
        self.dspLock = threading.Lock()
        self.sdr = None
        self.configSubs = []
        self.bookmarkSub = None
        self.connectionProperties = {}

        try:
            ClientRegistry.getSharedInstance().addClient(self)
        except TooManyClientsException:
            self.write_backoff_message("Too many clients")
            self.close()
            raise

        self.setupGlobalConfig()
        self.stack = self.setupStack()

        features = FeatureDetector().feature_availability()
        self.write_features(features)

        modes = Modes.getModes()
        self.write_modes(modes)
        
        CpuUsageThread.getSharedInstance().add_client(self)

    def setupStack(self):
        stack = PropertyStack()
        stack.addLayer(1, Config.get())
        configProps = stack.filter(*OpenWebRxReceiverClient.sdr_config_keys)

        def sendConfig(changes=None):
            if changes is None:
                config = configProps.__dict__()
            else:
                config = {k: v if v is not PropertyDeleted else None for k, v in changes.items()}
            if (
                (changes is None or "start_freq" in changes or "center_freq" in changes)
                and "start_freq" in configProps
                and "center_freq" in configProps
            ):
                config["start_offset_freq"] = configProps["start_freq"] - configProps["center_freq"]
            if (changes is None or "profile_id" in changes) and self.sdr is not None:
                config["sdr_id"] = self.sdr.getId()
            self.write_config(config)

        def sendBookmarks(*args):
            cf = configProps["center_freq"]
            srh = configProps["samp_rate"] / 2
            dial_frequencies = []
            bookmarks = []
            if "center_freq" in configProps and "samp_rate" in configProps:
                frequencyRange = (cf - srh, cf + srh)
                dial_frequencies = Bandplan.getSharedInstance().collectDialFrequencies(frequencyRange)
                bookmarks = [b.__dict__() for b in Bookmarks.getSharedInstance().getBookmarks(frequencyRange)]
            self.write_dial_frequencies(dial_frequencies)
            self.write_bookmarks(bookmarks)

        def updateBookmarkSubscription(*args):
            if self.bookmarkSub is not None:
                self.bookmarkSub.cancel()
            if "center_freq" in configProps and "samp_rate" in configProps:
                cf = configProps["center_freq"]
                srh = configProps["samp_rate"] / 2
                frequencyRange = (cf - srh, cf + srh)
                self.bookmarkSub = Bookmarks.getSharedInstance().subscribe(frequencyRange, sendBookmarks)
                sendBookmarks()

        self.configSubs.append(configProps.wire(sendConfig))
        self.configSubs.append(stack.filter("center_freq", "samp_rate").wire(updateBookmarkSubscription))

        sendConfig()
        return stack

    def setupGlobalConfig(self):
        def writeConfig(changes):
            if "waterfall_scheme" in changes or "waterfall_colors" in changes:
                scheme = WaterfallOptions(globalConfig["waterfall_scheme"]).instantiate()
                changes["waterfall_colors"] = scheme.getColors()
            self.write_config(changes)

        globalConfig = Config.get().filter(*OpenWebRxReceiverClient.global_config_keys)
        self.configSubs.append(globalConfig.wire(writeConfig))
        writeConfig(globalConfig.__dict__())

    def onStateChange(self, state: SdrSourceState):
        if state is SdrSourceState.RUNNING:
            self.handleSdrAvailable()

    def onFail(self):
        logger.warning('SDR device "%s" has failed, selecting new device', self.sdr.getName())
        self.write_log_message('SDR device "{0}" has failed, selecting new device'.format(self.sdr.getName()))
        self.setSdr()

    def onDisable(self):
        logger.warning('SDR device "%s" was disabled, selecting new device', self.sdr.getName())
        self.write_log_message('SDR device "{0}" was disabled, selecting new device'.format(self.sdr.getName()))
        self.setSdr()

    def onShutdown(self):
        logger.warning('SDR device "%s" is shutting down, selecting new device', self.sdr.getName())
        self.write_log_message('SDR device "{0}" is shutting down, selecting new device'.format(self.sdr.getName()))
        self.setSdr()

    def getClientClass(self) -> SdrClientClass:
        return SdrClientClass.USER


    def handleTextMessage(self, conn, message):
        try:
            message = json.loads(message)
            if "type" in message:
                if message["type"] == "dspcontrol":
                    dsp = self.getDsp()
                    if dsp is None:
                        logger.warning("DSP not available; discarding client dspcontrol message")
                    else:
                        if "action" in message and message["action"] == "start":
                            dsp.start()

                        if "params" in message:
                            params = message["params"]
                            dsp.setProperties(params)

                elif message["type"] == "setsdr":
                    if "params" in message:
                        self.setSdr(message["params"]["sdr"])
                elif message["type"] == "selectprofile":
                    if "params" in message and "profile" in message["params"]:
                        profile = message["params"]["profile"].split("|")
                        self.setSdr(profile[0])
                        self.sdr.activateProfile(profile[1])
                elif message["type"] == "connectionproperties":
                    if "params" in message:
                        self.connectionProperties = message["params"]
                        if self.dsp:
                            self.getDsp().setProperties(self.connectionProperties)

                elif message["type"] == "sdrselection":
                    if "params" in message:
                        if "sdrid" in message["params"]:
                            if "profileid" in message["params"]:
                                self.setSdr(message["params"]["sdrid"])
                                self.sdr.activateProfile(message["params"]["profileid"])
                                self.sdr.addClient(self)
            else:
                logger.warning("received message without type: {0}".format(message))

        except json.JSONDecodeError:
            logger.warning("message is not json: {0}".format(message))

    def setSdr(self, id=None):
        next = None
        if id is not None:
            next = SdrService.getSource(id)
        
        if next == self.sdr and next is not None:
            return

        self.stopDsp()
        self.stack.removeLayerByPriority(0)

        if self.sdr is not None:
            self.sdr.removeClient(self)

        self.sdr = next

        if next is None:
            logger.warning("the requested SDR device is not available")
            self.handleSdrNotAvailable()
            return

    def handleSdrAvailable(self):
        self.getDsp().setProperties(self.connectionProperties)
        self.stack.replaceLayer(0, self.sdr.getProps())

        self.sdr.addSpectrumClient(self)

    def handleSdrNotAvailable(self):
        self.write_sdr_error("The requested SDR device is not available")

    def close(self, error: bool = False):
        if self.sdr is not None:
            self.sdr.removeClient(self)
        self.stopDsp()
        CpuUsageThread.getSharedInstance().remove_client(self)
        ClientRegistry.getSharedInstance().removeClient(self)
        while self.configSubs:
            self.configSubs.pop().cancel()
        if self.bookmarkSub is not None:
            self.bookmarkSub.cancel()
            self.bookmarkSub = None
        super().close(error)

    def stopDsp(self):
        with self.dspLock:
            if self.dsp is not None:
                self.dsp.stop()
                self.dsp = None
        if self.sdr is not None:
            self.sdr.removeSpectrumClient(self)

    def getDsp(self):
        with self.dspLock:
            if self.dsp is None and self.sdr is not None:
                self.dsp = DspManager(self, self.sdr)
        return self.dsp

    def write_spectrum_data(self, data):
        self.mp_send(bytes([0x01]) + data)

    def write_dsp_data(self, data):
        self.send(bytes([0x02]) + data)

    def write_hd_audio(self, data):
        self.send(bytes([0x04]) + data)

    def write_s_meter_level(self, level):
        level, = struct.unpack('f', level[-4:])
        try:
            self.send({"type": "smeter", "value": level})
        except ValueError:
            logger.warning("unable to send smeter value: %s", str(level))

    def write_cpu_usage(self, usage):
        self.mp_send({"type": "cpuusage", "value": usage})

    def write_clients(self, clients):
        self.mp_send({"type": "clients", "value": clients})

    def write_secondary_fft(self, data):
        self.send(bytes([0x03]) + data)

    def write_secondary_demod(self, message):
        self.send({"type": "secondary_demod", "value": message})

    def write_secondary_dsp_config(self, cfg):
        self.send({"type": "secondary_config", "value": cfg})

    def write_config(self, cfg):
        self.send({"type": "config", "value": cfg})
    
    def write_features(self, features):
        self.send({"type": "features", "value": features})

    def write_metadata(self, metadata):
        self.send({"type": "metadata", "value": metadata})

    def write_dial_frequencies(self, frequencies):
        self.send({"type": "dial_frequencies", "value": frequencies})

    def write_bookmarks(self, bookmarks):
        self.send({"type": "bookmarks", "value": bookmarks})

    def write_log_message(self, message):
        self.send({"type": "log_message", "value": message})

    def write_sdr_error(self, message):
        self.send({"type": "sdr_error", "value": message})

    def write_demodulator_error(self, message):
        self.send({"type": "demodulator_error", "value": message})

    def write_backoff_message(self, reason):
        self.send({"type": "backoff", "reason": reason})

    def write_modes(self, modes):
        def to_json(m):
            res = {
                "modulation": m.modulation,
                "name": m.name,
                "type": "digimode" if isinstance(m, DigitalMode) else "analog",
                "requirements": m.requirements,
                "squelch": m.squelch,
            }
            if m.bandpass is not None:
                res["bandpass"] = {"low_cut": m.bandpass.low_cut, "high_cut": m.bandpass.high_cut}
            if isinstance(m, DigitalMode):
                res["underlying"] = m.underlying
            return res

        self.send({"type": "modes", "value": [to_json(m) for m in modes]})


class HandshakeMessageHandler(Handler):
    """
    This handler receives text messages, but will only respond to the second handshake string.
    As soon as a valid handshake is received, the handler replaces itself with the corresponding handler type.
    """
    def handleTextMessage(self, conn, message):
        if message[:16] == "SERVER DE CLIENT":
            meta = message[17:].split(" ")
            handshake = {v[0]: "=".join(v[1:]) for v in map(lambda x: x.split("="), meta)}

            logger.debug("client connection initialized")

            client = None
            if "type" in handshake:
                if handshake["type"] == "receiver":
                    client = OpenWebRxReceiverClient
                else:
                    logger.warning("invalid connection type: %s", handshake["type"])

            if client is not None:
                logger.debug("handshake complete, handing off to %s", client.__name__)
                
                conn.send("CLIENT DE SERVER server=openwebrx version={version}".format(version=openwebrx_version))
                conn.setMessageHandler(client(conn))
            else:
                logger.warning('invalid handshake received')
        else:
            logger.warning("not answering client request since handshake is not complete")

    def handleBinaryMessage(self, conn, data):
        pass

    def handleClose(self):
        pass
