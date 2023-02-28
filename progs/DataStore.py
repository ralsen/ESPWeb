#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#import shared_files.config as config
import config as cfg
import logging
import time
import datetime
import threading
import re
import string
import rrdtool

logger = logging.getLogger(__name__)

class DS():
    ds = dict()
    def __init__(self, StoreYML):
        self.Stores = StoreYML
        for Store, template in StoreYML['generate_stores']['ESP'].items():
            DS.append(self, Store, template)

    def append(self, Store, template):
        template = self.Stores['DataStores'][template]
        print(f'Building Store for: {Store}')
        logger.info(f'Building Store for: {Store}')
        self.ds[Store] = dict()
        for ShelfTag, x in template.items():
            self.ds[Store][ShelfTag] = dict()
            if ShelfTag == 'Commons':       # initialize Commons
                self.ds[Store]['Commons']['header'] = 'time'
                self.ds[Store]['Commons']['Active'] = False
                self.ds[Store]['Commons']['initTime'] = datetime.datetime.now()
            if ShelfTag != 'Commons':       # Commons are not part of the csv-header  
                if x['STORE_MODE'] != 'NONE':
                    self.ds[Store]['Commons']['header'] += ',' + ShelfTag
            self.ds[Store][ShelfTag]['CURRENT_DATA'] = 0
            self.ds[Store][ShelfTag]['STORE_MODE_DATA'] = 0
            for DataBox, Value in x.items():
                self.ds[Store][ShelfTag][DataBox] = dict()
                self.ds[Store][ShelfTag][DataBox] = Value
        self.ds[Store]['Commons']['Service'] = Service(Store) # start store handling
        

class Service():
    MyName = ''
    def __init__(self, StoreName):
        self.MyName = StoreName
        threading.Thread(target=self._monitoring_thread, daemon=True).start()        
      
    def _monitoring_thread(self):
        logger.info('DataStare monitoring started')
        while True:
            try:
                DS.ds[self.MyName]['Commons']['MERGE']
                self.merge()
            except:
                pass
            if(DS.ds[self.MyName]['Commons']['TIMEOUT']):
                DS.ds[self.MyName]['Commons']['TIMEOUT'] -= 1
                if(not DS.ds[self.MyName]['Commons']['TIMEOUT']):
                    DS.ds[self.MyName]['Commons']['Active'] = False
                    logger.error(f'Message missed: {self.MyName}')
                    print(f'Message missed: {self.MyName}')
            time.sleep(1)

    def handle_DataSet(self, DataSet):
        
        if cfg.hirestime:
            timeStamp = str(time.time())
        else:
            timeStamp = str(int(time.time()))
        for key in DataSet.keys():
            try:
                self.handleData(DataSet[key], timeStamp)
            except Exception as err:
                logger.error(f'receiving invalid DataSet: {key} - {type(err)}')
                print(f'receiving invalid DataSet: {key} - {type(err)}')

    def handle_CAN(self, msg):
      try:
          decoded_DBC = config.CAN_dbc.decode_message(msg.arbitration_id, msg.data)
      except:
          logger.error(f'receiving unknown CAN-Bus message-ID: {str(msg.arbitration_id)}')
          return
      if config.hirestime:
          timeStamp = str(msg.timestamp)
      else:
          timeStamp = str(int(msg.timestamp))
      self.handleData(decoded_DBC, timeStamp)

    def handleData(self, DataSet, timeStamp):
        if DS.ds[self.MyName]['Commons']['TIMEOUT'] == 0 and DS.ds[self.MyName]['Commons']['RELOAD_TIMEOUT'] != 0:
            logger.info(f'Message send resume: {self.MyName}')
            print(f'Message send resume: {self.MyName}')
        DS.ds[self.MyName]['Commons']['Active'] = True
        DS.ds[self.MyName]['Commons']['TIMEOUT'] = DS.ds[self.MyName]['Commons']['RELOAD_TIMEOUT']
        
        csv_line = timeStamp
        update = False
        resstr = ''
        for StoreShelf in DS.ds[self.MyName]:
            if StoreShelf == 'Commons':
                continue
            res= None
            if StoreShelf in DataSet:
                res = self.updateData(StoreShelf, DataSet.get(StoreShelf))
                if res:
                    update = True

            try:
                x = DS.ds[self.MyName][StoreShelf]['DECIMALS'] 
            except:
                x = 8

            if (res != None):
                try:
                    resstr = str(round(res, x))
                except Exception as err:
                    resstr = str(res)
            else:
                resstr = ''

            if DS.ds[self.MyName]['Commons']['FORMAT'] == 'SINGLE_CSV':
                if res != None:
                    self.writeDataSet(StoreShelf, csv_line + ',' + resstr)
                    return

            if DS.ds[self.MyName]['Commons']['FORMAT'] == 'MULTI_CSV':
                try:
                    DS.ds[self.MyName]['Commons']['FILLED_UP']
                    try:
                        fillerstr = str(round(DS.ds[self.MyName][StoreShelf]['STORE_MODE_DATA'], x))
                    except:
                        fillerstr = str(DS.ds[self.MyName][StoreShelf]['STORE_MODE_DATA'])
                except Exception as e:
                    fillerstr = resstr
                if(DS.ds[self.MyName][StoreShelf]['STORE_MODE'] != 'NONE'):
                    csv_line = csv_line + ',' + fillerstr
        if update:
            self.writeDataSet(StoreShelf, csv_line)

    def updateData(self, DataShelf, DataBoxValue):
        try:
            DS.ds[self.MyName][DataShelf]['CURRENT_DATA'] = DataBoxValue
        except Exception as err:
            logger.error(f'{type(err).__name__} in: {self.MyName} - {DataShelf}')
            return None

        try: # values can be omitted in the *.signals.yml
            DS.ds[self.MyName][DataShelf]['CURRENT_IN_RANGE'] = DS.ds[self.MyName][DataShelf]['CURRENT_DATA'] >= \
                                                        DS.ds[self.MyName][DataShelf]['MIN'] and \
                                                        DS.ds[self.MyName][DataShelf]['CURRENT_DATA'] <= \
                                                        DS.ds[self.MyName][DataShelf]['MAX']
        except: pass                                                                
        if(DS.ds[self.MyName][DataShelf]['STORE_MODE'] == 'NONE'):
            return None
        if(DS.ds[self.MyName][DataShelf]['STORE_MODE'] == 'ALL'):
            DS.ds[self.MyName][DataShelf]['STORE_MODE_DATA'] = DataBoxValue
            self.processValue(DataShelf, DataBoxValue)
            return DataBoxValue
        if(DS.ds[self.MyName][DataShelf]['STORE_MODE'] == 'CHANGE'):
            if(DS.ds[self.MyName][DataShelf]['STORE_MODE_DATA'] != DataBoxValue):
                DS.ds[self.MyName][DataShelf]['STORE_MODE_DATA'] = DataBoxValue
                self.processValue(DataShelf, DataBoxValue)
                return DataBoxValue
            return None
        if(DS.ds[self.MyName][DataShelf]['STORE_MODE'] == 'COUNT'):
            if(DS.ds[self.MyName][DataShelf]['CNT']):
                DS.ds[self.MyName][DataShelf]['CNT'] -= 1
                return None
            else:
                DS.ds[self.MyName][DataShelf]['CNT'] = DS.ds[self.MyName][DataShelf]['RELOAD_CNT'] - 1
                DS.ds[self.MyName][DataShelf]['STORE_MODE_DATA'] = DataBoxValue
                self.processValue(DataShelf, DataBoxValue)
                return DataBoxValue
        if(DS.ds[self.MyName][DataShelf]['STORE_MODE'] == 'AVR'):
            if DS.ds[self.MyName][DataShelf]['CNT']:
                DS.ds[self.MyName][DataShelf]['CNT'] -= 1
                DS.ds[self.MyName][DataShelf]['AVR_SUBTOTAL'] += DataBoxValue
                return None
            else:
                DS.ds[self.MyName][DataShelf]['CNT'] = DS.ds[self.MyName][DataShelf]['RELOAD_CNT'] - 1
                DS.ds[self.MyName][DataShelf]['STORE_MODE_DATA'] = (DS.ds[self.MyName][DataShelf]['AVR_SUBTOTAL'] + DataBoxValue) / \
                                                    DS.ds[self.MyName][DataShelf]['RELOAD_CNT']
                DS.ds[self.MyName][DataShelf]['AVR_SUBTOTAL'] = 0
                self.processValue(DataShelf, DS.ds[self.MyName][DataShelf]['STORE_MODE_DATA'])
                return DS.ds[self.MyName][DataShelf]['STORE_MODE_DATA']

    def processValue(self, DataShelf, value):
        try:
            DS.ds[self.MyName][DataShelf]['CURRENT_IN_RANGE'] = DS.ds[self.MyName][DataShelf]['STORE_MODE_DATA'] >= \
                                                      DS.ds[self.MyName][DataShelf]['MIN'] and \
                                                      DS.ds[self.MyName][DataShelf]['STORE_MODE_DATA'] <= \
                                                      DS.ds[self.MyName][DataShelf]['MAX']
        except KeyError:
            pass

    def mergeOperation(self, data, str):
        data[self.MyName][str[1]] = DS.ds[str[2]][str[3]][str[4]]
        if str[0] == 'and':
            data[self.MyName][str[1]] = True
            for i in range(2, len(str), 3):
                data[self.MyName][str[1]] = data[self.MyName][str[1]] and DS.ds[str[i]][str[i+1]][str[i+2]]
        if str[0] == 'or':
            data[self.MyName][str[1]] = False
            for i in range(2, len(str), 3):
                data[self.MyName][str[1]] = data[self.MyName][str[1]] or DS.ds[str[i]][str[i+1]][str[i+2]]
        if str[0] == 'add':
            data[self.MyName][str[1]] = 0
            for i in range(2, len(str), 3):
                data[self.MyName][str[1]] = data[self.MyName][str[1]] + DS.ds[str[i]][str[i+1]][str[i+2]]
        return data

    def merge(self):
        data = dict()
        data[self.MyName] = dict()
        try:
            DS.ds[self.MyName]['Commons']['TIMEOUT'] = DS.ds[self.MyName]['Commons']['RELOAD_TIMEOUT']
            DS.ds[self.MyName]['Commons']['Active'] = True
            mergeInfo = DS.ds[self.MyName]['Commons']['MERGE']
            for mergeStr in mergeInfo:
                if mergeStr[0] == 'get':
                    data[self.MyName][mergeStr[1]] = DS.ds[mergeStr[2]][mergeStr[3]][mergeStr[4]]
                else: data = self.mergeOperation(data, mergeStr)
            self.handle_DataSet(data)
        except Exception as err:
            logging.error('call of merge for a non merging device.')
            print('call of merge for a non merging device. ', err)
            pass
    def DataBase(self):
        # print('DataBase: ', self.MyName)
        try:
            self.doRRD()
        except Exception as err:    
            logger.error(f'fehlr in RRD-Verarbeitung: {type(err).__name__} in: {self.MyName}')
            print(f'fehlr in RRD-Verarbeitung: {type(err).__name__} in: {self.MyName}')

    def doRRD(self):
        try:
            DBInfo = DS.ds[self.MyName]['Commons']['RRD_DB']
        except: 
            # print('no RRD-handling')
            return
        #print('doing RRD')                
        for block in range(len(DBInfo)):
            rrdstr = 'N'
            for line in range(len(DBInfo[block])):
                res = self.getRRDValue(DBInfo[block][line])
                # print('--->: ', res)
                if DBInfo[block][line][0] == 'OUTFILE':
                    rrdfile = cfg.RRDPath + str(res) + '.rrd'
                else: rrdstr += ':' + str(res)
            #print(rrdfile, ' - ', rrdstr, end='\r\n\r\n')
            rrdtool.update(rrdfile, rrdstr)
        return    

    def getRRDValue(self, DBStr):
        # print('getRRDValue: ', DBStr)

        if DBStr[0][0] != '§':
            store = self.MyName
        else:
            store = DBStr[0][1:]

        if DBStr[1] == 'CONST':
            value = DBStr[2]
        elif DBStr[1][0] == '§':
            value = DS.ds[store][DBStr[1][1:]][DBStr[2]]
        else: print('FEHELR')
        if DBStr[0] == 'INFILE':
            try:
                with open(cfg.DataPath + value, 'r') as file:
                    value = file.read()
            except:
                print(f'File not found: {cfg.DataPath}{value}')
        # print('getRRDValue (store): ', store, ' - ', value)
        return value

    def writeDataSet(self, Shelf, line): 
        if DS.ds[self.MyName]['Commons']['FORMAT'] == 'SINGLE_CSV':
            FileName = cfg.DataPath + self.MyName + '_' + Shelf + '_' + DS.ds[self.MyName][Shelf]['STORE_MODE'] + DS.ds[self.MyName]['Commons']['initTime'].strftime(cfg.dataSuffix) + '.txt'
            DS.ds[self.MyName]['Commons']['header'] = 'time,' + Shelf
        if DS.ds[self.MyName]['Commons']['FORMAT'] == 'MULTI_CSV':
            FileName = cfg.DataPath + self.MyName + DS.ds[self.MyName]['Commons']['initTime'].strftime(cfg.dataSuffix) + '.txt'
        try:
            with open(FileName, 'r') as DataFile: 
                pass
        except:        
            line = DS.ds[self.MyName]['Commons']['header'] + '\n' + line
        with open(FileName, 'a') as DataFile: 
            DataFile.write(line + '\n')
            DataFile.close()
        self.DataBase()

def pick(Store, Shelf, DataBox):
    return DS.ds[Store][Shelf][DataBox]

def put(Store, *args):
    data = dict()
    data[Store] = dict()
    for arg in args:
        data[Store][arg[0]] = arg[1]
    handle_DataSet(data)

def handle_DataSet(DataSet):
    try:
        DS.ds[list(DataSet.keys())[0]]['Commons']['Service'].handle_DataSet(DataSet)
    except:
        logger.info(f'unknown Datastore: {DataSet.keys()}')
        print (f'unknown Datastore: {DataSet.keys()}')
  
def handle_CAN(StoreName, DataSet):
    DS.ds[StoreName]['Commons']['Service'].handle_CAN(DataSet)
    