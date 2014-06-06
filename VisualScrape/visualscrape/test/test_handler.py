'''
Created on Jun 6, 2014
@author: Mohammed Hamdy
'''
from threading import Timer

class Handler(object):
  def __init__(self):
    self.event_queue = None
    self.data_queue = None
    self.timer = Timer(30, self.check_queues)
    self.timer.start()
    
  def event_saver(self, queue):
    self.event_queue = queue
    
  def data_saver(self, queue):
    self.data_queue = queue
    
  def check_queues(self):
    while not self.event_queue.empty():
      print "Event Queue: %s" % self.event_queue.get(False)
    while not self.data_queue.empty():
      print "Data Queue: %s" % self.data_queue.get(False)