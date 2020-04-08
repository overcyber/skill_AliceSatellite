(function () {

	let timer;
	let timerStarted = false;

	$.ajax({
		url: '/home/widget/',
		data: JSON.stringify({
			skill: 'AliceSatellite',
			widget: 'Satellites',
			func: 'getSatellites',
			param: ''
		}),
		contentType: 'application/json',
		dataType: 'json',
		type: 'POST'
	}).done(function(devices) {
		for (let id in devices) {
			let device = JSON.parse(devices[id]);

			let color = device['connected'] ? '--text' : 'red';
			let $tile = $('<div class="Satellites_tile" id="' + device['uid'] + '">' +
					'<div class="Satellites_tile_deviceName ' + color + '">' + device['room'] + '</div>' +
					'<div class="Satellites_tile_muteUnmute"><i class="fas fa-microphone-alt fa-4x" aria-hidden="true" id="Satellites_muteUnmute_' + device['uid'] + '"></i></div>');

			$tile.append(
				'<div class="Satellites_tile_heartbeat"><i class="fas fa-heart-broken fa-2x" aria-hidden="true" id="Satellites_heartbeat_' + device['uid'] + '"></i></div>'
			);

			$tile.append('</div>');
			$('#Satellites_satelliteContainer').append($tile);
		}
	});

	function onConnect() {
		MQTT.subscribe('projectalice/devices/heartbeat');
		MQTT.subscribe('projectalice/devices/stopListen');
		MQTT.subscribe('projectalice/devices/startListen');
		MQTT.subscribe('projectalice/devices/disconnection');
		MQTT.subscribe('projectalice/devices/greeting');
	}

	function deadSatellite(uid) {
		$('#Satellites_heartbeat_' + uid).removeClass('fa-heartbeat').addClass('fa-heart-broken');
		$('#' + uid).find('.Satellites_tile_deviceName').removeClass('--text').addClass('red');
	}

	function satelliteLife(uid) {
		$('#Satellites_heartbeat_' + uid).removeClass('fa-heart-broken').addClass('fa-heartbeat');
		$('#' + uid).find('.Satellites_tile_deviceName').removeClass('red').addClass('--text');
		startTimeout(uid);
	}

	function startTimeout(uid) {
		if (timerStarted) {
			clearTimeout(timer);
		}

		timer = setTimeout(function () {
			deadSatellite(uid);
		}, 5000);
		timerStarted = true;
	}

	function onMessage(msg) {
		let payload = JSON.parse(msg.payloadString);
		if (msg.topic === 'projectalice/devices/heartbeat') {
			satelliteLife(payload['uid']);
		} else if (msg.topic === 'projectalice/devices/stopListen') {
			$('#Satellites_muteUnmute_' + payload['uid']).removeClass('fa-microphone-alt').addClass('fa-microphone-alt-slash');
		} else if (msg.topic === 'projectalice/devices/startListen') {
			$('#Satellites_muteUnmute_' + payload['uid']).removeClass('fa-microphone-alt-slash').addClass('fa-microphone-alt');
		} else if (msg.topic == 'projectalice/devices/disconnection') {
			deadSatellite(payload['uid'])
		} else if (msg.topic == 'projectalice/devices/greeting') {
			satelliteLife(payload['uid']);
		}
	}

	mqttRegisterSelf(onConnect, 'onConnect');
	mqttRegisterSelf(onMessage, 'onMessage');

})();