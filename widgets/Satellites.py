import sqlite3

from core.webui.model.Widget import Widget
from core.webui.model.WidgetSizes import WidgetSizes
from core.commons import constants


class Satellites(Widget):
	DEFAULT_SIZE = WidgetSizes.w_large_wide
	DEFAULT_OPTIONS: dict = dict()


	def __init__(self, data: sqlite3.Row):
		super().__init__(data)


	def getSatellites(self) -> dict:
		return {device.id: device.toJson() for device in self.DeviceManager.getDevicesByType(self.DeviceManager.SAT_TYPE)}


	def toggleMute(self, uid: str):
		device = self.DeviceManager.getDeviceByUID(uid)
		if device:
			self.MqttManager.publish(
				topic=constants.TOPIC_TOGGLE_DND,
				payload={
					'uid': uid
				}
			)
