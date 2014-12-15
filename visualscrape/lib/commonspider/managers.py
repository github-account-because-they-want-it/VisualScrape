'''
Created on Nov 21, 2014
@author: Mohammed Hamdy
'''

from visualscrape import settings

class BaseManager(object):
  
    
  def start_all(self):
    pass
  
  def stop_spider(self, spid, keepState):
    pass
  
  def temp_pause_spider(self, spid):
    pass
  
  def temp_resume_spider(self, spid):
    pass
  
  @classmethod
  def resume_spider(cls, spiderName):
    """This is a class method because I may not have an instance at the
       typical time this method will be called, which is before any crawling
       has been started"""
    pass
  
  def restart_spider(self, spid, keepState):
    pass
  
