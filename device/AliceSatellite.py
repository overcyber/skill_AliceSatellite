import socket
import sqlite3
import threading

from core.commons import constants
from core.device.model.Device import Device
from core.device.model.DeviceType import DeviceType
from core.dialog.model.DialogSession import DialogSession
from core.device.model.DeviceException import DeviceNotPaired


class AliceSatellite(DeviceType):

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
	def discover(self, device: Device, uid: str, replyOnSiteId: str = '', session: DialogSession = None) -> bool:
		return self.startBroadcastingForNewDevice(device=device, uid=uid, replyOnSiteId=replyOnSiteId)


	def getDeviceIcon(self, device: Device) -> str:
		if not device.connected:
			return 'satellite_offline.png'
		if device.getCustomValue('dnd'):
			return 'satellite_muted.png'
		if not device.uid:
			return 'AliceSatellite.png'
		return 'satellite_online.png'


	def getDeviceConfig(self):
		# return the custom configuration of that deviceType
		pass


	def toggle(self, device: Device):
		if device.uid:
		# todo use functionality of the connected skill
			self.MqttManager.publish(
				topic=constants.TOPIC_TOGGLE_DND,
				payload={
					'uid': device.uid
				}
			)
		else:
			raise DeviceNotPaired()


	@property
	def broadcastFlag(self) -> threading.Event:
		return self._broadcastFlag


	def startBroadcastingForNewDevice(self, device: Device, uid: str, replyOnSiteId: str = '') -> bool:
		if self.isBusy():
			return False

		self.logInfo(f'Started broadcasting on {self._broadcastPort} for new device addition. Attributed uid: {device.uid}')
		self._listenSocket.listen(2)
		self.ThreadManager.newThread(name='broadcast', target=self.startBroadcast, args=[device, uid, replyOnSiteId])

		self._broadcastTimer = self.ThreadManager.newTimer(interval=300, func=self.stopBroadcasting)

		self.broadcast(method=constants.EVENT_BROADCASTING_FOR_NEW_DEVICE, exceptions=[self.name], propagateToSkills=True)
		return True


	def stopBroadcasting(self):
		if not self.isBusy():
			return

		self.logInfo('Stopped broadcasting for new devices')
		self._broadcastFlag.clear()

		self._broadcastTimer.cancel()
		self.broadcast(method=constants.EVENT_STOP_BROADCASTING_FOR_NEW_DEVICE, exceptions=[self.name], propagateToSkills=True)


	def startBroadcast(self, device: Device, uid: str, replyOnSiteId: str = ''):
		self._broadcastFlag.set()
		location = device.getMainLocation()
		while self._broadcastFlag.isSet():
			self._broadcastSocket.sendto(bytes(f'{self.Commons.getLocalIp()}:{self._listenPort}:{location.getSaveName()}:{uid}', encoding='utf8'), ('<broadcast>', self._broadcastPort))
			try:
				sock, address = self._listenSocket.accept()
				sock.settimeout(None)
				answer = sock.recv(1024).decode()

				deviceIp = answer.split(':')[0]

				device.pairingDone(uid=uid)
				self.logWarning(f'Device with uid {uid} successfully paired')
				if replyOnSiteId:
					self.MqttManager.say(text=self.TalkManager.randomTalk('newDeviceAdditionSuccess', skill='system'), client=replyOnSiteId)

				self.ThreadManager.doLater(interval=5, func=self.WakewordRecorder.uploadToNewDevice, args=[uid])

				self._broadcastSocket.sendto(bytes('ok', encoding='utf8'), (deviceIp, self._broadcastPort))
				self.stopBroadcasting()
			except socket.timeout:
				self.logInfo('No device query received')


	def isBusy(self) -> bool:
		return self.ThreadManager.isThreadAlive('broadcast')
