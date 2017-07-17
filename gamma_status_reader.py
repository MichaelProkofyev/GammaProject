import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import argparse
from datetime import datetime
import threading
import queue
import time
import random
from pythonosc import osc_message_builder, udp_client

grid = []



def requestStatus():
	# r = requests.get(host + '/gridstatus')
	s = requests.Session()
	retries = Retry(total=10, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
	s.mount('http://', HTTPAdapter(max_retries=retries))


	r = s.get('http://46.4.28.17:6001/gridstatus')
	global grid

	new_grid = r.json()
	changed_elements = []

	if not grid: #IF GRID IS EMPTY
		grid = new_grid
	else:
		for rowIdx, row in enumerate(new_grid):
			# print('row' + str(rowIdx))
			for colIdx, cell in enumerate(row):
				if new_grid[rowIdx][colIdx] != grid[rowIdx][colIdx]:
					# print('Row: ' + str(rowIdx) + " Col: " +str(colIdx) + 'Value: ' + str(cell))
					changed_elements.append({'row': rowIdx, 'column': colIdx, 'value': cell})

	
	#STOPPING HERE
	return new_grid
	# print("Changed elemeents " + str(len(changed_elements)))
	return

def sendReset():
	duration_param = {'nextduration': '10000'}
	tick = datetime.now()
	r = requests.get('http://46.4.28.17:6001/reset', params=duration_param)
	tock = datetime.now()   

	return

end_flag_q = queue.Queue()

def http_status_loop(end_flag_q):
	parser = argparse.ArgumentParser()
	parser2 = argparse.ArgumentParser()
	parser.add_argument("--ip", default="127.0.0.1")
	parser2.add_argument("--ip", default="127.0.0.1")
	parser.add_argument("--port", type=int, default=10000)
	parser2.add_argument("--port", type=int, default=10001)
	args = parser.parse_args()
	args2 = parser2.parse_args()
	osc_client = udp_client.SimpleUDPClient(args.ip, args.port)
	osc_client_ping = udp_client.SimpleUDPClient(args2.ip, args2.port)

	# global osc_client
	# global grid
	while(True):
		try:
			tick = datetime.now()
			grid = requestStatus()
			tock = datetime.now()
			ping_time = (tock - tick).total_seconds()
			print(ping_time)
			osc_client_ping.send_message("/ping", float(ping_time) )		

			for rowIdx, row in enumerate(grid):
				# print('row' + str(rowIdx))
				for colIdx, cell in enumerate(row):
					osc_client.send_message("/cell" + str(rowIdx) + '_' + str(colIdx), cell)		
			# osc_client.send_message("/filter23", '\t'.join(str(grid[0])) )
			# osc_client.send_message("/filter23", 2.23)
		except KeyboardInterrupt:
			end_flag_q.put('FINISHED')
			print("^C received, shutting down")
			break
	return

#############################################
#HTTP STATUS
#############################################
#ENABLE 2
http_status_thread = threading.Thread(target=http_status_loop, args=(end_flag_q,), daemon=True)
http_status_thread.start()
# 
# while(True):
# 	time.sleep(0.1)
# 	print('MAIN THREAD')



s = end_flag_q.get()
# sendReset()

