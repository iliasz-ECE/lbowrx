from owrx.source.soapy import SoapyConnectorSource, SoapyConnectorDeviceDescription


class PlutoSdrSource(SoapyConnectorSource):
    def getDriver(self):
        return "plutosdr"


class PlutoSdrDeviceDescription(SoapyConnectorDeviceDescription):
    def getName(self):
        return "PlutoSDR"
