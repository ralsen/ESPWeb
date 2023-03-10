#\\testpi\root\mnt\samba\Daten\Projekte\ESPWeb\server.py

from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import sys
import ast
import time
import datetime
import threading
import logging 
import config as cfg
import DataStore as ds

logger = logging.getLogger(__name__)

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                site = ""
                site += ' <html> \
                        <head> \
                        <meta http-equiv="refresh" content="2"> \
                        <TITLE>Python Web-Server</TITLE> \
                        <style type="text/css">body{FONT-FAMILY: Arial, Helvetica, sans-serif} \
                        p         {FONT-FAMILY: Arial, Helvetica, sans-serif} \
                        a:link    {color:#000000; text-decoration:none} \
                        a:hover   {color:#000000; text-decoration:none; background-color:#C0C0C0;} \
                        a:visited {color:#000000; text-decoration:none} \
                        a:active  {color:#000000; text-decoration:none} \
                        .oben     {vertical-align:top;   } \
                        .mittig   {vertical-align:middle;} \
                        .unten    {vertical-align:bottom;} \
                        </style> \
                        </head> \
                        <body \
                        bgcolor="#d0d0d0" text="#434343" link="#1a1a1a" alink="#1a1a1a" vlink="#1a1a1a"> \
                        <center> \
                        <h2> Hello, this is the LaneCharge Webserver</h2></form> \
                        </center> \
                        <center> \
                        {TABLE} \
                        </center>'
                table = '<style> \
                            table { \
                                border-collapse: collapse; \
                                width: 100% \
                            } \
                            td { \
                                width: 11%; \
                                border: 1px solid black; \
                                text-align: center; \
                                vertical-align: middle; \
                            } \
                        </style> \
                        <table>'
                devices = devs.getDeviceList()
                for dev in devices.keys():
                    table += '<tr>'
                    for ident, value in devices[dev].items():
                        for varname, varval in value.items():
                            table += "<td>" + str(varname) + ": " + str(varval) + "</td>"
                    table += '</tr>'
                table += "</table>"
                output = site.replace("{TABLE}", table)
                output += '</body></html>'
                self.wfile.write(output.encode())
            return

        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            dict_str = post_data.decode("UTF-8")
            data = ast.literal_eval(dict_str)
            self.send_response(301)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
            content_len = int(self.headers.get('Content-length'))
            output = ''
            output += '<html><body>'
            output += '<h2> Okay, got the data at: ' + str((time.time())) +'</h2>'
            output += '</body></html>'
            self.wfile.write(output.encode())
        except:
            self.send_error(404, "{}".format(sys.exc_info()[0]))
            print(sys.exc_info())
        devs.update(data)
        print(cfg.yml['devices'])

class Devices():
    devlist = {}
    
    def addDevice(self, data):
        self.MyName = data['name']
        self.devlist[self.MyName] = {}
        self.devlist[self.MyName]['info'] = {}
        self.devlist[self.MyName]['info'] = data
        self.devlist[self.MyName]['stat'] = {
            'online': True,
            'cnt': 1,
            'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.devlist[self.MyName]['__services__'] = {
            'service': self.Service(self.devlist[self.MyName])
        }
        #cfg.Dstore.append(self.MyName, 'with_RRD_and_CONF')
        dataset = {}
        dataset[data['name']] = data
        ds.handle_DataSet(dataset)
        self.devlist[self.MyName]['__services__']['service'].MyThread.start()

    def getDeviceList(self):
        liste = {}
        for key in self.devlist.keys():
            liste[key] = {}
            liste[key]['info'] = self.devlist[key]['info']
            liste[key]['stat'] = self.devlist[key]['stat']
        return dict(sorted(liste.items(), key=lambda item: item[0]))
        #return liste
    def update(self, data):
        try:
            self.devlist[data['name']]['__services__']['service'].Supdate(data)
        except Exception as err:
            logger.info(f'new device: {err} -> generating')
            print (f'new device: {err} -> generating')
            self.addDevice(data)


    class Service():
        def __init__ (self, list):
            logger.info('Device Service started')
            self.MyList = list
            self.MyName = list['info']['name']
            self.MyThread = threading.Thread(target=self._monitoring_thread, daemon=True)

        def _monitoring_thread(self):
            logger.info('Device monitoring started')
            while True:
                self.MyList['stat']['online'] = ds.pick(self.MyName, 'Commons', 'Active')
                time.sleep(1)
        
        def Supdate(self, data):
            self.MyList['stat']['online'] = True
            self.MyList['stat']['cnt'] += 1    
            self.MyList['stat']['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.MyList['info'] = data
            dataset = {}
            dataset[data['name']] = data
            ds.handle_DataSet(dataset)



devs = Devices()

def main():
    cfg.init()
    logger.info('---------- starting ESPWeb - server ----------') 
    ServerName = cfg.yml['Communication']['ServerName']
    ServerPort = cfg.yml['Communication']['ServerPort']
    
    try:
        server = HTTPServer((ServerName, ServerPort), webserverHandler)
        print('Server started on http://%s:%s' % (ServerName, ServerPort))
        logger.info('Server started on http://%s:%s' % (ServerName, ServerPort))
        server.serve_forever()

    except KeyboardInterrupt:
        print(' ^C entered stopping web server...')
        server.socket.close()


if __name__ == '__main__':
    main()