from datetime import datetime, timezone
import mimetypes
import os
import pkg_resources
from abc import ABCMeta, abstractmethod
import gzip
from string import Template
import logging
logger = logging.getLogger(__name__)

from lbowrx_lb.controllers import Controller
from lbowrx_lb.config.core import CoreConfig
from lbowrx_lb.config.dynamic import DynamicConfig

from lbowrx_lb.distribution import Distribution
from lbowrx_lb.receivestate import ReceiveServersStateThread


class GzipMixin(object):
    def send_response(self, content, code=200, headers=None, content_type="text/html", *args, **kwargs):
        if self.zipable(content_type) and "accept-encoding" in self.request.headers:
            accepted = [s.strip().lower() for s in self.request.headers["accept-encoding"].split(",")]
            if "gzip" in accepted:
                if type(content) == str:
                    content = content.encode()
                content = self.gzip(content)
                if headers is None:
                    headers = {}
                headers["Content-Encoding"] = "gzip"
        super().send_response(content, code, headers=headers, content_type=content_type, *args, **kwargs)

    def zipable(self, content_type):
        types = ["text/javascript", "application/javascript", "text/css", "text/html", "image/svg+xml"]
        return content_type in types

    def gzip(self, content):
        return gzip.compress(content)


class ModificationAwareController(Controller, metaclass=ABCMeta):
    @abstractmethod
    def getModified(self, file):
        pass

    def wasModified(self, file):
        try:
            modified = self.getModified(file).replace(microsecond=0)

            if modified is not None and "If-Modified-Since" in self.handler.headers:
                client_modified = datetime.strptime(
                    self.handler.headers["If-Modified-Since"], "%a, %d %b %Y %H:%M:%S %Z"
                ).replace(tzinfo=timezone.utc)
                if modified <= client_modified:
                    return False
        except FileNotFoundError:
            pass

        return True


class AssetsController(GzipMixin, ModificationAwareController, metaclass=ABCMeta):
    def getModified(self, file):
        return datetime.fromtimestamp(os.path.getmtime(self.getFilePath(file)), timezone.utc)

    def openFile(self, file):
        return open(self.getFilePath(file), "rb")

    @abstractmethod
    def getFilePath(self, file):
        pass

    def serve_file(self, file, content_type=None):
        try:
            modified = self.getModified(file)

            if not self.wasModified(file):
                self.send_response("", code=304)
                return

            f = self.openFile(file)
            data = f.read()
            f.close()

            if content_type is None:
                (content_type, encoding) = mimetypes.guess_type(self.getFilePath(file))
            self.send_response(data, content_type=content_type, last_modified=modified, max_age=3600)
        except FileNotFoundError:
            self.send_response("file not found", code=404)

    def indexAction(self):
        filename = self.request.matches.group(1)
        self.serve_file(filename)


class OwrxAssetsController(AssetsController):
    def getFilePath(self, file):
        mappedFiles = {
            "gfx/openwebrx-avatar.png": "receiver_avatar",
            "gfx/openwebrx-top-photo.jpg": "receiver_top_photo",
        }
        if file in mappedFiles and ("mapped" not in self.request.query or self.request.query["mapped"][0] != "false"):
            config = CoreConfig.get_shared_config()
            for ext in ["png", "jpg", "webp"]:
                user_file = "{}/{}.{}".format(config.get_data_directory(), mappedFiles[file], ext)
                if os.path.exists(user_file) and os.path.isfile(user_file):
                    return user_file
        return pkg_resources.resource_filename("htdocs", file)


class AprsSymbolsController(AssetsController):
    def __init__(self, handler, request, options):
        path = CoreConfig.get_shared_config().get_aprs_symbols_path()
        if not path.endswith("/"):
            path += "/"
        self.path = path
        super().__init__(handler, request, options)

    def getFilePath(self, file):
        return self.path + file

class CompiledAssetsControllerLibs(GzipMixin, ModificationAwareController):
    profiles = {
        "receiver.js": [
            "lib/chroma.min.js",
            "openwebrx.js",
            "lib/jquery-3.2.1.min.js",
            "lib/jquery.nanoscroller.min.js",
            "lib/Header.js",
            "lib/Demodulator.js",
            "lib/DemodulatorPanel.js",
            "lib/BookmarkLocalStorage.js",
            "lib/BookmarkBar.js",
            "lib/BookmarkDialog.js",
            "lib/AudioEngine.js",
            "lib/ProgressBar.js",
            "lib/Measurement.js",
            "lib/FrequencyDisplay.js",
            "lib/MessagePanel.js",
            "lib/Js8Threads.js",
            "lib/Modes.js",
            "lib/MetaPanel.js",
        ],
        "settings.js": [
            "lib/jquery-3.2.1.min.js",
            "lib/bootstrap.bundle.min.js",
            "lib/location-picker.min.js",
            "lib/Header.js",
            "lib/settings/MapInput.js",
            "lib/settings/ImageUpload.js",
            "lib/BookmarkLocalStorage.js",
            "lib/settings/BookmarkTable.js",
            "lib/settings/WsjtDecodingDepthsInput.js",
            "lib/settings/WaterfallDropdown.js",
            "lib/settings/GainInput.js",
            "lib/settings/OptionalSection.js",
            "lib/settings/SchedulerInput.js",
            "lib/settings/ExponentialInput.js",
            "settings.js",
        ],
    }

    def indexAction(self):
        profileName = self.request.matches.group(1)
        if profileName not in self.profiles:
            self.send_response("profile not found", code=404)
            return

        files = self.profiles[profileName]
        files = [pkg_resources.resource_filename("htdocs", f) for f in files]

        modified = self.getModified(files)

        if not self.wasModified(files):
            self.send_response("", code=304)
            return

        contents = [self.getContents(f) for f in files]

        (content_type, encoding) = mimetypes.guess_type(profileName)
        self.send_response("\n".join(contents), content_type=content_type, last_modified=modified, max_age=3600)

    def getContents(self, file):
        with open(file) as f:
            return f.read()

    def getModified(self, files):
        modified = [os.path.getmtime(f) for f in files]
        return datetime.fromtimestamp(max(*modified), timezone.utc)

class CompiledAssetsControllerVars(GzipMixin, Controller):
    def indexAction(self):

        # Always update current state before deciding, so that newest data are available, especially at profile change.
        ReceiveServersStateThread.wake_and_wait_until_thread_works()
    
        profiles_id_list = DynamicConfig.get_profiles_id_list()

        selected_profile = None
        decision = None
        
        if self.request.query:
            if "profileid" in self.request.query:
                selected_profile = self.request.query["profileid"][0]
                
                if selected_profile not in profiles_id_list:
                    # default profile
                    selected_profile = DynamicConfig.get_profiles_id_list()[0]
        else:
            # default profile
            selected_profile = DynamicConfig.get_profiles_id_list()[0]


        all_sdrs = Distribution.get_sdrs()
        failed_sdrs_list = []
        
        if "failed_sdrs" in self.request.cookies:
            failed_sdrs_cookie = self.request.cookies["failed_sdrs"].value
            for sdr_id in failed_sdrs_cookie.split(','):
                if sdr_id in all_sdrs:
                     failed_sdrs_list.append(sdr_id)
        else:
            failed_sdrs_list = []

        decision = Distribution.decision_algorithm(selected_profile, failed_sdrs_list)

        if not decision:
            decision_vars = {"decision": "false","server": "null", "sdrid": "null", "profileid": "null",
                            "current_profile": "'"+selected_profile+"'", "profiles": DynamicConfig.get_profiles_id_name_list()}
        else:
            servers = DynamicConfig.get_servers()

            decided_server = decision[0]
            decided_ip = servers[decided_server].ip
            decided_port = servers[decided_server].port
            
            decided_sdr = decision[1]

            decided_profile = decision[2]
            
            decision_vars = {"decision": "true", "server": "'"+decided_ip+":"+str(decided_port)+"'", 
            "sdrid": "'"+decided_sdr+"'", "profileid": "'"+decided_profile+"'", "current_profile":                   
            "'"+selected_profile+"'", "profiles": DynamicConfig.get_profiles_id_name_list()}
        
        
        file_content = pkg_resources.resource_string("htdocs", "websocket-vars.js").decode("utf-8")
        template = Template(file_content)
        content = template.safe_substitute(**decision_vars)

        self.send_response(content, content_type="text/javascript", max_age=0)
