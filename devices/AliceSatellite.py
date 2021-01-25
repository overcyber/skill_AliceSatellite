from core.device.model.Device import Device
from core.device.model.DeviceAbility import DeviceAbility


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
