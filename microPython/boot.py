import gc
import webrepl
import network
import time
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
	sta_if.active(True)
	sta_if.connect('SSID','WIFI_PSK')
	while not sta_if.isconnected():
		pass
sta_if.ifconfig(('IP_ADDR', 'NETMASK', 'GATEWAY', 'DNS'))
webrepl.start()
gc.collect()
