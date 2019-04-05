MPU6050_I2C_ADDR = 0x68
MPU6050_REG_PM = 0X6B
MPU6050_REG_GC = 0X1B
MPU6050_REG_AC = 0X1C
MPU6050_REG_DATA = 0x3B
MPU6050_REG_DLPF = 0x1A
MPU6050_REG_DLPF_DATA = 0b00000110
MPU6050_ACC = 16384
MPU6050_GYR = 131

import machine, time
from machine import I2C, Pin
class mpu6050(object):
	def __init__(self, pin_scl, pin_sda, hi_low=False):
		self.I2C_ADDR = MPU6050_I2C_ADDR+hi_low
		self.i2c_obj = I2C(scl=Pin(pin_scl), sda=Pin(pin_sda))
		self.i2c_obj.start()
		self.i2c_obj.writeto_mem(self.I2C_ADDR, MPU6050_REG_PM, bytearray([0]))
		self.i2c_obj.stop()
		self.i2c_obj.start()
		self.i2c_obj.writeto_mem(self.I2C_ADDR, MPU6050_REG_GC, bytearray([0]))
		self.i2c_obj.stop()
		self.i2c_obj.start()
		self.i2c_obj.writeto_mem(self.I2C_ADDR, MPU6050_REG_AC, bytearray([0]))
		self.i2c_obj.stop()
		#optional config
		self.i2c_obj.start()
		self.i2c_obj.writeto_mem(self.I2C_ADDR, MPU6050_REG_DLPF, bytearray([MPU6050_REG_DLPF_DATA]))
		self.i2c_obj.stop()
	def get_raw_values(self):
		self.i2c_obj.start()
		self.raw_data = self.i2c_obj.readfrom_mem(self.I2C_ADDR, MPU6050_REG_DATA, 14)
		self.i2c_obj.stop()
		return self.raw_data
	def convert_to_int(self, input_bytes):
		if (input_bytes[0] & 128):
			temp_number = -(((input_bytes[0] ^ 255) << 8) + (input_bytes[1] ^ 255) + 1)
		else:
			temp_number = int.from_bytes(input_bytes, "big")
		return temp_number
		
	def process_raw_values(self):
		self.x_accel_raw = self.convert_to_int(self.raw_data[0:2])
		self.y_accel_raw = self.convert_to_int(self.raw_data[2:4])
		self.z_accel_raw = self.convert_to_int(self.raw_data[4:6])
		self.temperature_raw = self.convert_to_int(self.raw_data[6:8])
		self.x_gyro_raw = self.convert_to_int(self.raw_data[8:10])
		self.y_gyro_raw = self.convert_to_int(self.raw_data[10:12])
		self.z_gyro_raw = self.convert_to_int(self.raw_data[12:14])
	def convert_to_real(self):
		self.acceleration = [self.x_accel_raw/MPU6050_ACC, self.y_accel_raw/MPU6050_ACC, self.z_accel_raw/MPU6050_ACC]
		self.gyroscope = [self.x_gyro_raw/MPU6050_GYR, self.y_gyro_raw/MPU6050_GYR, self.z_gyro_raw/MPU6050_GYR]
		self.temperature = (self.temperature_raw/340) + 36.53
	def get_measurement(self):
		self.get_raw_values()
		self.process_raw_values()
		self.convert_to_real()
	def get_raw_measurement(self):
		self.get_raw_values()
		self.process_raw_values()
	def print_measurement(self):
		self.get_measurement()
		print(self.acceleration)
		#print(self.temperature)
		#print(self.gyroscope)
