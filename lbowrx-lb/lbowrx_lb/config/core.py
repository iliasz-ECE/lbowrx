from configparser import ConfigParser
from pathlib import Path
import os

from lbowrx_lb.config.error import ConfigError


class CoreConfig(object):
    defaultSearchLocations = ["./lbowrx-lb.conf"]

    defaults = {
        "core": {
            "data_directory": "/var/lib/lbowrx/lb",
            "temporary_directory": "/tmp",
            "log_level": "INFO",
        },
        "web": {
            "port": 8080,
            "ipv6": True,
        }
    }

    sharedConfig = None
        
    def __init__(self,file: Path = None):
        def expand_base(base: Path):
            # check if config exists
            if not base.exists() or not base.is_file():
                return []
            # every location can additionally have a directory containing config overrides
            # this directory must have the same name, with the ".d" suffix
            override_dir = Path(str(base) + ".d")
            # check if override dir exists
            if not override_dir.exists() or not override_dir.is_dir():
                return [base]
            # load all .conf files from the override dir
            overrides = override_dir.glob("*.conf")
            return [base] + [o for o in overrides if o.is_file()]

        if file is None:
            bases = [Path(b) for b in CoreConfig.defaultSearchLocations]
        else:
            bases = [file]
        configFiles = [o for b in bases for o in expand_base(b)]

        config = ConfigParser()
        # set up config defaults
        config.read_dict(CoreConfig.defaults)
        # read the allocated files
        config.read(configFiles)

        self.data_directory = config.get("core", "data_directory")
        CoreConfig.checkDirectory(self.data_directory, "data_directory")
        self.temporary_directory = config.get("core", "temporary_directory")
        CoreConfig.checkDirectory(self.temporary_directory, "temporary_directory")
        self.log_level = config.get("core", "log_level")
        self.web_port = config.getint("web", "port")
        self.web_ipv6 = config.getboolean("web", "ipv6")

        CoreConfig.sharedConfig = self

    @classmethod
    def get_shared_config(cls):
        # not sure when (if ever) the if is followed since main will create one at start.
        if cls.sharedConfig is None:
            cls.sharedConfig = cls()
        return cls.sharedConfig

    @staticmethod
    def checkDirectory(dir, key):
        if not os.path.exists(dir):
            raise ConfigError(key, "{dir} doesn't exist".format(dir=dir))
        if not os.path.isdir(dir):
            raise ConfigError(key, "{dir} is not a directory".format(dir=dir))
        if not os.access(dir, os.W_OK):
            raise ConfigError(key, "{dir} is not writable".format(dir=dir))

    def get_web_port(self) -> int:
        return self.web_port

    def get_web_ipv6(self) -> bool:
        return self.web_ipv6

    def get_data_directory(self) -> str:
        return self.data_directory

    def get_temporary_directory(self) -> str:
        return self.temporary_directory

    def get_log_level(self) -> str:
        return self.log_level
