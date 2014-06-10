'''
Created on May 25, 2014
@author: Mohammed Hamdy
'''
from visualscrape.config import settings
from visualscrape.lib import Signal
from visualscrape.lib.event_handler import EventHandler

class CrawlEngine(object):
  """This is where a client application interfaces with the API"""
  def __init__(self):
    self.spiders_info = [] # multi-spider support
    self.current_spider_info = None
    self.event_handler = EventHandler()
    
  def add_spider(self, spiderName="TestSpider"):
    self.current_spider_info = SpiderInfo(spiderName=spiderName)
    self.spiders_info.append(self.current_spider_info)
    return self
  
  def set_path(self, path):
    self.current_spider_info.set_path(path)
    return self
    
  def start(self):
    """
    Group required spider(s) info by their preferred scraper, get each scraper's 
    manager and let the manager handle the rest 
    """
    managers_to_spinfo_map = {}
    for sp_info in self.spiders_info:
      spider_start_url = sp_info.get_start_url()
      scraper_cls = settings.get_preferred_scraper_for(spider_start_url)
      spider_manager = scraper_cls.get_manager()
      managers_to_spinfo_map.setdefault(spider_manager, [])
      managers_to_spinfo_map[spider_manager].append(sp_info)
    
    for manager, sp_infos in managers_to_spinfo_map.items():
      manager_inst = manager(sp_infos)
      manager_inst.start_all()
    
  def register_handlers(self, eventHandler=None, dataHandler=None):
    """The handlers are both functions that accept a single argument, a Queue.
       Look at the EventHandler class"""
    self.event_handler.register_event_handler(eventHandler)
    self.event_handler.register_data_handler(dataHandler)
    self.current_spider_info.set_event_handler(self.event_handler)
    return self
      
      
class SpiderInfo(object):
  """Container for spider information collected by the engine"""
  
  DEFAULT_NAME = "TestSpider"
  def __init__(self, spiderPath=None, spiderName="TestSpider"):
    self.spider_path = spiderPath
    self.spider_name = spiderName
    self.event_handler = None
    
  def set_path(self, path):
    self.spider_path = path
    
  def get_start_url(self):
    return self.spider_path[0]
    
  def set_event_handler(self, eventHandler):
    self.event_handler = eventHandler
    
  def __str__(self):
    return "<SpiderInfo {0}>".format(self.spider_name)