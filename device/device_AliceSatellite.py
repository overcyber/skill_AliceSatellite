from core.device.model.Device import Device
from core.device.model.Location import Location
from core.device.model.DeviceType import DeviceType
from core.commons import constants
import sqlite3
import threading
import socket
from core.base.model.ProjectAliceObject import ProjectAliceObject

class device_AliceSatellite(DeviceType):

	DEV_SETTINGS = ""
	LOC_SETTINGS = ""

	def __init__(self, data: sqlite3.Row):
		super().__init__(data, self.DEV_SETTINGS, self.LOC_SETTINGS)
		self._broadcastFlag = threading.Event()

		self._listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._listenSocket.settimeout(2)

		self._broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self._broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self._broadcastPort = int(self.ConfigManager.getAliceConfigByName('newDeviceBroadcastPort'))  # Default 12354
		self._listenPort = self._broadcastPort + 1

		self._listenSocket.bind(('', self._listenPort))

		self._broadcastTimer = None


	def onStop(self):
		self.stopBroadcasting()
		self._broadcastSocket.close()


	### to reimplement for any device type
	### Find A new Device
	def discover(self, uid: str = None, device: Device = None, voiceSiteId: str = ""):
		self.startBroadcastingForNewDevice(uid=uid, device=device, siteId=voiceSiteId)
		pass


	def getDeviceIcon(self, device: Device) -> str:
		if not device.connected:
			return 'satellite_offline.png'
		self.logInfo(f'dnd: {device.getCustomValue("dnd")}')
		if device.getCustomValue('dnd'):
			return 'satellite_muted.png'
		if not device.uid:
			return 'device_AliceSatellite.png'
		return 'satellite_online.png'


	def getDeviceConfig(self):
		# return the custom configuration of that deviceType
		pass


	def toggle(self, device: Device):
		# todo use functionality of the connected skill
		# todo there is currently no feedback loop -> when should the image on the screen be changed?
		self.MqttManager.publish(
			topic=constants.TOPIC_TOGGLE_DND,
			payload={
				'uid': device.uid
			}
		)


	@property
	def broadcastFlag(self) -> threading.Event:
		return self._broadcastFlag


	def startBroadcastingForNewDevice(self, siteId: str, uid: str = '', device: Device = None) -> bool:
		if self.isBusy():
			return False

		if not uid:
			uid = self.DeviceManager._getFreeUID()

		self.logInfo(f'Started broadcasting on {self._broadcastPort} for new device addition. Attributed uid: {uid}')
		self._listenSocket.listen(2)
		self.ThreadManager.newThread(name='broadcast', target=self.startBroadcast, args=[uid, siteId, device])

		self._broadcastTimer = self.ThreadManager.newTimer(interval=300, func=self.stopBroadcasting)

		self.broadcast(method=constants.EVENT_BROADCASTING_FOR_NEW_DEVICE, exceptions=[self.name], propagateToSkills=True)
		return True


	def stopBroadcasting(self):
		self.logInfo('Stopped broadcasting for new devices')
		self._broadcastFlag.clear()

		if self._broadcastTimer:
			self._broadcastTimer.cancel()

		self.broadcast(method=constants.EVENT_STOP_BROADCASTING_FOR_NEW_DEVICE, exceptions=[self.name], propagateToSkills=True)


	def startBroadcast(self, uid: str, replyOnSiteId: str = "", device: Device = None):
		self._broadcastFlag.set()
		location = device.getMainLocation()
		while self._broadcastFlag.isSet():
			self._broadcastSocket.sendto(bytes(f'{self.Commons.getLocalIp()}:{self._listenPort}:{location.getSaveName()}:{uid}', encoding='utf8'), ('<broadcast>', self._broadcastPort))
			try:
				sock, address = self._listenSocket.accept()
				sock.settimeout(None)
				answer = sock.recv(1024).decode()

				deviceIp = answer.split(':')[0]
				deviceTypeName = answer.split(':')[1]

				deviceType = self.DeviceManager.getDeviceTypeByName(deviceTypeName)

				if device:
					device.pairingDone(uid=uid)
					self.logWarning(f'Device with uid {uid} successfully paired')
				else:
					if self.DeviceManager.addNewDevice(deviceTypeID=deviceType.id, locationID=location.id, uid=uid):
						self.logInfo(f'New device with uid {uid} successfully added')
						if replyOnSiteId != "":
							self.MqttManager.say(text=self.TalkManager.randomTalk('newDeviceAdditionSuccess'), client=replyOnSiteId)
					else:
						self.logWarning('Failed adding new device')
						if replyOnSiteId != "":
							self.MqttManager.say(text=self.TalkManager.randomTalk('newDeviceAdditionFailed'), client=replyOnSiteId)

				self.ThreadManager.doLater(interval=5, func=self.WakewordRecorder.uploadToNewDevice, args=[uid])

				self._broadcastSocket.sendto(bytes('ok', encoding='utf8'), (deviceIp, self._broadcastPort))
				self.stopBroadcasting()
			except socket.timeout:
				self.logInfo('No device query received')


	def isBusy(self) -> bool:
		return self.ThreadManager.isThreadAlive('broadcast')
