from abc import ABCMeta, abstractmethod
from datetime import datetime

from lbowrx_lb.form.input import Input

class ImageInput(Input, metaclass=ABCMeta):
    def render_input(self, value, errors):
        # TODO display errors
        return """
            <div class="imageupload" data-max-size="{maxsize}">
                <input type="hidden" id="{id}" name="{id}">
                <div class="image-container">
                    <img class="{classes}" src="{url}" alt="{label}"/>
                </div>
                <button type="button" class="btn btn-primary upload">Upload new image...</button>
                <button type="button" class="btn btn-secondary restore">Restore original image</button>
            </div>
        """.format(
            id=self.id,
            label=self.label,
            url=self.cachebuster(self.getUrl()),
            classes=" ".join(self.getImgClasses()),
            maxsize=self.getMaxSize(),
        )

    def cachebuster(self, url: str):
        return "{url}{separator}cb={cachebuster}".format(
            url=url,
            cachebuster=datetime.now().timestamp(),
            separator="&" if "?" in url else "?",
        )

    @abstractmethod
    def getUrl(self) -> str:
        pass

    @abstractmethod
    def getImgClasses(self) -> list:
        pass

    @abstractmethod
    def getMaxSize(self) -> int:
        pass


class AvatarInput(ImageInput):
    def getUrl(self) -> str:
        return "../static/gfx/openwebrx-avatar.png"

    def getImgClasses(self) -> list:
        return ["webrx-rx-avatar"]

    def getMaxSize(self) -> int:
        # 256 kB
        return 250 * 1024


class TopPhotoInput(ImageInput):
    def getUrl(self) -> str:
        return "../static/gfx/openwebrx-top-photo.jpg"

    def getImgClasses(self) -> list:
        return ["webrx-top-photo"]

    def getMaxSize(self) -> int:
        # 2 MB
        return 2 * 1024 * 1024
