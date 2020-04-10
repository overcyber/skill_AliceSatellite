import sqlite3

from core.base.model.Widget import Widget
from core.base.model.widgetSizes import WidgetSizes
from core.commons import constants


class Satellites(Widget):
	SIZE = WidgetSizes.w_large_wide
	OPTIONS: dict = dict()


	def __init__(self, data: sqlite3.Row):
		super().__init__(data)


	def getSatellites(self) -> dict:
		return {device.id: device.toJson() for device in self.DeviceManager.getDevicesByType('AliceSatellite')}


	def toggleMute(self, uid: str):
		device = self.DeviceManager.getDeviceByUID(uid)
		print('here')
		if device:
			self.MqttManager.publish(
				topic=constants.TOPIC_TOGGLE_DND,
				payload={
					'uid': uid
				}
			)
