from core.base.SuperManager import SuperManager
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import MqttHandler
from core.commons import constants


class AliceSatellite(AliceSkill):

	def __init__(self):
		self._sensorReadings = dict()
		super().__init__()


	def onBooted(self):
		confManager = SuperManager.getInstance().configManager
		if confManager.configAliceExists('onReboot') and confManager.getAliceConfigByName('onReboot') == 'greetAndRebootDevices':
			self.DeviceManager.broadcastToDevices(
				topic='projectalice/devices/restart'
			)


	def onSleep(self):
		self.publish('projectalice/devices/sleep')


	def onWakeup(self):
		self.publish('projectalice/devices/wakeup')


	def onGoingBed(self):
		self.publish('projectalice/devices/goingBed')


	def onFullMinute(self):
		self.getSensorReadings()


	@MqttHandler('projectalice/devices/sensorsFeedback')
	def feedbackSensorIntent(self, session: DialogSession):
		data = session.payload.get('data')
		if data:
			self._sensorReadings[session.siteId] = data


	@MqttHandler('projectalice/devices/disconnection')
	def deviceDisconnectIntent(self, session: DialogSession):
		uid = session.payload.get('uid')
		if uid:
			self.DeviceManager.deviceDisconnecting(uid)


	def getSensorReadings(self):
		self.publish('projectalice/devices/alice/getSensors')


	def temperatureAt(self, siteId: str) -> str:
		return self.getSensorValue(siteId, 'temperature')


	def getSensorValue(self, siteId: str, value: str) -> str:
		return self._sensorReadings.get(siteId, dict()).get(value, 'undefined')
