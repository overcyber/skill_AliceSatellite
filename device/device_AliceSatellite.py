from core.device.model.Device import Device
from core.device.model.DeviceType import DeviceType
import sqlite3
from core.base.model.ProjectAliceObject import ProjectAliceObject

class device_AliceSatellite(DeviceType):

	DEV_SETTINGS = ""
	LOC_SETTINGS = ""

	def __init__(self, data: sqlite3.Row):
		super().__init__(data, DEV_SETTINGS, LOC_SETTINGS)


	def getStatusTile(self):
		# Return the tile representing the current status of the device:
		# e.g. a light bulb can be on or off and display its status
		pass


	def getDeviceConfig(self):
		# return the custom configuration of that deviceType
		pass


	def findNewDevice(self, siteId: str):
		# look for new Devices
		pass
