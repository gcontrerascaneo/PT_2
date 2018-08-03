function move(kind, direction, amount, speed) {
	$.ajax({
		'type': 'POST',
		'url': '/move',
		'data': {'kind':kind, 'direction':direction, 'amount':amount, 'speed':speed},
		'dataType': 'text'
	});
}

$(document).ready(function(){
	$("#nw").click(function(){ move('pivot', 'left', degrees, speed); });
	$("#n").click(function(){ move('move', 'forward', distance, speed); });
	$("#ne").click(function(){ move('pivot', 'right', degrees, speed); });
	
	$("#w").click(function(){ move('spin', 'left', degrees, speed); });
	$("#c").click(function(){ move('wave', 'around', degrees, speed); });
	$("#e").click(function(){ move('spin', 'right', degrees, speed); });
	
	$("#sw").click(function(){ move('pivot', 'left', -degrees, speed); });
	$("#s").click(function(){ move('move', 'backward', distance, speed); });
	$("#se").click(function(){ move('pivot', 'right', -degrees, speed); });
	
	$("#speak").submit(function(e) {
		$.ajax({
			'type': 'POST',
			'url': '/speak',
			'data': {'text': $("#speak-text").val()},
			'dataType': 'text'
		});
		$("#speak-text").val("");
		e.preventDefault();
	});
});

$(document).keyup(function(e) {
	var activeElement = $(document.activeElement)
	if (activeElement.prop("tagName") == "INPUT") {
		return;
	}
	switch(e.which) {
		case 32: move('wave', 'around', distance, speed); break; // space
		case 37: move('spin', 'left', degrees, speed); break; // left
		case 38: move('move', 'forward', distance, speed); break; // up
		case 39: move('spin', 'right', degrees, speed); break; // right
		case 40: move('move', 'backward', distance, speed); break; // down
		default: return; // exit this handler for other keys
	}
	e.preventDefault();
});