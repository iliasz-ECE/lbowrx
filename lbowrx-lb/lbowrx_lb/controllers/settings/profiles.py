from urllib.parse import quote, unquote, parse_qs
from uuid import uuid4

from lbowrx_lb.controllers.admin import AuthorizationMixin
from lbowrx_lb.controllers.template import WebpageController
from lbowrx_lb.controllers.settings import SettingsFormController,SettingsBreadcrumb

from lbowrx_lb.config.dynamic import DynamicConfig, ProfileInfo

from lbowrx_lb.breadcrumb import BreadcrumbMixin, Breadcrumb, BreadcrumbItem

from lbowrx_lb.form.section import Section
from lbowrx_lb.form.error import FormError
from lbowrx_lb.form.input import TextInput, ExponentialInput
from lbowrx_lb.form.input.validator import RequiredValidator

class ProfilesBreadcrumb(SettingsBreadcrumb):
    def __init__(self):
        super().__init__()        
        self.append(BreadcrumbItem("Profiles settings", "settings/profiles"))

class ProfilesListController(AuthorizationMixin, BreadcrumbMixin, WebpageController):
    def template_variables(self):
        variables = super().template_variables()
        variables["content"] = self.render_profiles()
        variables["title"] = "Profiles settings"
        variables["modal"] = ""
        variables["error"] = ""
        return variables

    def get_breadcrumb(self):
        return ProfilesBreadcrumb()

    def render_profiles(self):
        profiles = DynamicConfig.get_profiles()
    
        def render_profile(profile_id, profile_info):
            additional_info = """
                <div>Start Frequency: {start_freq}</div>
                <div>End Frequency  : {end_freq}</div>
            """.format(start_freq=profile_info.start_freq, end_freq=profile_info.end_freq)

            return """
                <li class="list-group-item">
                    <div class="row">
                        <div class="col-6">
                            <a href="{profile_link}">
                                <h3>{profile_name}</h3>
                            </a>
                        </div>
                        <div class="col-6">
                            {additional_info}
                        </div>
                    </div>
                </li>
            """.format(
                profile_link="{}settings/profile/{}".format(self.get_document_root(), quote(profile_id)),
                profile_name= profile_info.name,
                additional_info=additional_info,
            )

        return """
            <ul class="list-group list-group-flush profile-list">
                {profiles}
            </ul>
            <div class="buttons container">
                <a class="btn btn-success" href="newprofile">Add new profile...</a>
            </div>
        """.format(
            profiles="".join(render_profile(key, value) for key, value in profiles.items())
        )


    def indexAction(self):
        self.serve_template("settings/general.html", **self.template_variables())
        
class NewProfileController(SettingsFormController):
    def __init__(self, handler, request, options):
        super().__init__(handler, request, options)
        self.profile_info = ProfileInfo(None,None,None)
        self.profile_id = str(uuid4())

    def get_breadcrumb(self) -> Breadcrumb:
        return ProfilesBreadcrumb().append(BreadcrumbItem("New Profile", "settings/profile/newprofile"))

    def getSections(self):
        return [
            Section(
                "New profile settings",
                TextInput("name", "Profile name", validator=RequiredValidator()),
                ExponentialInput("start_freq", "Start frequency", "Hz"),
                ExponentialInput("end_freq", "End frequency", "Hz")
            )
        ]

    def getTitle(self):
        return "New profile"

    def getData(self):
        return self.profile_info.__dict__
    
    def getDataObject(self):
        return self.profile_info

    def parseFormData(self):
        data = parse_qs(self.get_body().decode("utf-8"), keep_blank_values=True)
        result = {}
        errors = []
        for section in self.getSections():
            section_data, section_errors = section.parse(data)
            if section_data["start_freq"] >= section_data["end_freq"]:
                e1 = FormError("start_freq","start freq must be less than end_freq")
                errors.append(e1)
                e2 = FormError("end_freq","start freq must be less than end_freq")
                errors.append(e2)
            result.update(section_data)
            errors += section_errors
        return result, errors

    def store(self):
        DynamicConfig.add_profile(self.profile_id, self.profile_info)
    
    def getSuccessfulRedirect(self):
        return "{}settings/profile/{}".format(self.get_document_root(), quote(self.profile_id))
  

class ProfileController(SettingsFormController):
    def __init__(self, handler, request, options):
        super().__init__(handler, request, options)
        self.profile_id = unquote(self.request.matches.group(1))
        self.profile_info = DynamicConfig.get_profiles_object().get_profile_info(self.profile_id)
        
    def getTitle(self):
        return self.profile_info.name


    def get_breadcrumb(self) -> Breadcrumb:
        return ProfilesBreadcrumb().append(
            BreadcrumbItem(self.profile_info.name, "settings/profile/{}".format(self.profile_id))
        )

    def getData(self):
        return self.profile_info.__dict__
        
    def getDataObject(self):
        return self.profile_info

    def getSections(self):
        return [
            Section(
                "Profile settings",
                TextInput("name", "Profile name", validator=RequiredValidator()),
                ExponentialInput("start_freq", "Start frequency", "Hz"),
                ExponentialInput("end_freq", "End frequency", "Hz")            )
        ]

    def render_remove_button(self):
        return """
            <button type="button" class="btn btn-danger" data-toggle="modal" data-target="#deleteModal">Remove profile...</button>
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

    def parseFormData(self):
        data = parse_qs(self.get_body().decode("utf-8"), keep_blank_values=True)
        result = {}
        errors = []
        for section in self.getSections():
            section_data, section_errors = section.parse(data)
            if section_data["start_freq"] >= section_data["end_freq"]:
                e1 = FormError("start_freq","start freq must be less than end_freq")
                errors.append(e1)
                e2 = FormError("end_freq","start freq must be less than end_freq")
                errors.append(e2)
            result.update(section_data)
            errors += section_errors
        return result, errors

    def processFormData(self):
        if self.profile_info is None:
            self.send_response("profile not found", code=404)
            return
        return super().processFormData()

    def store(self):
        DynamicConfig.modify_profile(self.profile_id, self.profile_info)

    def indexAction(self):
        if self.profile_id is None:
            self.send_response("profile not found", code=404)
            return
        super().indexAction()

    def getModalObjectType(self):
        return "Profile"

    def getModalConfirmUrl(self):
        return "{}settings/deleteprofile/{}".format(self.get_document_root(), quote(self.profile_id))

    def deleteProfile(self):
        if self.profile_info is None:
            return self.send_response("profile not found", code=404)
        DynamicConfig.delete_profile(self.profile_id)
        return self.send_redirect("{}settings/profiles".format(self.get_document_root()))
