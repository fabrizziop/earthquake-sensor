import socket
import time
import math
import subprocess
# ~ CALIB_CONST_MUL = 0.08076
MEASUREMENT_AMOUNT = 50
EARTHQUAKE_RESET = 10
MAX_G_ALLOWANCE = 0.004 * 16384
CORRECTION_FACTOR = 0.03
GENERATE_HTML = True
#REPLACE YOUR_USER with your user.
GENERATE_HTML_SCRIPT = "screen -dmS earthquakegen python3 /home/YOUR_USER/earthquake_main/gen_script.py"
WARMUP_TIME = 120
s = socket.socket()
s.bind(("192.168.5.192",8010))
s.listen(100)

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

def simple_data(ba):
	calibration = [signed_deconverter(int.from_bytes(ba[:2], 'little')), signed_deconverter(int.from_bytes(ba[2:4], 'little')), signed_deconverter(int.from_bytes(ba[4:6], 'little'))]
	current_data = []
	for i in range(6, 6+(MEASUREMENT_AMOUNT*6), 2):
		current_data.append(signed_deconverter(int.from_bytes(ba[i:i+2], 'little')))
	return calibration, current_data

def calculate_deviation(cal_data, cur_data):
	deviation_list = []
	for i in range(0, MEASUREMENT_AMOUNT*3, 3):
		# ~ print(cur_data[i], cal_data[0], abs(cur_data[i]-cal_data[0])**2)
		# ~ print(cur_data[i+1], cal_data[1], abs(cur_data[i+1]-cal_data[1])**2)
		# ~ print(cur_data[i+2], cal_data[2], abs(cur_data[i+2]-cal_data[2])**2)
		deviation_list.append(math.sqrt(abs(cur_data[i]-cal_data[0])**2+abs(cur_data[i+1]-cal_data[1])**2+abs(cur_data[i+2]-cal_data[2])**2))
	#print(deviation_list)
	#print(max(deviation_list)/16384)
	return deviation_list, max(deviation_list)
		
def calculate_avg_deviation(cal_data, cur_data):
	average_x = 0
	average_y = 0
	average_z = 0
	for i in range(0, MEASUREMENT_AMOUNT*3, 3):
		average_x += cur_data[i]-cal_data[0]
		average_y += cur_data[i+1]-cal_data[1]
		average_z += cur_data[i+2]-cal_data[2]
	return average_x/MEASUREMENT_AMOUNT, average_y/MEASUREMENT_AMOUNT, average_z/MEASUREMENT_AMOUNT

def get_name_to_write():
	f = open("cwrite","r")
	n = str(int(f.read()) + 1)
	f.close()
	f = open("cwrite","w")
	f.write(n)
	f.close()
	while len(n) < 8:
		n = "0" + n
	return str(n)
	
def get_data():
	conn, addr = s.accept()
	sdat = conn.recv(6+(MEASUREMENT_AMOUNT*6))
	conn.close()
	# ~ print(sdat)
	return simple_data(sdat)

def generate_huge_string(current_data):
	a = str(current_data[0])
	for item in current_data[1:]:
		a += "," + str(item)
	return a
#creating file


current_earthquake_reset = 0
calibration_correction = [0,0,0]
while True:
	conn, addr = s.accept()
	sdat = conn.recv(6+(MEASUREMENT_AMOUNT*6))
	conn.close()
	processed_data = simple_data(sdat)
	if sum(processed_data[0]) > 1024:
		true_cal_data = [processed_data[0][0] + calibration_correction[0], processed_data[0][1] + calibration_correction[1], processed_data[0][2] + calibration_correction[2]]
		true_cal_data_int = [int(true_cal_data[0]),int(true_cal_data[1]),int(true_cal_data[2])]
		deviation_list, maximum_deviation = calculate_deviation(true_cal_data_int, processed_data[1])
		print("DEV:",maximum_deviation/16384)
		if WARMUP_TIME == 0:
			if maximum_deviation >= MAX_G_ALLOWANCE:
				if current_earthquake_reset == 0:
					file_to_open = get_name_to_write()
					print("Earthquake Detected")
					print("Opening file", file_to_open)
					obj_to_write = open(file_to_open, "w")
				current_earthquake_reset = EARTHQUAKE_RESET
			if current_earthquake_reset >= 1:
				print("Reset count:", current_earthquake_reset)
				obj_to_write.write(str(int(time.time()*1000)) +"," + generate_huge_string(true_cal_data_int) + "," + generate_huge_string(processed_data[1]) + "\n")
				obj_to_write.flush()
				current_earthquake_reset -= 1
				if current_earthquake_reset == 0:
					print("Closing File")
					obj_to_write.close()
					if GENERATE_HTML:
						temporal_process = subprocess.Popen(GENERATE_HTML_SCRIPT,stdout=subprocess.DEVNULL, shell=True)
		avg_deviations = calculate_avg_deviation(true_cal_data, processed_data[1])
		calibration_correction = [calibration_correction[0] + avg_deviations[0]*CORRECTION_FACTOR, calibration_correction[1] + avg_deviations[1]*CORRECTION_FACTOR, calibration_correction[2] + avg_deviations[2]*CORRECTION_FACTOR]
		print(calibration_correction)
		print(processed_data[0],true_cal_data_int)
		if WARMUP_TIME > 0:
			print("WARMUP")
			WARMUP_TIME -= 1
	else:
		print("Null data received, avoiding false report!")
