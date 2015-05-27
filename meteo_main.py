'''
Created on 25 kwi 2015

@author: fxk
'''
import meteo_hw, updatecba
from config import config as cfg

import Queue
import threading
import time
import logging



class cDataDipenser(threading.Thread):
    def __init__(self, queue, queues):
        threading.Thread.__init__(self)
        self.queues = queues
        self.queue = queue
        self.semaphore_killed = False

    def exit(self, *args, **kwargs):
        print "Killing  therad: " + str(self)
        self.semaphore_killed = True

    def run(self):
        while(self.semaphore_killed==False):
            data = self.queue.get()
            for q in self.queues:
                q.put(data)
            
            pass
            
    
def mainTask():

    datafromhwQ = Queue.Queue() # Queue with data received from device
    updatecbaQ = Queue.Queue() 
    
   
    dataDispenser = cDataDipenser(datafromhwQ, [updatecbaQ])
    device = meteo_hw.MeteoHW(cfg['SERIALPORT'], datafromhwQ)
    cbaUpdater = updatecba.CBAUpdater(updatecbaQ)
    device.start()
    cbaUpdater.start()
    dataDispenser.start()

    try:
        while(True):
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        cbaUpdater.exit()
        device.exit()
        dataDispenser.exit()


if __name__ == '__main__':
    mainTask()
