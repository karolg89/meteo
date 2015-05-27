'''
Created on 26 kwi 2015

@author: fxk
'''

import threading
import urllib,urllib2

class CBAUpdater(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.semaphore_killed = False

    def update(self,dataFromHardware):
        data = {
                }
        
        data['dt'] = dataFromHardware['time']
        data['ws'] = dataFromHardware['wspeedAVG']
        data['wd'] = dataFromHardware['wdir']
        data['wds'] = dataFromHardware['wdirSTR']

        url_values = urllib.urlencode(data)
        url = 'http://stacjameteo.cba.pl/insertcba.php'
        full_url = url + '?' + url_values
        try:
            data = urllib2.urlopen(full_url,timeout=5)
        except:
            print "err updating db via URLLIB/php"
    
    def exit(self, *args, **kwargs):
        print "Killing  therad: " + str(self)
        self.semaphore_killed = True   

    def run(self):
        while(self.semaphore_killed==False):
            data = self.queue.get()
            self.update(data)
            
if __name__ == '__main__':
    pass