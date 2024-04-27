from urllib.parse import quote, unquote
from uuid import uuid4

from lbowrx_lb.controllers.admin import AuthorizationMixin
from lbowrx_lb.controllers.template import WebpageController
from lbowrx_lb.controllers.settings import SettingsFormController,SettingsBreadcrumb

from lbowrx_lb.config.dynamic import DynamicConfig, ServerInfo
from lbowrx_lb.distribution import Distribution
from lbowrx_lb.receivestate import ReceiveServersStateThread

from lbowrx_lb.breadcrumb import BreadcrumbMixin, Breadcrumb, BreadcrumbItem

from lbowrx_lb.form.section import Section
from lbowrx_lb.form.input import TextInput, NumberInput
from lbowrx_lb.form.input.validator import RequiredValidator, RangeValidator

class ServersBreadcrumb(SettingsBreadcrumb):
    def __init__(self):
        super().__init__()        
        self.append(BreadcrumbItem("Servers settings", "settings/servers"))

class ServersListController(AuthorizationMixin, BreadcrumbMixin, WebpageController):
    def template_variables(self):
        variables = super().template_variables()
        variables["content"] = self.render_servers()
        variables["title"] = "Servers settings"
        variables["modal"] = ""
        variables["error"] = ""
        return variables

    def get_breadcrumb(self):
        return ServersBreadcrumb()

    def render_servers(self):
        ReceiveServersStateThread.wake_and_wait_until_thread_works()
        servers = Distribution.get_servers()
    
        def render_server(server_id, server_dict):
            additional_info = """
                <div>IP: {ip}</div>
                <div>Port: {port}</div>
                <div>Priority: {priority}</div>
                <div>Responding: {responding}</div>
            """.format(ip=server_dict["ip"], port=server_dict["port"], priority=server_dict["priority"], responding= server_dict["responding"])

            if server_dict["responding"]:
                additional_info += """
                <div>Cpu: {cpu}</div>
                <div>Active sdrs: {active_sdrs}</div>
                <div>Total Connections: {connections}</div>
            """.format(cpu=server_dict["cpu"], active_sdrs = server_dict["active_sdrs"], connections = server_dict["connections"])
            
            return """
                <li class="list-group-item">
                    <div class="row">
                        <div class="col-6">
                            <a href="{server_link}">
                                <h3>{server_name}</h3>
                            </a>
                        </div>
                        <div class="col-6">
                            {additional_info}
                        </div>
                    </div>
                </li>
            """.format(
                server_link="{}settings/server/{}".format(self.get_document_root(), quote(server_id)),
                server_name= server_dict["name"],
                additional_info=additional_info,
            )

        return """
            <ul class="list-group list-group-flush server-list">
                {servers}
            </ul>
            <div class="buttons container">
                <a class="btn btn-success" href="newserver">Add new server...</a>
            </div>
        """.format(
            servers="".join(render_server(key, value) for key, value in servers.items())
        )


    def indexAction(self):
        self.serve_template("settings/general.html", **self.template_variables())
        
class NewServerController(SettingsFormController):
    def __init__(self, handler, request, options):
        super().__init__(handler, request, options)
        self.server_info = ServerInfo(None,None,None,100)
        self.server_id = str(uuid4())

    def get_breadcrumb(self) -> Breadcrumb:
        return ServersBreadcrumb().append(BreadcrumbItem("New Server", "settings/server/newserver"))

    def getSections(self):
        return [
            Section(
                "New server settings",
                TextInput("name", "Server name", validator=RequiredValidator()),
                TextInput("ip", "Server IP", validator=RequiredValidator()),
                NumberInput("port", "Server Port", validator=RequiredValidator()),
                NumberInput("priority", "Server Priority", validator=RangeValidator(0,1000), infotext="Note: Optional server priority for load balancing. <br /> " + "Note: default is 100, range: 0-1000, 0 means disabled."),
            )
        ]

    def getTitle(self):
        return "New server"

    def getData(self):
        return self.server_info.__dict__
    
    def getDataObject(self):
        return self.server_info

    def store(self):
        DynamicConfig.add_server(self.server_id, self.server_info)
        Distribution.add_server(self.server_id)
        ReceiveServersStateThread.wake_and_wait_until_thread_works()
    
    def getSuccessfulRedirect(self):
        return "{}settings/server/{}".format(self.get_document_root(), quote(self.server_id))
  

class ServerController(SettingsFormController):
    def __init__(self, handler, request, options):
        super().__init__(handler, request, options)
        self.server_id = unquote(self.request.matches.group(1))
        self.server_info = DynamicConfig.get_servers_object().get_server_info(self.server_id)
        
    def getTitle(self):
        return self.server_info.name


    def get_breadcrumb(self) -> Breadcrumb:
        return ServersBreadcrumb().append(
            BreadcrumbItem(self.server_info.name, "settings/server/{}".format(self.server_id))
        )

    def getData(self):
        return self.server_info.__dict__
        
    def getDataObject(self):
        return self.server_info

    def getSections(self):
        return [
            Section(
                "Server settings",
                TextInput("name", "Server name", validator=RequiredValidator()),
                TextInput("ip", "Server IP", validator=RequiredValidator()),
                NumberInput("port", "Server Port", validator=RequiredValidator()),
                NumberInput("priority", "Server Priority", validator=RangeValidator(0,1000), infotext="Note: Optional server priority for load balancing. <br /> " + "Note: default is 100, range: 0-1000, 0 means disabled."),
            )
        ]

    def render_remove_button(self):
        return """
            <button type="button" class="btn btn-danger" data-toggle="modal" data-target="#deleteModal">Remove server...</button>
        """

    def render_buttons(self):
        return self.render_remove_button() + super().render_buttons()


    def buildModal(self):
        return """
            <div class="modal" id="deleteModal" tabindex="-1" role="dialog">
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5>Please confirm</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <p>Do you really want to delete this {object_type}?</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                            <a type="button" class="btn btn-danger" href="{confirm_url}">Delete</a>
                        </div>
                    </div>
                </div>
            </div>
        """.format(
            object_type=self.getModalObjectType(),
            confirm_url=self.getModalConfirmUrl(),
        )

    def processFormData(self):
        if self.server_info is None:
            self.send_response("server not found", code=404)
            return
        return super().processFormData()

    def store(self):
        DynamicConfig.modify_server(self.server_id, self.server_info)
        Distribution.modify_server(self.server_id)
        ReceiveServersStateThread.wake_and_wait_until_thread_works()

    def indexAction(self):
        if self.server_id is None:
            self.send_response("server not found", code=404)
            return
        super().indexAction()

    def getModalObjectType(self):
        return "Server"

    def getModalConfirmUrl(self):
        return "{}settings/deleteserver/{}".format(self.get_document_root(), quote(self.server_id))

    def deleteServer(self):
        if self.server_info is None:
            return self.send_response("server not found", code=404)
        DynamicConfig.delete_server(self.server_id)
        Distribution.delete_server(self.server_id)
        return self.send_redirect("{}settings/servers".format(self.get_document_root()))
