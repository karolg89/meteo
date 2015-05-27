'''
Created on 26 kwi 2015

@author: fxk
'''

import unittest
import threading
import Queue


class meteoMath(threading.Thread):
    def __init__(self, inqueue,outqueue):
        threading.Thread.__init__(self)
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.semaphore_killed = False
        self.data = []



    def exit(self, *args, **kwargs):
        print "Killing  therad: " + str(self)
        self.semaphore_killed = True   

    def run(self):
        while(self.semaphore_killed==False):
            data = self.inqueue.get()
                
            

# --------------------------------------------------------#
# Tests  
# Device must be present and run
# --------------------------------------------------------#         

class TestMeteoMath(unittest.TestCase):

    def testInit(self):
        iq = Queue.Queue()
        oq = Queue.Queue()
        mm = meteoMath(iq,oq)
        assert mm!=None, "Failed creatine object meteoMath"
    

if __name__ == '__main__':
    unittest.main()
    pass