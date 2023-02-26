#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import yaml
import platform
import re
import DataStore as ds
import socket
import datetime

def init():
    global ymlcfg
    global DataPath, RRDPath, dataSuffix, hirestime

    with open("../yml/config.yml", "r") as ymlfile:
        ymlcfg = yaml.safe_load(ymlfile)
    logSuffix = ymlcfg["suffixes"]["log"]
    dataSuffix = ymlcfg["suffixes"]["data"]
    logYML = ymlcfg["debug"]["logYML"]
    debugdatefmt = ymlcfg["debug"]["datefmt"]
    hirestime = ymlcfg["debug"]["hirestime"]

    LogPath = ymlcfg["pathes"]["ROOT_PATH"] + ymlcfg["pathes"]["LOG"]
    DataPath = ymlcfg["pathes"]["ROOT_PATH"] + ymlcfg["pathes"]["DATA"]
    RRDPath = ymlcfg["pathes"]["ROOT_PATH"] + ymlcfg["pathes"]["RRD"]
    YMLPath = ymlcfg["pathes"]["ROOT_PATH"] + ymlcfg["pathes"]["YML"]

    x = datetime.datetime.now()
    logging.basicConfig(filename=LogPath + socket.gethostname()+x.strftime(logSuffix)+".log",
                        level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)-s :: %(message)s [%(name)s] [%(lineno)s]',
                        datefmt=debugdatefmt)

    logging.info("\r\n")
    logging.info("-----------------------------------------------------------")
    with open(YMLPath + ymlcfg["files"]["DATASTORE_YML"], "r") as file:
        StoreYML = yaml.safe_load(file)
    
    Dstore = ds.DS(StoreYML) ######
    # """  how to append a new DataStore from existing definition in datastore*.yml and set some values
    Dstore.append("Gsund", "without_RRD_and_CONF")
    data = {}
    data["Gsund"] = {}
    data["Gsund"]["name"] = "mein"
    data["Gsund"]["IP"] = "Name"
    data["Gsund"]["Type"] = "tut"
    data["Gsund"]["Version"] = "nix zur Sache"
    ds.handle_DataSet(data)
    
    #ds.DS(StoreYML) 

    print(ymlcfg["devices"])
    if "No_Name_70_03_9F_9A_7C_05" in ymlcfg["devices"]:
        print("######### das gibt es ########")
        
    print(ymlcfg["archive"])
    logging.info("everything initialized !!!")