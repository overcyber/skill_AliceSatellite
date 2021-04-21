class AliceSatellite_Satellites extends Widget {

	constructor(uid, widgetId) {
		super(uid, widgetId);
		this.uid = uid;
		this.widgetId = widgetId;
		this.aliceSettings = JSON.parse(window.sessionStorage.aliceSettings);
		this.myDiv = document.querySelector(`[data-ref="AliceSatellites_${this.uid}"]`)
		this.timer = null;
		this.timerStarted = false;
		this.refresh();
		//this.interval = setInterval(() => this.refresh(), 1000 * 10);
		this.topics = [
			'projectalice/devices/heartbeat',
			'projectalice/devices/stopListen',
			'projectalice/devices/startListen',
			'projectalice/devices/toggleListen',
			'projectalice/devices/disconnection',
			'projectalice/devices/greeting',
			'projectalice/devices/status'
		]
		self = this;
		this.topics.forEach(function (topic) {
			self.subscribe(topic, self.onMessage);
		});
	}

	stop() {
		clearInterval(this.interval)
	}

	deadSatellite(uid) {
		this.myDiv.querySelector('#Satellites_heartbeat_' + uid).removeClass('fa-heartbeat').addClass('fa-heart-broken');
		this.myDiv.querySelector('#' + uid).find('.Satellites_tile_deviceName').removeClass('--text').addClass('red');
	}

	satelliteLife(uid) {
		this.myDiv.querySelector('#Satellites_heartbeat_' + uid).removeClass('fa-heart-broken').addClass('fa-heartbeat');
		this.myDiv.querySelector('#' + uid).find('.Satellites_tile_deviceName').removeClass('red').addClass('--text');
		this.startTimeout(uid);
	}

	startTimeout(uid) {
		if (this.timerStarted) {
			clearTimeout(this.timer);
		}

		this.timer = setTimeout(function () {
			this.deadSatellite(uid);
		}, 5000);
		this.timerStarted = true;
	}


	refresh() {
		let that = this
		fetch(`http://${this.aliceSettings['aliceIp']}:${this.aliceSettings['apiPort']}/api/v1.0.1/widgets/${this.widgetId}/function/getSatellites/`, {
			method : 'POST',
			body   : '{}',
			headers: {
				'auth'        : localStorage.getItem('apiToken'),
				'content-type': 'application/json'
			}
		}).then(response => response.json())
			.then(function (devices) {
				devices = devices.data
				for (let id in devices) {
					console.log(devices)
					if (id === 'success') {
						continue;
					}
					let device = devices[id];

					let color = device['connected'] ? '--text' : 'red';
					let $tile = document.createElement("div")
					$tile.className = "tile"
					$tile.id = device['uid']
					$tile.innerHTML = '<div class="Satellites_tile_deviceName ' + color + '">' + device['deviceConfigs']['displayName'] + '</div>'

					// get mic item
					let micClass = "fas fa-microphone-alt fa-4x";
					if (device['custom'] && 'dnd' in device['custom'] && device['custom']['dnd']) {
						micClass = "fas fa-microphone-alt-slash fa-4x";
					}

					//make button

					let $button = document.createElement("div")
					$button.className = "Satellites_tile_muteUnmute"
					$button.innerHTML = '<i class="' + micClass + '" aria-hidden="true" id="Satellites_muteUnmute_' + device['uid'] + '"></i>'
					$button.onclick = function () {
						fetch(`http://${that.aliceSettings['aliceIp']}:${that.aliceSettings['apiPort']}/api/v1.0.1/widgets/${that.widgetId}/function/toggleMute/`, {
							method : 'POST',
							body   : JSON.stringify({"uid": device["uid"]}),
							headers: {
								'auth'        : localStorage.getItem('apiToken'),
								'content-type': 'application/json'
							}
						})
					}

					let $heartbeat = document.createElement("div")
					$heartbeat.className = "Satellites_tile_heartbeat"
					$heartbeat.innerHTML = '<i class="fas fa-heart-broken fa-2x" aria-hidden="true" id="Satellites_heartbeat_' + device['uid'] + '"></i>'
					$tile.appendChild($button)
					$tile.appendChild($heartbeat)
					that.myDiv.appendChild($tile)
				}
			});
	}

	onMessage(msg) {
		if (!this.topics.includes(msg.topic) || !msg.payloadString) {
			return;
		}

		let payload = JSON.parse(msg.payloadString);
		if (msg.topic === 'projectalice/devices/heartbeat') {
			this.satelliteLife(payload['uid']);
		} else if (msg.topic === 'projectalice/devices/stopListen') {
			this.myDiv.querySelector('#Satellites_muteUnmute_' + payload['uid']).removeClass('fa-microphone-alt').addClass('fa-microphone-alt-slash');
		} else if (msg.topic === 'projectalice/devices/startListen') {
			this.myDiv.querySelector('#Satellites_muteUnmute_' + payload['uid']).removeClass('fa-microphone-alt-slash').addClass('fa-microphone-alt');
		} else if (msg.topic === 'projectalice/devices/toggleListen') {
			if (this.myDiv.querySelector('#Satellites_muteUnmute_' + payload['uid']).hasClass('fa-microphone-alt-slash')) {
				this.myDiv.querySelector('#Satellites_muteUnmute_' + payload['uid']).removeClass('fa-microphone-alt-slash').addClass('fa-microphone-alt');
			} else {
				this.myDiv.querySelector('#Satellites_muteUnmute_' + payload['uid']).removeClass('fa-microphone-alt').addClass('fa-microphone-alt-slash');
			}
		} else if (msg.topic == 'projectalice/devices/disconnection') {
			this.deadSatellite(payload['uid'])
		} else if (msg.topic == 'projectalice/devices/greeting') {
			this.satelliteLife(payload['uid']);
		}
		// else if (msg.topic == 'projectalice/devices/status') {
		//	if('dnd' in payload) {
		//		satelliteStatus(payload['uid'], payload['dnd'])
		//	}
		//}
	}
}


