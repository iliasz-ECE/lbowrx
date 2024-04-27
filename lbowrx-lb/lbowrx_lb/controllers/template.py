from string import Template
import pkg_resources

from lbowrx_lb.config.dynamic import DynamicConfig
from lbowrx_lb.controllers import Controller
from lbowrx_lb.details import ReceiverDetails


class TemplateController(Controller):
    def render_template(self, file, **vars):
        file_content = pkg_resources.resource_string("htdocs", file).decode("utf-8")
        template = Template(file_content)

        return template.safe_substitute(**vars)

    def serve_template(self, file, **vars):
        self.send_response(self.render_template(file, **vars), content_type="text/html")

    def default_variables(self):
        return {}


class WebpageController(TemplateController):
    def get_document_root(self):
        path_parts = [part for part in self.request.path[1:].split("/")]
        levels = max(0, len(path_parts) - 1)
        return "../" * levels

    def header_variables(self):
        variables = {"document_root": self.get_document_root()}
        variables.update(ReceiverDetails().get())
        return variables

    def template_variables(self):
        header = self.render_template("include/header.include.html", **self.header_variables())
        return {"header": header, "document_root": self.get_document_root()}


class IndexController(WebpageController):
    def indexAction(self):
        self.serve_template("index.html", **self.template_variables())
