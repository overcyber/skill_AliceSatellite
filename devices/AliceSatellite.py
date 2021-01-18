import sqlite3
from pathlib import Path
from typing import Dict, Union

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


	def __init__(self, data: Union[sqlite3.Row, Dict]):
		super().__init__(data)


	def getDeviceIcon(self) -> Path:
		if not self.connected:
			return super().getDeviceIcon()
		else:
			return Path(f'{self.Commons.rootDir()}/skills/{self.skillName}/devices/img/connected.png')
