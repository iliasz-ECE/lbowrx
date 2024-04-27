from typing import List
from abc import ABC, abstractmethod


class BreadcrumbItem(object):
    def __init__(self, title, href):
        self.title = title
        self.href = href

    def render(self, documentRoot, active=False):
        return '<li class="breadcrumb-item {active}"><a href="{documentRoot}{href}">{title}</a></li>'.format(
            documentRoot=documentRoot, href=self.href, title=self.title, active="active" if active else ""
        )


class Breadcrumb(object):
    def __init__(self, breadcrumbs: List[BreadcrumbItem]):
        self.items = breadcrumbs

    def render(self, documentRoot):
        return """
            <ol class="breadcrumb">
                {crumbs}
                {last_crumb}
            </ol>
        """.format(
            crumbs="".join(item.render(documentRoot) for item in self.items[:-1]),
            last_crumb="".join(item.render(documentRoot, True) for item in self.items[-1:]),
        )

    def append(self, crumb: BreadcrumbItem):
        self.items.append(crumb)
        return self


class BreadcrumbMixin(ABC):
    def template_variables(self):
        variables = super().template_variables()
        variables["breadcrumb"] = self.get_breadcrumb().render(self.get_document_root())
        return variables

    @abstractmethod
    def get_breadcrumb(self) -> Breadcrumb:
        pass
