import os
import pipes
import SimpleHTTPServer
import SocketServer
import subprocess
import sys
import urllib
import urlparse
import time

import ev3dev.ev3 as ev3

import ev3dev.core

SERVER_PORT = 8081

#LEFT_MOTOR = "outA"
#RIGHT_MOTOR = "outD"
#ARM_MOTOR = "outD"

def motor_block_until_finished(motor):
	while 'running' not in motor.state:
		pass
	while 'running' in motor.state:
		pass

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_POST(self):
		try:
			mname = "action_" + self.path[1:]
			method = getattr(self, mname)
		except AttributeError:
			return self.send_response(404)
		
		try:
			clength = int(self.headers["content-length"])
			form_data = self.rfile.read(clength)
			query = dict(urlparse.parse_qsl(form_data, keep_blank_values=True))
		except (KeyError, ValueError):
			return self.send_response(400) # Bad Request
		
#		try:
		response = method(**query)
#		except:
#			return self.send_response(500) # Internal Server Error
		
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(response)
	
	def action_speak(self, text):
		command = "espeak -a 200 -s 80 --stdout {} | aplay".format(pipes.quote(text))
		subprocess.Popen(command, shell=True)
   
	
	def action_move(self, kind="move", speed="20", direction="forward", amount="10"):
		global motors
		amount = int(amount) # Exceptions get handled in move caller
		speed = int(speed)
		
		print (kind, speed, direction, amount)
		
		if amount == 0:
			raise Exception("Invalid amount 0")
		#if 'running' in (motors['left'].state + motors['right'].state + motors['arm'].state):
		#	raise Exception("Robot already in motion")
		
		if kind in ('move', 'pivot', 'spin'):
			left_amount, right_amount = {
				'move': {'forward': (amount, amount), 'backward': (-amount, -amount)},
				'pivot': {'left': (0, amount), 'right': (amount, 0)},
				'spin': {'left': (-amount, amount), 'right': (amount, -amount)}
			}[kind][direction]
			print (left_amount, right_amount, speed)
			motors['left'].run_to_rel_pos(position_sp = left_amount, speed_sp = speed)
			motors['right'].run_to_rel_pos(position_sp = right_amount, speed_sp = speed)
			time.sleep(1)
		elif kind == "wave":
			motors['arm'].run_to_abs_pos(position_sp=-45, speed_sp=180)
			motor_block_until_finished(motors['arm'])
		  #motors['arm'].run_to_abs_pos(position_sp=45, speed_sp=180)
			motor_block_until_finished(motors['arm'])
			motors['arm'].run_to_abs_pos(position_sp=0, speed_sp=180)
			motor_block_until_finished(motors['arm'])
		else:
		  raise Exception("Unknown movement type {}".format(kind))

if __name__ == '__main__':
	motors = {
		'left': ev3dev.core.LargeMotor('outD'),
		'right': ev3dev.core.LargeMotor('outA'),
		#'arm': ev3dev.core.MediumMotor(ARM_MOTOR)
	}
	for motor in motors:
		motors[motor].reset()
		#motors[motor].speed_regulation_enabled = "on"
	
	os.chdir("./www/root")
	# Allow new instances of the script to use the port even if the old one died unexpectedly
	SocketServer.TCPServer.allow_reuse_address = True
	httpd = SocketServer.TCPServer(("", SERVER_PORT), MyHandler)
	print("Running on port {}".format(SERVER_PORT))
	try:
		httpd.serve_forever()
	finally:
		for motor in motors:
			motors[motor].stop()
