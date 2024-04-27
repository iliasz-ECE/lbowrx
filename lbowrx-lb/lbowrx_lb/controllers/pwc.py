from urllib.parse import parse_qs

from lbowrx_lb.controllers.template import WebpageController
from lbowrx_lb.controllers.admin import AuthorizationMixin
from lbowrx_lb.users import UserList, DefaultPasswordClass



class PasswordChangeController(AuthorizationMixin, WebpageController):
    def isAuthorized(self):
        return self.user is not None and self.user.is_enabled() and self.user.must_change_password

    def indexAction(self):
        self.serve_template("pwchange.html", **self.template_variables())

    def processPwChange(self):
        data = parse_qs(self.get_body().decode("utf-8"))
        data = {k: v[0] for k, v in data.items()}
        userlist = UserList.getSharedInstance()
        if "password" in data and "confirm" in data and data["password"] == data["confirm"]:
            self.user.setPassword(DefaultPasswordClass(data["password"]), must_change_password=False)
            userlist.store()
            target = self.request.query["ref"][0] if "ref" in self.request.query else "/settings"
        else:
            target = "/pwchange"
        self.send_redirect(target)
