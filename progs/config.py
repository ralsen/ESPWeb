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
    global yml
    global DataPath, RRDPath, dataSuffix, hirestime

    with open('../yml/config.yml', 'r') as ymlfile:
        yml = yaml.safe_load(ymlfile)
    logSuffix = yml['suffixes']['log']
    dataSuffix = yml['suffixes']['data']
    logYML = yml['debug']['logYML']
    debugdatefmt = yml['debug']['datefmt']
    hirestime = yml['debug']['hirestime']

    LogPath = yml['pathes']['ROOT_PATH'] + yml['pathes']['LOG']
    DataPath = yml['pathes']['ROOT_PATH'] + yml['pathes']['DATA']
    RRDPath = yml['pathes']['ROOT_PATH'] + yml['pathes']['RRD']
    YMLPath = yml['pathes']['ROOT_PATH'] + yml['pathes']['YML']

    x = datetime.datetime.now()
    logging.basicConfig(filename=LogPath + socket.gethostname()+x.strftime(logSuffix)+'.log',
                        level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)-s :: %(message)s [%(name)s] [%(lineno)s]',
                        datefmt=debugdatefmt)

    logging.info('\r\n')
    logging.info('-----------------------------------------------------------')
    with open(YMLPath + yml['files']['DATASTORE_YML'], 'r') as file:
        StoreYML = yaml.safe_load(file)
    
    Dstore = ds.DS(StoreYML) ######
    # '''  how to append a new DataStore from existing definition in datastore*.yml and set some values
    Dstore.append('Gsund', 'without_RRD_and_CONF')
    data = {}
    data['Gsund'] = {}
    data['Gsund']['name'] = 'mein'
    data['Gsund']['IP'] = 'Name'
    data['Gsund']['Type'] = 'tut'
    data['Gsund']['Version'] = 'nix zur Sache'
    ds.handle_DataSet(data)
    
    #ds.DS(StoreYML) 

    print(yml['devices'])
    if 'No_Name_70_03_9F_9A_7C_05' in yml['devices']:
        print('######### das gibt es ########')
        
    print(yml['archive'])
    logging.info('everything initialized !!!')