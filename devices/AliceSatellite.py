from core.device.model.Device import Device
from core.device.model.DeviceAbility import DeviceAbility
from core.commons import constants
import json


class AliceSatellite(Device):

	@classmethod
	def getDeviceTypeDefinition(cls) -> dict:
		return {
			'deviceTypeName'        : 'AliceSatellite',
			'perLocationLimit'      : 1,
			'totalDeviceLimit'      : 0,
			'allowLocationLinks'    : True,
			'allowHeartbeatOverride': False,
			'heartbeatRate'         : 2,
			'deviceSettings'        : dict(),
			'abilities'             : [DeviceAbility.PLAY_SOUND, DeviceAbility.CAPTURE_SOUND]
		}


	def onUIClick(self) -> dict:
		# todo: implement advanced dnd behaviour as well (mute output - but not all?)
		if self.getParam('micMuted'):
			# both muted, enable mic
			self.MqttManager.mqttClient.publish(topic=constants.TOPIC_HOTWORD_TOGGLE_ON,
												payload=json.dumps({'uid': self.getConfig('uuid')}))
			self.updateParam('micMuted', False)
		else:
			# nothing muted, mute mic
			self.MqttManager.mqttClient.publish(topic=constants.TOPIC_HOTWORD_TOGGLE_OFF,
			                                    payload=json.dumps({'uid': self.getConfig('uuid')}))
			self.updateParam('micMuted', True)

		return super().onUIClick()
