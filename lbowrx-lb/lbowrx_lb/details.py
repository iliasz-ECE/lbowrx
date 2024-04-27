import logging

from lbowrx_lb.config.dynamic import DynamicConfig
from lbowrx_lb.locator import Locator

logger = logging.getLogger(__name__)

class ReceiverDetails():
    def __init__(self):
        self.receiver_details = DynamicConfig.get_receiver_details()
        try:
            self.receiver_details["locator"] = Locator.fromCoordinates(self.receiver_details["receiver_gps"])
        except ValueError as e:
            logger.error("invalid receiver location, check in settings: %s", str(e))
           
    def get(self):
        return self.receiver_details
