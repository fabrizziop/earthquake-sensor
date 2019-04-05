import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import matplotlib.dates as md
import matplotlib.ticker as ticker
from yattag import Doc
import base64
import numpy as np
import datetime
import time
import gc
import math
import smtplib
import ssl
from email.mime.text import MIMEText
#REPLACE YOUR_USER with your user.
graph_location = "/home/YOUR_USER/earthquake_main/http/"

CONST_DIV_ACC = 16384
MEAS_PER_LINE = 50
DESIRED_TICKS = 6
MAX_G_ALLOWANCE = 0.004
GMAIL_ENABLED = True
GMAIL_USER = "YOUR_EMAIL@gmail.com"
GMAIL_PW = "YOUR_PW"
GMAIL_SENDTO = ["EMAIL1@gmail.com", "EMAIL2@gmail.com"]

def send_mail_easy(mail_msg):
	msg = MIMEText("".join(mail_msg))
	msg['Subject'] = "SmartQuake"
	msg['From'] = GMAIL_USER
	msg['To'] = ", ".join(GMAIL_SENDTO)
	attempts_remaining = 4
	while attempts_remaining > 0:
		try:
			print("TRYING EMAIL, ATTEMPTS REMAINING:",attempts_remaining)
			ssl_context = ssl.create_default_context()
			smtp_inst = smtplib.SMTP(host="smtp.gmail.com",port=587, timeout=5)
			smtp_inst.starttls(context=ssl_context)
			smtp_inst.ehlo()
			smtp_inst.login(GMAIL_USER, GMAIL_PW)
			smtp_inst.send_message(msg)
			smtp_inst.close()
			attempts_remaining = 0
		except:
			time.sleep(30)
			attempts_remaining -= 1
			print("EMAIL FAILURE")


def is_file_accessible(file_name):
	try:
		test_file = open(file_name,'r')
		test_file.close()
		return True
	except:
		return False

def get_names_to_read():
	f = open("cwrite","r")
	n = int(f.read())
	f.close()
	flist = []
	for i in range(1, n+1):
		n2 = str(i)
		while len(n2) < 8:
			n2 = "0" + n2
		flist.append(n2)
	return flist

def get_all_data(file_name_list):
	dates = []
	currents = []
	for file_name in file_name_list:
		a = open(file_name,"r")
		for line in a:
			tline = line.split(",")
			dates.append(tline[0])
			currents.append(tline[3])
			#print(tline[0],tline[3])
		a.close()
	return dates, currents

def get_data(file_name):
	dates = []
	calibrations = []
	measurements = []
	a = open(file_name,"r")
	# ~ print(a.read())
	for line in a:
		tline = line.split(",")
		dates.append(tline[0])
		calibrations.append([int(tline[1]), int(tline[2]), int(tline[3])])
		measurements.append(tline[4:])
		#print(tline[0],tline[3])
	return dates, calibrations, measurements

def get_ticks(date_list):
	tick_list = []
	tick_list.append(date_list[0])
	tick_interval = len(date_list) / (DESIRED_TICKS - 1)
	for i in range(DESIRED_TICKS-1):
		tick_list.append(date_list[int(i*tick_interval)-1])
	# ~ for i in range(50, len(date_list)+1, MEAS_PER_LINE*4):
		# ~ tick_list.append(date_list[i-1])
	return tick_list

def process_raw_data(raw_dates, raw_calibrations, raw_measurements):
	earthquake_found = False
	earthquake_measurement = 0
	measurement_amount = len(raw_measurements[0])//3
	true_dates = [] #		   [1,2,3]
	true_calibrations = [] # [ [x,y,z], [x,y,z] ]
	true_measurements = [] # [ [x,y,z], [x,y,z] ]
	true_sum = [] #		       [1,2,3]
	first_date_difference = int(raw_dates[1]) - int(raw_dates[0])
	first_date_divided = first_date_difference / measurement_amount
	for i in range(measurement_amount):
		print(datetime.datetime.fromtimestamp(int(int(raw_dates[0]) - ((measurement_amount - i)*first_date_divided))/1000))
		true_dates.append(datetime.datetime.fromtimestamp(int(int(raw_dates[0]) - ((measurement_amount - i)*first_date_divided))/1000))
		true_calibrations.append(raw_calibrations[0])
		true_measurements.append([int(raw_measurements[0][i*3])-true_calibrations[0][0],int(raw_measurements[0][(i*3)+1])-true_calibrations[0][1],int(raw_measurements[0][(i*3)+2])-true_calibrations[0][2]])
	for i in range(1, len(raw_dates)):
		date_difference = int(raw_dates[i]) - int(raw_dates[i-1])
		date_divided = date_difference / measurement_amount
		for j in range(measurement_amount):
			true_dates.append(datetime.datetime.fromtimestamp(int(int(raw_dates[i]) - ((measurement_amount - j)*date_divided))/1000))
			temp_calibrations = raw_calibrations[i]
			true_calibrations.append(raw_calibrations[i])
			true_measurements.append([int(raw_measurements[i][j*3])-temp_calibrations[0],int(raw_measurements[i][(j*3)+1])-temp_calibrations[1],int(raw_measurements[i][(j*3)+2])-temp_calibrations[2]])
	for i in range(len(true_measurements)):
		true_sum.append(math.sqrt(true_measurements[i][0]**2+true_measurements[i][1]**2+true_measurements[i][2]**2)/CONST_DIV_ACC)
	#print(true_dates)
	#print(true_calibrations)
	#print(true_measurements)
	#print(true_sum)
	measurements_by_axis = [ [], [], [] ]
	max_measurements_by_axis = []
	for i in range(len(true_measurements)):
		measurements_by_axis[0].append(true_measurements[i][0] / CONST_DIV_ACC)
		measurements_by_axis[1].append(true_measurements[i][1] / CONST_DIV_ACC)
		measurements_by_axis[2].append(true_measurements[i][2] / CONST_DIV_ACC)
	for i in range(0,3):
		max_measurements_by_axis.append(max(measurements_by_axis[i]))
	max_measurements_by_axis.append(max(true_sum))
	while earthquake_found == False:
		if true_sum[earthquake_measurement] >= MAX_G_ALLOWANCE:
			earthquake_found = True
		else:
			earthquake_measurement += 1
	# ~ for i in range(len(raw_dates)-1, 0, -1):
		# ~ date_difference = raw_dates(i) - raw_dates(i-1)

		# ~ true_dates.append(datetime.datetime.fromtimestamp(int(date)/1000))
	# ~ for current in raw_currents:
		# ~ true_currents.append(float(current))
	return true_dates, true_calibrations, measurements_by_axis, true_sum, max_measurements_by_axis, earthquake_measurement

def update_earthquake_info():
	files_to_read = get_names_to_read()
	event_list = []
	for file_name in files_to_read:
		b = get_data(file_name)
		c = process_raw_data(b[0], b[1], b[2])
		event_list.append([file_name, c[0], c[1], c[2], c[3], c[4], c[5]])
		if not is_file_accessible(graph_location+file_name+".html"):
			if GMAIL_ENABLED:
				generate_email(file_name, c[0], c[1], c[2], c[3], c[4], c[5])
			generate_plots_and_data(file_name, c[0], c[1], c[2], c[3], c[4], c[5])
			generate_individual_html(file_name, c[0], c[1], c[2], c[3], c[4], c[5])
	generate_html(event_list)

def generate_plots_and_data(name, dates, calibrations, measurements, sums, max_measurements, earthquake_measurement):

	plt.figure(figsize=(16,9))
	plt.title("X AXIS of Event "+str(int(name))+ " at "+str(dates[earthquake_measurement])+ " MAX: " + str(max_measurements[0])[:7] + " g")
	plt.xlabel('TIME')
	plt.ylabel('X AXIS ACCELERATION (g)')
	ax=plt.gca()
	xfmt = md.DateFormatter('%m-%d %H:%M:%S.%f')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(dates, measurements[0], 'r-')
	plt.xticks(get_ticks(dates))
	plt.axhspan(-MAX_G_ALLOWANCE/2, MAX_G_ALLOWANCE/2, alpha=0.1, color='green')
	plt.axhspan(MAX_G_ALLOWANCE/2, MAX_G_ALLOWANCE, alpha=0.1, color='yellow')
	plt.axhspan(-MAX_G_ALLOWANCE/2, -MAX_G_ALLOWANCE, alpha=0.1, color='yellow')
	plt.grid()
	plt.savefig(graph_location+name+"_x.png", dpi=400)

	plt.clf()
	
	plt.figure(figsize=(16,9))
	plt.title("Y AXIS of Event "+str(int(name))+ " at "+str(dates[earthquake_measurement])+ " MAX: " + str(max_measurements[1])[:7] + " g")
	plt.xlabel('TIME')
	plt.ylabel('Y AXIS ACCELERATION (g)')
	ax=plt.gca()
	xfmt = md.DateFormatter('%m-%d %H:%M:%S.%f')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(dates, measurements[1], 'r-')
	plt.xticks(get_ticks(dates))
	plt.axhspan(-MAX_G_ALLOWANCE/2, MAX_G_ALLOWANCE/2, alpha=0.1, color='green')
	plt.axhspan(MAX_G_ALLOWANCE/2, MAX_G_ALLOWANCE, alpha=0.1, color='yellow')
	plt.axhspan(-MAX_G_ALLOWANCE/2, -MAX_G_ALLOWANCE, alpha=0.1, color='yellow')
	plt.grid()
	plt.savefig(graph_location+name+"_y.png", dpi=400)


	plt.clf()

	plt.figure(figsize=(16,9))
	plt.title("Z AXIS of Event "+str(int(name))+ " at "+str(dates[earthquake_measurement])+ " MAX: " + str(max_measurements[2])[:7] + " g")
	plt.xlabel('TIME')
	plt.ylabel('Z AXIS ACCELERATION (g)')
	ax=plt.gca()
	xfmt = md.DateFormatter('%m-%d %H:%M:%S.%f')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(dates, measurements[2], 'r-')
	plt.xticks(get_ticks(dates))
	plt.axhspan(-MAX_G_ALLOWANCE/2, MAX_G_ALLOWANCE/2, alpha=0.1, color='green')
	plt.axhspan(MAX_G_ALLOWANCE/2, MAX_G_ALLOWANCE, alpha=0.1, color='yellow')
	plt.axhspan(-MAX_G_ALLOWANCE/2, -MAX_G_ALLOWANCE, alpha=0.1, color='yellow')
	plt.grid()
	plt.savefig(graph_location+name+"_z.png", dpi=400)

	plt.clf()
	# ~ print(sums)
	plt.figure(figsize=(16,9))
	plt.title("Acceleration Vector Mag of Event "+str(int(name))+ " at "+str(dates[earthquake_measurement])+ " MAX: " + str(max_measurements[3])[:7] + " g")
	plt.xlabel('TIME')
	plt.ylabel('ACCELERATION VECTOR ADDITION MAG (g)')
	ax=plt.gca()
	xfmt = md.DateFormatter('%m-%d %H:%M:%S.%f')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(dates, sums, 'r-')
	plt.xticks(get_ticks(dates))
	plt.axhspan(0, MAX_G_ALLOWANCE/2, alpha=0.1, color='green')
	plt.axhspan(MAX_G_ALLOWANCE/2, MAX_G_ALLOWANCE, alpha=0.1, color='yellow')
	plt.grid()
	plt.savefig(graph_location+name+"_mag.png", dpi=400)


	plt.clf()
	plt.close('all')

def generate_email(name, dates, calibrations, measurements, sums, max_measurements, earthquake_measurement):
	a = [
	'GENERATED AT: ' + datetime.datetime.now().isoformat()+"\n",
	'EVENT NUMBER: '+str(int(name))+ " at "+str(dates[earthquake_measurement])+"\n",
	'X AXIS MAXIMUM ACCELERATION: ' + str(max_measurements[0])[:7] + " g"+"\n",
	'Y AXIS MAXIMUM ACCELERATION: ' + str(max_measurements[1])[:7] + " g"+"\n",
	'Z AXIS MAXIMUM ACCELERATION: ' + str(max_measurements[2])[:7] + " g"+"\n",
	'MAXIMUM ACCELERATION VECTOR MAGNITUDE: ' + str(max_measurements[3])[:7] + " g"+"\n",
	]
	send_mail_easy(a)

def generate_individual_html(name, dates, calibrations, measurements, sums, max_measurements, earthquake_measurement):
	doc, tag, text, line = Doc().ttl()
	with tag('a', 'href=index.html'):
		line('h3', '<-----GO BACK')
	line('h2', 'GENERATED AT: ' + datetime.datetime.now().isoformat())
	line('h2', 'EVENT NUMBER: '+str(int(name))+ " at "+str(dates[earthquake_measurement]))
	line('h2', 'X AXIS MAXIMUM ACCELERATION: ' + str(max_measurements[0])[:7] + " g")
	line('h2', 'Y AXIS MAXIMUM ACCELERATION: ' + str(max_measurements[1])[:7] + " g")
	line('h2', 'Z AXIS MAXIMUM ACCELERATION: ' + str(max_measurements[2])[:7] + " g")
	line('h2', 'MAXIMUM ACCELERATION VECTOR MAGNITUDE: ' + str(max_measurements[3])[:7] + " g")
	with open(graph_location+name+"_x.png", "rb") as f2b64:
		base64img = str(base64.b64encode(f2b64.read()))
		doc.stag('img', src='data:image/png;base64,'+base64img[2:-1], width="100%")
	# ~ line('h3', 'LAST 86400 MEASUREMENTS')
	with open(graph_location+name+"_y.png", "rb") as f2b64:
		base64img = str(base64.b64encode(f2b64.read()))
		doc.stag('img', src='data:image/png;base64,'+base64img[2:-1], width="100%")
	# ~ line('h3', 'LAST 3600 MEASUREMENTS')
	with open(graph_location+name+"_z.png", "rb") as f2b64:
		base64img = str(base64.b64encode(f2b64.read()))
		doc.stag('img', src='data:image/png;base64,'+base64img[2:-1], width="100%")
	# ~ line('h3', 'LAST 1800 MEASUREMENTS')
	with open(graph_location+name+"_mag.png", "rb") as f2b64:
		base64img = str(base64.b64encode(f2b64.read()))
		doc.stag('img', src='data:image/png;base64,'+base64img[2:-1], width="100%")
	# ~ line('h3', 'LAST 600 MEASUREMENTS')
	with tag('a', 'href=index.html'):
		line('h3', '<-----GO BACK')
	tw = open(graph_location+name+".html","w")
	tw.write(doc.getvalue())
	tw.close()

def generate_html(all_data):
	doc, tag, text, line = Doc().ttl()
	line('h2', 'GENERATED AT: ' + datetime.datetime.now().isoformat())
	line('h2', 'LAST EVENT DATA: ')
	line('h2', 'EVENT NUMBER: '+str(int(all_data[-1][0]))+ " at "+str(all_data[-1][1][all_data[-1][6]]))
	line('h2', 'X AXIS MAXIMUM ACCELERATION: ' + str(all_data[-1][5][0])[:7] + " g")
	line('h2', 'Y AXIS MAXIMUM ACCELERATION: ' + str(all_data[-1][5][1])[:7] + " g")
	line('h2', 'Z AXIS MAXIMUM ACCELERATION: ' + str(all_data[-1][5][2])[:7] + " g")
	line('h2', 'MAXIMUM ACCELERATION VECTOR MAGNITUDE: ' + str(all_data[-1][5][3])[:7] + " g")
	line('h2', 'ALL EVENTS BELOW:')
	line('h4', '---------------------------------')
	for i in range(len(all_data)-1, -1, -1):
		with tag('a', 'href='+all_data[i][0]+'.html'):
			line('h4', 'EVENT NUMBER: '+str(int(all_data[i][0]))+ " at "+str(all_data[i][1][all_data[i][6]]))
			line('h4', 'MAX ACCELERATION: '+ str(all_data[i][5][3])[:7] + " g")
		line('h4', '---------------------------------')
	tw = open(graph_location+"index.html","w")
	tw.write(doc.getvalue())
	tw.close()


update_earthquake_info()
