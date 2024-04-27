from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import re
from abc import ABC, abstractmethod
import logging

from http.cookies import SimpleCookie

from lbowrx_lb.controllers.template import IndexController
from lbowrx_lb.controllers.assets import OwrxAssetsController, AprsSymbolsController, CompiledAssetsControllerLibs, CompiledAssetsControllerVars

from lbowrx_lb.controllers.settings import SettingsController
from lbowrx_lb.controllers.settings.general import GeneralSettingsController
from lbowrx_lb.controllers.settings.servers import ServersListController, NewServerController, ServerController
from lbowrx_lb.controllers.settings.profiles import ProfilesListController, NewProfileController, ProfileController
from lbowrx_lb.controllers.settings.sdrs import SdrsListController

from lbowrx_lb.controllers.imageupload import ImageUploadController
from lbowrx_lb.controllers.session import SessionController
from lbowrx_lb.controllers.pwc import PasswordChangeController


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Request(object):
    def __init__(self, url, method, headers):
        parsed_url = urlparse(url)
        self.path = parsed_url.path
        self.query = parse_qs(parsed_url.query)
        self.matches = None
        self.method = method
        self.headers = headers
        self.cookies = SimpleCookie()
        if "Cookie" in headers:
            self.cookies.load(headers["Cookie"])

    def setMatches(self, matches):
        self.matches = matches


class Route(ABC):
    def __init__(self, controller, method="GET", options=None):
        self.controller = controller
        self.controllerOptions = options if options is not None else {}
        self.method = method

    @abstractmethod
    def matches(self, request):
        pass


class StaticRoute(Route):
    def __init__(self, route, controller, method="GET", options=None):
        self.route = route
        super().__init__(controller, method, options)

    def matches(self, request):
        return request.path == self.route and self.method == request.method


class RegexRoute(Route):
    def __init__(self, regex, controller, method="GET", options=None):
        self.regex = re.compile(regex)
        super().__init__(controller, method, options)

    def matches(self, request):
        matches = self.regex.match(request.path)
        # this is probably not the cleanest way to do it...
        request.setMatches(matches)
        return matches is not None and self.method == request.method


class Router(object):
    def __init__(self):
        self.routes = [
            StaticRoute("/", IndexController),
            RegexRoute("^(/favicon.ico)$", OwrxAssetsController),
            RegexRoute("^/static/(.+)$", OwrxAssetsController),
            StaticRoute("/compiled/websocket-vars.js", CompiledAssetsControllerVars),
            RegexRoute("^/compiled/(.+)$", CompiledAssetsControllerLibs),
            StaticRoute("/settings", SettingsController),
            
            StaticRoute("/settings/general", GeneralSettingsController),
            StaticRoute("/settings/general", GeneralSettingsController, method="POST", options={"action": "processFormData"}),
            
            StaticRoute("/settings/servers", ServersListController),
            StaticRoute("/settings/newserver", NewServerController),
            StaticRoute("/settings/newserver", NewServerController, method="POST", options={"action": "processFormData"}),
            
            RegexRoute("^/settings/server/([^/]+)$", ServerController),
            RegexRoute("^/settings/server/([^/]+)$", ServerController, method="POST", options={"action": "processFormData"}),
            RegexRoute("^/settings/deleteserver/([^/]+)$", ServerController, options={"action": "deleteServer"}),
            
            StaticRoute("/settings/profiles", ProfilesListController),
            StaticRoute("/settings/newprofile", NewProfileController),
            StaticRoute("/settings/newprofile", NewProfileController, method="POST", options={"action": "processFormData"}),
            
            RegexRoute("^/settings/profile/([^/]+)$", ProfileController),
            RegexRoute("^/settings/profile/([^/]+)$", ProfileController, method="POST", options={"action": "processFormData"}),
            RegexRoute("^/settings/deleteprofile/([^/]+)$", ProfileController, options={"action": "deleteProfile"}),
            
            StaticRoute("/settings/sdrs", SdrsListController),
            
            StaticRoute("/imageupload", ImageUploadController),
            StaticRoute("/imageupload", ImageUploadController, method="POST", options={"action": "processImage"}),
            
            StaticRoute("/login", SessionController, options={"action": "loginAction"}),
            StaticRoute("/login", SessionController, method="POST", options={"action": "processLoginAction"}),
            StaticRoute("/pwchange", PasswordChangeController),
            StaticRoute("/pwchange", PasswordChangeController, method="POST", options={"action": "processPwChange"})
            
        ]

    def find_route(self, request):
        for r in self.routes:
            if r.matches(request):
                return r

    def route(self, handler, request):
        route = self.find_route(request)
        if route is not None:
            controller = route.controller
            controller(handler, request, route.controllerOptions).handle_request()
        else:
            handler.send_error(404, "Not Found", "The page you requested could not be found.")


class RequestHandler(BaseHTTPRequestHandler):
    timeout = 30
    router = Router()

    
    def log_message(self, format, *args):
        # fix default implementation
        pass
        
    def do_GET(self):
        self.router.route(self, self._build_request("GET"))

    def do_POST(self):
        self.router.route(self, self._build_request("POST"))

    def do_DELETE(self):
        self.router.route(self, self._build_request("DELETE"))

    def _build_request(self, method):
        return Request(self.path, method, self.headers)
