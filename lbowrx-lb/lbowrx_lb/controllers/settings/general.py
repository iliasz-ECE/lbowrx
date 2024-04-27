import shutil
import os
import re
from glob import glob

from lbowrx_lb.controllers.admin import AuthorizationMixin
from lbowrx_lb.controllers.settings import SettingsFormController

from lbowrx_lb.config.dynamic import DynamicConfig
from lbowrx_lb.config.core import CoreConfig

from lbowrx_lb.form.section import Section
from lbowrx_lb.form.input import (
    TextInput,
    NumberInput,
    FloatInput,
    TextAreaInput,
    DropdownInput,
    Option
)
from lbowrx_lb.form.input.receiverid import ReceiverKeysConverter
from lbowrx_lb.form.input.gfx import AvatarInput, TopPhotoInput
from lbowrx_lb.form.input.location import LocationInput
from lbowrx_lb.form.input.converter import IntConverter

from lbowrx_lb.breadcrumb import Breadcrumb, BreadcrumbItem
from lbowrx_lb.controllers.settings import SettingsBreadcrumb

class GeneralSettingsController(SettingsFormController):
    def __init__(self, handler, request, options):
        super().__init__(handler, request, options)
        self.receiver_details = DynamicConfig.get_receiver_details()
    

    def getTitle(self):
        return "General Settings"

    def get_breadcrumb(self) -> Breadcrumb:
        return SettingsBreadcrumb().append(BreadcrumbItem("General Settings", "settings/general"))

    def getSections(self):
        return [
            Section(
                "Receiver information",
                TextInput("receiver_name", "Receiver name"),
                TextInput("receiver_location", "Receiver location"),
                NumberInput(
                    "receiver_asl",
                    "Receiver elevation",
                    append="meters above mean sea level",
                ),
                TextInput("receiver_admin", "Receiver admin"),
                LocationInput("receiver_gps", "Receiver coordinates"),
                TextInput("photo_title", "Photo title"),
                TextAreaInput("photo_desc", "Photo description", infotext="HTML supported "),
            ),
            Section(
                "Receiver images",
                AvatarInput(
                    "receiver_avatar",
                    "Receiver Avatar",
                    infotext="For performance reasons, images are cached. "
                    + "It can take a few hours until they appear on the site.",
                ),
                TopPhotoInput(
                    "receiver_top_photo",
                    "Receiver Panorama",
                    infotext="For performance reasons, images are cached. "
                    + "It can take a few hours until they appear on the site.",
                ),
            ),
            Section(
                "Receiver limits",
                NumberInput(
                    "max_clients",
                    "Maximum number of clients",
                ),
            ),
            Section(
                "Receiver listings",
                TextAreaInput(
                    "receiver_keys",
                    "Receiver keys",
                    converter=ReceiverKeysConverter(),
                    infotext="Put the keys you receive on listing sites (e.g. "
                    + '<a href="https://www.receiverbook.de" target="_blank">Receiverbook</a>) here, one per line',
                ),
            )
        ]

    def getData(self):
        return self.receiver_details

    def remove_existing_image(self, image_id):
        config = CoreConfig.get_shared_config()
        # remove all possible file extensions
        for ext in ["png", "jpg", "webp"]:
            try:
                os.unlink("{}/{}.{}".format(config.get_data_directory(), image_id, ext))
            except FileNotFoundError:
                pass

    def handle_image(self, data, image_id):
        if image_id in data:
            config = CoreConfig.get_shared_config()
            if data[image_id] == "restore":
                self.remove_existing_image(image_id)
            elif data[image_id]:
                if not data[image_id].startswith(image_id):
                    logger.warning("invalid file name: %s", data[image_id])
                else:
                    # get file extension (at least 3 characters)
                    # should be all lowercase since they are set by the upload script
                    pattern = re.compile(".*\\.([a-z]{3,})$")
                    matches = pattern.match(data[image_id])
                    if matches is None:
                        logger.warning("could not determine file extension for %s", image_id)
                    else:
                        self.remove_existing_image(image_id)
                        ext = matches.group(1)
                        data_file = "{}/{}.{}".format(config.get_data_directory(), image_id, ext)
                        temporary_file = "{}/{}".format(config.get_temporary_directory(), data[image_id])
                        shutil.copy(temporary_file, data_file)
            del data[image_id]
            # remove any accumulated temporary files on save
            for file in glob("{}/{}*".format(config.get_temporary_directory(), image_id)):
                os.unlink(file)

    def processData(self, data):
        # Image handling
        for img in ["receiver_avatar", "receiver_top_photo"]:
            self.handle_image(data, img)
        
        config = self.getData()
        
        for k, v in data.items():
            if v is None:
                if k in config_dict:
                    del config_dict[k]
            else:
                config[k] = v
                
    def store(self):
        DynamicConfig.modify_receiver_details(self.receiver_details)
