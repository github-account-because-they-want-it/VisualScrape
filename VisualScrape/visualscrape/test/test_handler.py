'''
Created on Jun 6, 2014
@author: Mohammed Hamdy
'''
from visualscrape.lib.signal import SpiderClosed
from visualscrape.lib.event_handler import IEventHandler
from threading import Timer

class Handler(IEventHandler):
  def __init__(self):
    self.event_queue = None
    self.data_queue = None
    self.timer = Timer(30, self.check_queues)
    self.timer.start()
    
  def set_event_queue(self, queue):
    self.event_queue = queue
    
  def set_data_queue(self, queue):
    self.data_queue = queue
    
  def set_engine(self, engine):
    pass
    
  def check_queues(self):
    finished = False
    while not self.event_queue.empty():
      event = self.event_queue.get(block=False, timeout=0)
      if isinstance(event, SpiderClosed):
        finished = True
      print "Event Queue: %s" % event
    while not self.data_queue.empty():
      print "Data Queue: %s" % self.data_queue.get(block=False, timeout=0)
    if not finished: Timer(15, self.check_queues).start()