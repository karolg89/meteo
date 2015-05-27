'''
Created on 18 kwi 2015

@author: fxk
'''
import unittest

from config import config as cfg
import serial
import time
import datetime
import re
import threading
import traceback
import Queue

class MeteoHW(threading.Thread):
    def __init__(self, port, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.port = port
        self.ser = None
        self.semaphore_killed = False
        self.syncTimeOnDevice = None
        self.syncDatetime = None
        self.synced = False
    
    def connect(self):
        try:
            self.ser = serial.Serial(self.port)
        except Exception, e:
            #TODO log exception here
            self.connectTTYUSBxx()
        finally:
            if self.ser == None:
                raise Exception('Device is not connencted') 

    def connectTTYUSBxx(self):
        portTmp = None
        if isinstance( self.port, ( int, long ) ):
            portTmp = "/dev/ttyUSB" + str(self.port)

        try:
            self.ser = serial.Serial(portTmp)
            self.port = portTmp
        except Exception, e:
            #TODO log exception here
            print "error connecting port " + str(self.port)
            self.ser = None
            pass

    def reconnect(self):
        try:
            self.ser.close()
            self.connect()
        except:
            print "reconnect failed"
    
    def run(self):

        if self.ser == None:
            self.connect()

        syncPeriod = 60
        i = 0

        while(self.semaphore_killed==False):
            try:
                
                if i == 0 :
                    data = self.tryToSyncWithDev()
                    self.enqueueData(data)
                    i=syncPeriod
                i-=1

                data = self.readData()
                data = self.arrangeDataListIntoDict(data)
                data['datetime'] = self.getSynchronizedDatetime(int(data['timedDEV']))

                self.enqueueData(data)
            except Exception, e:
                print traceback.format_exc()
                time.sleep(1)
                self.reconnect()
    
    def tryToSyncWithDev(self):
        
        synced = False
        while synced==False:
            try:
                data = self.syncTimeWithDev()
                synced = True
                print "Synced"
                return data
            except Exception,e:
                synced = False
                print traceback.format_exc()

    def syncTimeWithDev(self):
        data = self.readData()
        data = self.arrangeDataListIntoDict(data)
        self.syncTimeOnDevice = int(data['timedDEV']) 
        self.syncDatetime = datetime.datetime.now() 
        return data         



    def readData(self):
        #sample line read from hardware
        #DATA FORMAT:[WIND SPEED;WIND SPEED 10S AVG;WIND DIR (ADC RAW);MEASURE TIME (MILISECONDS)]: [7.50;4.75;3369;1122000]
        l = self.ser.readline()
        l = l.split("[")
        l = l[2].split("]")

        #list with data
        datalist = l[0].split(";")
        return datalist

    def enqueueData(self,data):
        self.queue.put(data)
        print 'Data put on queue: ' + str(data)
      
    def arrangeDataListIntoDict(self,datalist):
        l = datalist
        [wdir, wdirstr] = self.convRawDatToWindDirCode(int(l[2]))

        data = {
                'wspeed' : float(l[0])/3.6, #convert kph to mps
                'wspeedAVG' : float(l[1])/3.6, #convert kph to mps
                'wdir' : wdir,
                'wdirSTR' : wdirstr,
                'time': datetime.datetime.now(),
                'timedDEV': int(l[3])
                }
        return data

    def getSynchronizedDatetime(self,timeFromDevice):
        deltaTimeMilisecond = int(timeFromDevice) - int(self.syncTimeOnDevice)
        deltaTimeSecond = deltaTimeMilisecond / 1
        return self.syncDatetime + datetime.timedelta(seconds=deltaTimeSecond)
        
        
    def correctTimeInData(self,data):
        data['datetime'] = self.getSynchronizedDatetime(int(data['timedDEV']))
        return data

    def convRawDatToWindDirCode(self, wdir):
        #Set covers raw ADC ranges for wind direction
        #read from hardware
        rawWindDirRanges = {
                    0 : [1950, 2550],
                    1 : [900, 1400],
                    2 : [0, 300],
                    3 : [300, 550],
                    4 : [550, 900],
                    5 : [1400, 1950],
                    6 : [3000, 4095],
                    7 : [2550, 3000],
                    }
        windDirCodes = {
                 0 : 'N',
                 1 : 'NE',
                 2 : 'E',
                 3 : 'SE',
                 4 : 'S',
                 5 : 'SW',
                 6 : 'W',
                 7 : 'NW'
                 }
        
        def isInRange(Xvalue, Xrange):
            if  (Xvalue < Xrange[1] and Xvalue > Xrange[0]):
                return True
            else:
                return False

        for i in range(len(rawWindDirRanges)):
            if isInRange(wdir, rawWindDirRanges[i]):
                return [i, windDirCodes[i]]
                break
            pass
        return 0

    def exit(self, *args, **kwargs):
        print "Killing  therad" + str(self)
        self.semaphore_killed = True

    
# --------------------------------------------------------#
# Tests  
# Device must be present and run
# --------------------------------------------------------#         
class TestMeteoHW(unittest.TestCase):

    def setUp(self):
        self.validPortName = "/dev/ttyUSB0"
        self.validPortNumber = 0

        self.invalidPortNumber = 9999999 
    
    def testMeteoHWCreate(self):
        hw = None
        hw = MeteoHW(None,None)
        assert hw != None, "error creating object"
         
    def testConnectNoneExistinPort(self):
        port = self.invalidPortNumber
        hw = MeteoHW(port,None)
        try:
            hw.connect()
        except Exception, e:
            print e
            pass
        assert hw.ser == None, "connected to non existin port" 
    
    def testConnectExistinPortByName(self):
        # port must be valid port name 
        port = self.validPortName
        hw = MeteoHW(port,None)
        hw.connect()
        assert hw.ser != None, "connected to non existin port" 

    def testConnectExistinPortByNumber(self):
        # port must be valid port number
        port = self.validPortNumber
        hw = MeteoHW(port,None)
        hw.connect()
        assert hw.ser != None, "connected to non existin port" 
    
    def testReconnect(self):
        # port must be valid port name 
        port = self.validPortName
        hw = MeteoHW(port,None)
        hw.connect()
        hw.reconnect()
        assert hw.ser != None, "reconnect failed" 

    def testReconnectFailure(self):
        # port must be valid port name 
        port = self.validPortName
        hw = MeteoHW(port,None)
        hw.connect()

        hw.port = self.invalidPortNumber
        hw.reconnect()
        assert hw.ser == None, "reconnect failed" 


    def testReadDataFromDevice(self):
        q = Queue.Queue()
        port = self.validPortName
        hw = MeteoHW(port,q)
        hw.connect()

        # read two lines from device
        hw.readData()
        hw.readData()

        # first line might be corrupted
        q.get()

        data = q.get()

        assert len(data) == 6, "received data have wrong length"
        assert self.receivedDataFormatTest(data), "received data have wrong format"

    def receivedDataFormatTest(self,data):
        d = data
        lst = [
            isinstance(d['wspeedAVG'], float),
            isinstance(d['wspeed'], float),
            isinstance(d['wdirSTR'], str),
            isinstance(d['wdir'], int),
            isinstance(d['timedDEV'], int),
            isinstance(d['time'], datetime.datetime)
            ]

        for l in lst:
            if l==False:
               return False

        return True

    def testThreadRun(self):
        pass

    def testThreadExit(self):
        pass


if __name__ == '__main__':
    unittest.main()
    

   