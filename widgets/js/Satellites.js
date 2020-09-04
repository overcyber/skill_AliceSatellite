(function () {

	let timer;
	let timerStarted = false;

	let topics = [
		'projectalice/devices/heartbeat',
		'projectalice/devices/stopListen',
		'projectalice/devices/startListen',
		'projectalice/devices/toggleListen',
		'projectalice/devices/disconnection',
		'projectalice/devices/greeting',
		'projectalice/devices/status'
	]

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
			if (id === 'success') {
				continue;
			}

			let device = JSON.parse(devices[id]);

			let color = device['connected'] ? '--text' : 'red';
			let $tile = $('<div class="tile" id="' + device['uid'] + '"><div class="Satellites_tile_deviceName ' + color + '">' + device['room'] + '</div>');

			//
			let micClass = "fas fa-microphone-alt fa-4x";
			if(device['custom']['dnd']){
				micClass = "fas fa-microphone-alt-slash fa-4x";
			}

			//
			let $button = $('<div class="Satellites_tile_muteUnmute"><i class="'+micClass+'" aria-hidden="true" id="Satellites_muteUnmute_' + device['uid'] + '"></i></div>');
			$button.on('click touchstart', function(){
				$.ajax({
					url: '/home/widget/',
					data: JSON.stringify({
						skill: 'AliceSatellite',
						widget: 'Satellites',
						func: 'toggleMute',
						param: JSON.stringify({
							'uid': device['uid']
						})
					}),
					contentType: 'application/json',
					dataType: 'json',
					type: 'POST'
				});
			})

			let $heartbeat = $('<div class="Satellites_tile_heartbeat"><i class="fas fa-heart-broken fa-2x" aria-hidden="true" id="Satellites_heartbeat_' + device['uid'] + '"></i></div>');
			$tile.append($button, $heartbeat, '</div>')
			$('#Satellites_satelliteContainer').append($tile);
		}
	});

	function onConnect() {
		for (const topic in topics) {
			MQTT.subscribe(topic);
		}
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
		if (!topics.includes(msg.topic) || !msg.payloadString) {
			return;
		}

		let payload = JSON.parse(msg.payloadString);
		if (msg.topic === 'projectalice/devices/heartbeat') {
			satelliteLife(payload['uid']);
		} else if (msg.topic === 'projectalice/devices/stopListen') {
			$('#Satellites_muteUnmute_' + payload['uid']).removeClass('fa-microphone-alt').addClass('fa-microphone-alt-slash');
		} else if (msg.topic === 'projectalice/devices/startListen') {
			$('#Satellites_muteUnmute_' + payload['uid']).removeClass('fa-microphone-alt-slash').addClass('fa-microphone-alt');
		} else if (msg.topic === 'projectalice/devices/toggleListen') {
			if ($('#Satellites_muteUnmute_' + payload['uid']).hasClass('fa-microphone-alt-slash')) {
				$('#Satellites_muteUnmute_' + payload['uid']).removeClass('fa-microphone-alt-slash').addClass('fa-microphone-alt');
			} else {
				$('#Satellites_muteUnmute_' + payload['uid']).removeClass('fa-microphone-alt').addClass('fa-microphone-alt-slash');
			}
		} else if (msg.topic == 'projectalice/devices/disconnection') {
			deadSatellite(payload['uid'])
		} else if (msg.topic == 'projectalice/devices/greeting') {
			satelliteLife(payload['uid']);
		}
		// else if (msg.topic == 'projectalice/devices/status') {
		//	if('dnd' in payload) {
		//		satelliteStatus(payload['uid'], payload['dnd'])
		//	}
		//}
	}

	mqttRegisterSelf(onConnect, 'onConnect');
	mqttRegisterSelf(onMessage, 'onMessage');

})();
