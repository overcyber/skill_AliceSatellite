import sqlite3
from pathlib import Path
from typing import Dict, Union

from core.commons import constants
from core.device.model.Device import Device


class AliceSatellite(Device):

	def __init__(self, data: Union[sqlite3.Row, Dict]):
		super().__init__(data)


	def getDeviceIcon(self) -> Path:
		if not self.connected:
			return Path(f'{self.Commons.rootDir()}/skills/{self.skillName}/device/img/{self.deviceTypeName}.png')
		elif self.connected:
			return Path(f'{self.Commons.rootDir()}/skills/{self.skillName}/device/img/connected.png')


	def onUIClick(self):
		super().onUIClick()

		# TODO satellites should be able to mic and/or sound mute
		if self.getParam('micMuted') and self.getParam('soundMuted'):
			topic = constants.TOPIC_STOP_DND
			self.updateParams('soundMuted', False)
			self.updateParams('micMuted', False)
		elif self.getParam('micMuted'):
			topic = constants.TOPIC_DND
			self.MqttManager.mqttClient.unsubscribe(constants.TOPIC_AUDIO_FRAME.format(self.ConfigManager.getAliceConfigByName('uuid')))
			self.updateParams('soundMuted', True)
		else:
			topic = constants.TOPIC_DND
			self.WakewordManager.disableEngine()
			self.updateParams('micMuted', True)

		self.MqttManager.publish(
			topic=topic,
			payload={
				'uid': self.uid
			}
		)
