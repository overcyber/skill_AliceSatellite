import sqlite3

from core.base.model.Widget import Widget
from core.base.model.widgetSizes import WidgetSizes


class Satellites(Widget):
	SIZE = WidgetSizes.w_large_wide
	OPTIONS: dict = dict()


	def __init__(self, data: sqlite3.Row):
		super().__init__(data)


	def getSatellites(self) -> dict:
		return {device.id: device.toJson() for device in self.DeviceManager.getDevicesByType('AliceSatellite')}
