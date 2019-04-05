import time
import usocket
from machine import Pin, ADC
from utime import sleep, ticks_ms
from mpu6050 import *

IP_RECEIVER = "IP_CLIENT"
PORT_RECEIVER = 8010
IOT_RECEIVER = usocket.getaddrinfo(IP_RECEIVER, PORT_RECEIVER)[0][-1]
PIN_FAIL = 2
PIN_OK = 16

def signed_converter(num):
	if num >= 0:
		return num
	else:
		return abs(num) + 32767
		
def signed_deconverter(num):
	if num < 32768:
		return num
	else:
		return -(num-32767)
		

class main_program(object):
	def __init__(self, acc_obj, sleep_time, calibration_amount, measurement_amount):
		self.pin_fail = Pin(PIN_FAIL, Pin.OUT, value=1)
		self.pin_ok = Pin(PIN_OK, Pin.OUT, value=1)
		self.acc_obj = acc_obj
		self.acc_obj.get_measurement()
		self.sleep_time = sleep_time
		self.measurement_amount = measurement_amount
		self.calibration_amount = calibration_amount
		self.stored_values = []
		time.sleep(sleep_time)
	def calibrate_accelerometer(self):
		x, y, z = [], [], []
		for i in range(self.calibration_amount):
			time.sleep(self.sleep_time)
			self.acc_obj.get_raw_measurement()
			x.append(self.acc_obj.x_accel_raw)
			y.append(self.acc_obj.y_accel_raw)
			z.append(self.acc_obj.z_accel_raw)
		self.x_average = sum(x) // self.calibration_amount
		self.y_average = sum(y) // self.calibration_amount
		self.z_average = sum(z) // self.calibration_amount
		self.calibration_bytes = signed_converter(self.x_average).to_bytes(2, 'little') + signed_converter(self.y_average).to_bytes(2, 'little') + signed_converter(self.z_average).to_bytes(2, 'little')
		print(self.x_average, self.y_average, self.z_average)
	def get_measurement(self):
		self.acc_obj.get_raw_measurement()
		x_bytes = signed_converter(self.acc_obj.x_accel_raw).to_bytes(2, 'little')
		y_bytes = signed_converter(self.acc_obj.y_accel_raw).to_bytes(2, 'little')
		z_bytes = signed_converter(self.acc_obj.z_accel_raw).to_bytes(2, 'little')
		return x_bytes + y_bytes + z_bytes
	def get_all_measurements(self):
		self.stored_values = bytearray()
		self.stored_values.extend(self.calibration_bytes)
		for i in range(self.measurement_amount):
			time.sleep(self.sleep_time)
			self.stored_values.extend(self.get_measurement())
	def is_failed(self, fail):
		if fail:
			self.pin_fail.value(0)
			self.pin_ok.value(1)
		else:
			self.pin_fail.value(1)
			self.pin_ok.value(0)
	def send_measurements(self):
		self.get_all_measurements()
		s = usocket.socket()
		s.settimeout(0.5)
		try:
			s.connect(IOT_RECEIVER)
			sdat = s.send(self.stored_values)
			s.close()
			self.is_failed(False)
		except:
			self.is_failed(True)
		# ~ self.get_all_measurements()
		# ~ s = usocket.socket()
		# ~ s.settimeout(0.5)
		# ~ s.connect(IOT_RECEIVER)
		# ~ sdat = s.send(self.stored_values)
		# ~ s.close()

mpu_obj = mpu6050(5,4)
main_obj = main_program(mpu_obj, 0.02, 500, 50)
print("CALIBRATION")
main_obj.calibrate_accelerometer()
while True:
	main_obj.send_measurements()
	#print(main_obj.stored_values)

