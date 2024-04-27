from urllib.parse import quote, unquote

from lbowrx_lb.controllers.admin import AuthorizationMixin
from lbowrx_lb.controllers.template import WebpageController
from lbowrx_lb.controllers.settings import SettingsBreadcrumb

from lbowrx_lb.distribution import Distribution
from lbowrx_lb.receivestate import ReceiveServersStateThread

from lbowrx_lb.breadcrumb import BreadcrumbMixin, Breadcrumb, BreadcrumbItem

class SdrsBreadcrumb(SettingsBreadcrumb):
    def __init__(self):
        super().__init__()        
        self.append(BreadcrumbItem("Sdrs settings", "settings/sdrs"))

class SdrsListController(AuthorizationMixin, BreadcrumbMixin, WebpageController):
    def template_variables(self):
        variables = super().template_variables()
        variables["content"] = self.render_sdrs()
        variables["title"] = "Sdrs settings"
        variables["modal"] = ""
        variables["error"] = ""
        return variables

    def get_breadcrumb(self):
        return SdrsBreadcrumb()

    def render_sdrs(self):
        ReceiveServersStateThread.wake_and_wait_until_thread_works()
        sdrs = Distribution.get_sdrs()
        
        def render_sdr(sdr_dict):
            additional_info = """
                <div>server: {server}</div>
                <div>Type: {type}</div>
                <div>Priority: {priority}</div>
                <div>Number of Profiles: {profiles_num}</div>
                <div>Available: {available}</div>
                <div>Connections: {connections}</div>
            """.format(server=sdr_dict["server"], type=sdr_dict["type"], priority=sdr_dict["priority"], profiles_num = sdr_dict["profiles_num"], available= sdr_dict["available"], connections= sdr_dict["connections"])

            return """
                <li class="list-group-item">
                    <div class="row">
                        <div class="col-6">
                                <h3>{sdr_name}</h3>
                            </a>
                        </div>
                        <div class="col-6">
                            {additional_info}
                        </div>
                    </div>
                </li>
            """.format(
                sdr_name= sdr_dict["name"],
                additional_info=additional_info,
            )

        return """
            <ul class="list-group list-group-flush server-list">
                {sdrs}
            </ul>
        """.format(
            sdrs="".join(render_sdr(value) for value in sdrs.values())
        )


    def indexAction(self):
        self.serve_template("settings/general.html", **self.template_variables())
