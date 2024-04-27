import logging

from lbowrx_lb.form.input import Input
from lbowrx_lb.form.input.validator import Validator
from lbowrx_lb.form.error import ValidationError

from lbowrx_lb.config.dynamic import DynamicConfig


logger = logging.getLogger(__name__)


class LocationValidator(Validator):
    def validate(self, key, value):
        if "lat" in value and not -90 < value["lat"] < 90:
            raise ValidationError(key, "Latitude out of range (-90 to 90)")
        if "lon" in value and not -180 < value["lon"] < 180:
            raise ValidationError(key, "Longitude out of range (-180 to 180)")
        pass


class LocationInput(Input):
    def __init__(self, id, label, validator: Validator = None):
        if validator is None:
            validator = LocationValidator()
        super().__init__(id, label, validator=validator)

    def render_input_group(self, value, errors):
        return """
            <div class="row {rowclass}">
                {inputs}
            </div>
            {errors}
        """.format(
            id=self.id,
            rowclass="is-invalid" if errors else "",
            inputs=self.render_input(value, errors),
            errors=self.render_errors(errors),
        )

    def render_input(self, value, errors):
        return "".join(self.render_sub_input(value, id, errors) for id in ["lat", "lon"])

    def render_sub_input(self, value, id, errors):
        return """
            <div class="col">
                <input type="number" class="{classes}" id="{id}" name="{id}" placeholder="{label}" value="{value}"
                step="any" {disabled}>
            </div>
        """.format(
            id="{0}-{1}".format(self.id, id),
            label=self.label,
            classes=self.input_classes(errors),
            value=value[id],
            disabled="disabled" if self.disabled else "",
        )

    def parse(self, data):
        value = {k: float(data["{0}-{1}".format(self.id, k)][0]) for k in ["lat", "lon"]}
        if self.validator is not None:
            self.validator.validate(self.id, value)
        return {self.id: value}
