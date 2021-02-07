from core.base.SuperManager import SuperManager
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import MqttHandler


class AliceSatellite(AliceSkill):

	def __init__(self):
		self._sensorReadings = dict()
		super().__init__()


	def onBooted(self):
		confManager = SuperManager.getInstance().configManager
		if confManager.configAliceExists('onReboot') and confManager.getAliceConfigByName('onReboot') == 'greetAndRebootDevices':
			self.MqttManager.mqttBroadcast(
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
			self._sensorReadings[session.sessionId] = data


	@MqttHandler('projectalice/devices/disconnection')
	def deviceDisconnectIntent(self, session: DialogSession):
		uid = session.payload.get('uid')
		if uid:
			self.DeviceManager.deviceDisconnecting(uid)


	@MqttHandler('projectalice/devices/status')
	def deviceStatus(self, session: DialogSession):
		uid = session.payload.get('uid')
		device = self.DeviceManager.getDevice(uid=uid)
		refresh = False

		if device.skillName != self.name:
			return

		if 'dnd' in session.payload:
			device.updateParams('dnd', session.payload.get('dnd', None))
			refresh = True

		if refresh:
			self.publish('projectalice/devices/updated', payload={'id': device.id, 'type': 'status'})


	def getSensorReadings(self):
		self.publish('projectalice/devices/alice/getSensors')


	def temperatureAt(self, deviceUid: str) -> str:
		return self.getSensorValue(deviceUid, 'temperature')


	def getSensorValue(self, deviceUid: str, value: str) -> str:
		return self._sensorReadings.get(deviceUid, dict()).get(value, 'undefined')
