import sqlite3
from core.commons import constants
from core.webui.model.Widget import Widget
from core.webui.model.WidgetSizes import WidgetSizes


class Satellites(Widget):
	DEFAULT_SIZE = WidgetSizes.w_large_wide
	DEFAULT_OPTIONS: dict = dict()


	def __init__(self, data: sqlite3.Row):
		super().__init__(data)


	def getSatellites(self) -> dict:
		return {device.id: device.toDict() for device in self.DeviceManager.getDevicesBySkill(skillName=self.skillInstance.name)}


	def toggleMute(self, uid: str):
		device = self.DeviceManager.getDevice(uid=uid)
		if device:
			self.MqttManager.publish(
				topic=constants.TOPIC_TOGGLE_DND,
				payload={
					'uid': uid
				}
			)
