
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from distutils.log import debug
from logging import Logger
#from tkinter.messagebox import NO
import yaml
import platform
import cantools
import re
import socket
import shared_files.DataStore as ds
import datetime

print("---------- starting main_server @ ", datetime.datetime.now())

print(socket.gethostname()[:-12])

with open("shared_files/config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

manner = socket.gethostname()[:-12]

if manner == "primary":
    with open(cfg[manner]["location"], "r") as ymllocfile:
        loc = yaml.safe_load(ymllocfile)
    cfg.update(yaml.safe_load(open(cfg[manner]["location"])))
    for i in cfg["transponder"]:
        print ("ID:", i , "| EDAG:", cfg["transponder"][i]["EDAG"], "| Coil:", cfg["transponder"][i]["Coil"], \
               "| GPIO:",cfg["transponder"][i]["GPIO"], "| Pin: ", cfg["transponder"][i]["PIN"])
    powermeter_ip = cfg[manner]['powermeter']['ip']
    powermeter_username = cfg[manner]['powermeter']['username']
    powermeter_password = cfg[manner]['powermeter']['password']

if manner == 'secondary':
    server_hostname_list = cfg[manner]['server']['hostname_list']
    server_authentication_port = cfg[manner]["server"]["port1"]
    can_antenna = cfg[manner]["can"]["antenna"]
    NetPrefix = cfg[manner]["network"]["NetPrefix"]
    HostPrefix = cfg[manner]["network"]["Hostprefix"]
    WiFiDelay = cfg[manner]["network"]["WiFiDelay"]
    display_orientation = cfg[manner]["GUI"]["display_orientation"]
    WPT_Button = cfg[manner]["GUI"]["WPT_Button"]
    kill_Button = cfg[manner]["GUI"]["kill_Button"]
    dummy_machine = cfg[manner]["GUI"]["dummy_machine"]
    gui_infos = cfg[manner]["GUI"]["infos"]


server_authentication_port = cfg["secondary"]["server"]["port1"]
can_car = cfg[manner]["can"]["car"]


path_to_own_cert = cfg[manner]['tls']['path_to_own_cert']
path_to_public_certs = cfg[manner]['tls']['path_to_public_certs']

web_infos = cfg[manner]["WEB"]["infos"]
web_URL = cfg[manner]["WEB"]["BASE_URL"]

siodi_path = cfg["pathes"]["siodi"]

logSuffix = cfg["suffixes"]["log"]
dataSuffix = cfg["suffixes"]["data"]
logYML = cfg["debug"]["logYML"]
withRFID = cfg["debug"]["withRFID"]
datefmt = cfg["debug"]["datefmt"]
hirestime = cfg["debug"]["hirestime"]

autobind = cfg[manner]["network"]["autobind"]

with open(cfg[manner]["DATASTORE_YML"], "r") as file:
    loc = yaml.safe_load(file)
cfg.update(yaml.safe_load(open(cfg[manner]["DATASTORE_YML"])))

DataStorePath = cfg["pathes"]["DATA_STORE_PATH"]
CAN_dbc_File = cfg["pathes"]["CONFIG_PATH"] + cfg[manner]["CAN_dbc"]
with open(CAN_dbc_File, "r") as file:
    CAN_dbc = cantools.database.load_file(CAN_dbc_File)

with open(cfg[manner]["DATASTORE_YML"], "r") as file:
    StoreYML = yaml.safe_load(file)

Dstore = ds.DS(StoreYML) ######
# """  how to append a new DataStore from existing definition in datastore*.yml and set some values
Dstore.append("Gsund", "System")
data = {}
data["Gsund"] = {}
data["Gsund"]["MyName"] = "mein"
data["Gsund"]["own_IP"] = "Name"
data["Gsund"]["ServerName"] = "tut"
data["Gsund"]["Server_IP"] = "nix zur Sache"

data = dict()
data["System"] = dict()
data["System"]["MyName"] = socket.gethostname()
data["System"]["own_IP"] = socket.gethostbyname(data["System"]["MyName"])
data["System"]["ServerName"] = "None"
data["System"]["Server_IP"] = "None"
ds.handle_DataSet(data)
