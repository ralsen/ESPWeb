#!/usr/bin/env python

import requests
import time
import socket

BASE_URL = 'http://192.168.1.53:8080'
'''
{'name': 'secondary000e8e93adb2', 'IP: ': '127.0.1.1', 'Disk usage [%]: ': 5.7, 'EDAG Busv. [V]: ': 92.5, 'charging: ': 1, 'System uptime [s]: ': 21511, 'App uptime [s]: ': 4174}
{'name': 'secondary000e8eaa31d6', 'IP: ': '192.168.2.26', 'Disk usage [%]: ': 6.1, 'EDAG Busv. [V]: ': 0, 'charging: ': 0, 'System uptime [s]: ': 21513, 'App uptime [s]: ': 2623}
{'name': 'secondary000e8eaa31d1', 'IP: ': '192.168.2.21', 'Disk usage [%]: ': 5.2, 'EDAG Busv. [V]: ': 0, 'charging: ': 0, 'System uptime [s]: ': 21510, 'App uptime [s]: ': 3702}
{'name': 'primary4c52629f697c', 'IP: ': '192.168.2.77', 'Disk usage [%]: ': 5.0, 'Power usage [kWh]: ': 384.15, 'Power [kW]: ': 0.38, 'System uptime [s]: ': 21511, 'App uptime [s]: ': 19888}
{'name': 'primary00305914880b', 'IP: ': '127.0.1.1', 'Disk usage [%]: ': 5.7, 'Power usage [kWh]: ': 384.15, 'Power [kW]: ': 0.38, 'System uptime [s]: ': 21510, 'App uptime [s]: ': 19964}
{'name': 'primary0030591540e0', 'IP: ': '127.0.1.1', 'Disk usage [%]: ': 5.5, 'Power usage [kWh]: ': 383.93, 'Power [kW]: ': 0.37, 'System uptime [s]: ': 21511, 'App uptime [s]: ': 19844}
'''
devices = []
device = {}
device['name'] = 'secondary000e8e93adb2'
device['IP'] = socket.gethostbyname(socket.gethostname())
device['Disk usage [%]'] = 5.7
device['EDAG Busv. [V]'] = 92.5
device['charging'] = 1
device['System uptime [s]'] = 12345
device['App uptime [s]'] = 67890
devices.append(device)

device = {}
device['name'] = 'secondary000e8eaa31d6'
device['IP'] = socket.gethostbyname(socket.gethostname())
device['Disk usage [%]'] = -5.7
device['EDAG Busv. [V]'] = -92.5
device['charging'] = 1
device['System uptime [s]'] = 12345
device['App uptime [s]'] = 67890
devices.append(device)

device = {}
device['name'] = 'primary4c52629f697c'
device['IP'] = socket.gethostbyname(socket.gethostname())
device['Disk usage [%]'] = 5.7
device['Power usage [kWh]'] = 384.15
device['Power [kW]'] = 0.38
device['System uptime [s]'] = 12345
device['App uptime [s]'] = 67890
devices.append(device)

device = {}
device['name'] = 'primary0030591540e0'
device['IP'] = socket.gethostbyname(socket.gethostname())
device['Disk usage [%]'] = 5.7
device['Power usage [kWh]'] = 384.15
device['Power [kW]'] = 0.38
device['System uptime [s]'] = 12345
device['App uptime [s]'] = 67890
devices.append(device)


print('Client started, sending to: ', BASE_URL)

while True:
    for dev in devices:
      dev['System uptime [s]'] = dev['System uptime [s]'] + 1
      dev['App uptime [s]'] = str(int(time.time()))[-2:]
      reponse = None
      try:
        response = requests.post(f'{BASE_URL}/', json=dev)
      except:
        print('could not send, abort: ', response)
        #exit()
      print(response.text)
      time.sleep(1)      
    time.sleep(5)
