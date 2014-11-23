'''
Created on Nov 21, 2014
@author: Mohammed Hamdy
'''

class BaseManager(object):
  """A special singleton in that it doesn't know the subclass
    in advance.
    Managers are singletons"""
  
  _instance = None
  
  @classmethod
  def getInstance(cls, *args, **kwargs):
    if not cls._instance:
      cls._instance = cls(*args, **kwargs)
    return cls._instance
    
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
  
