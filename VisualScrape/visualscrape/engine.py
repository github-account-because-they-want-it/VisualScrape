'''
Created on May 25, 2014
@author: Mohammed Hamdy
'''
from visualscrape.config import settings
from visualscrape.lib import Signal
from visualscrape.lib.event_handler import IEventHandler

class CrawlEngine(object):
  """This is where a client application interfaces with the API"""
  def __init__(self):
    self.spiders_info = [] # multi-spider support
    self.managers = []
    self.current_spider_info = None
    
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
      self.managers.append(spider_manager)
      managers_to_spinfo_map.setdefault(spider_manager, [])
      managers_to_spinfo_map[spider_manager].append(sp_info)
    
    for manager, sp_infos in managers_to_spinfo_map.items():
      manager_inst = manager(sp_infos)
      manager_inst.start_all()
    
  def register_handler(self, handler):
    # assert isinstance(handler, IEventHandler), "Handler doesn't implement required interface <IEventHandler>"
    handler.stop_spider_signal.connect(self.stop_spider)
    self.current_spider_info.set_handler(handler)
    return self
  
  def stop_spider(self, spiderID):
    """Called by the handlers to stop the spiders if they wish"""
    for manager in self.managers:
      manager.stop_spider(spiderID)
  
      
class SpiderInfo(object):
  """Container for spider information collected by the engine"""
  
  DEFAULT_NAME = "TestSpider"
  def __init__(self, spiderPath=None, spiderName="TestSpider"):
    self.spider_path = spiderPath
    self.spider_name = spiderName
    self.handler = None
    
  def set_path(self, path):
    self.spider_path = path
    
  def get_start_url(self):
    return self.spider_path[0]
    
  def set_handler(self, handler):
    self.handler = handler
    
  def __str__(self):
    return "<SpiderInfo {0}>".format(self.spider_name)