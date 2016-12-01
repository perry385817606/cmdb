#encoding: utf-8

import time
import psutil
import requests
from datetime import datetime

INTERVAL = 10
URL = 'http://localhost:18989/monitor/host/create/'

def get_addr():
	addr = '0.0.0.0'
	nics = psutil.net_if_addrs().get('eth0')
	for nic in nics:
		if nic.address.find('.') != -1:
			addr = nic.address
			break
	return addr

def monitor():
	ip_addr = get_addr()
	while True:
		usage = {}
		usage['ip'] = ip_addr
		usage['disk'] = psutil.disk_usage('/').percent
		usage['cpu'] = psutil.cpu_percent()
		usage['mem'] = psutil.virtual_memory().percent
		usage['m_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		print usage
		response = requests.post(URL,data=usage)
		if response.ok:
			print response.json()
		else:
			print 'error'
		time.sleep(INTERVAL)

if __name__ == '__main__':
	monitor()