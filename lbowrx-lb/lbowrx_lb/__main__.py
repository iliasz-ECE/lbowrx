import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from http.server import HTTPServer
from socketserver import ThreadingMixIn
import signal
import argparse
import socket

from lbowrx_lb.httproutes import RequestHandler

from lbowrx_lb.config.core import CoreConfig
from lbowrx_lb.config.dynamic import DynamicConfig

from lbowrx_lb.receivestate import ReceiveServersStateThread
from lbowrx_lb.distribution import Distribution

from lbowrx_lb.admin import add_admin_parser, run_admin_action

class ThreadedHttpServer(ThreadingMixIn, HTTPServer):
    def __init__(self, web_port, RequestHandlerClass, use_ipv6):
        bind_address = "0.0.0.0"
        if use_ipv6:
            self.address_family = socket.AF_INET6
            bind_address = "::"
        super().__init__((bind_address, web_port), RequestHandlerClass)


class SignalException(Exception):
    pass


def handleSignal(sig, frame):
    raise SignalException("Received Signal {sig}".format(sig=sig))


def main():

    parser = argparse.ArgumentParser(description="OpenWebRX - Open Source SDR Web App for Everyone!")
    parser.add_argument("--debug", action="store_true", help="Set loglevel to DEBUG")
    
    moduleparser = parser.add_subparsers(title="Modules", dest="module")
    adminparser = moduleparser.add_parser("admin", help="Administration actions")
    add_admin_parser(adminparser)
    
    args = parser.parse_args()

    if args.debug:
       logger.setLevel(logging.DEBUG)

    if args.module == "admin":
        return run_admin_action(adminparser, args)

    CoreConfig()
    
    return start_receiver(loglevel=logging.DEBUG if args.debug else None)

def start_receiver(loglevel=None):
    print(
        """

Load Balancing OpenWebRX - Open Source SDR Web App for Everyone!  
for license see LICENSE file in the package
_________________________________________________________________________________________________

Load Balancing OpenWebRX Author:    Ilias Zervas
OpenWebRX Authors: Jakob Ketterl, András Retzler
Documentation:          https://github.com/jketterl/openwebrx/wiki
Support and info:       https://groups.io/g/openwebrx

        """,
        flush=True
    )

    
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, handleSignal)

    coreConfig = CoreConfig.get_shared_config()
    logger.debug("Port: " + str(coreConfig.get_web_port()))
    logger.debug(coreConfig.get_data_directory())
    
    dynamicConfig = DynamicConfig()
    
    receive_servers_state_thread = ReceiveServersStateThread(loglevel)
    receive_servers_state_thread.start()
    
    try:
        server = ThreadedHttpServer(coreConfig.get_web_port(), RequestHandler, coreConfig.get_web_ipv6())
        logger.info("Ready to serve requests.")
        server.serve_forever()
    except SignalException:
        pass


    receive_servers_state_thread.shutdown()

    return 0
    
    
import sys
if __name__ == "__main__":
    sys.exit(main())
