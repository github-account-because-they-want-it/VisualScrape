'''
Created on May 25, 2014
@author: Mohammed Hamdy
'''
import os
from scrapy.utils.misc import load_object
from lib.path import SpiderPath
from visualscrape.config import settings
from visualscrape.lib import Signal

class CrawlEngine(object):
  """This is where a client application interfaces with the API"""
  def __init__(self):
    self.spider_switch_handlers = [] #this is recommended to be connected to, otherwise, you won't know of it
    self.spiders_info = [] # multi-spider support
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
    Get the spider class that has the turn to run, get it's manager and
    let the manager handle the rest 
    """
    spider_class_str = settings.nextSetting(settings.SCRAPER_CLASSES)
    Spider = load_object(spider_class_str)
    #instantiate it
    SpiderManager = Spider.get_manager()
    sm = SpiderManager(self.spiders_info)
    sm.start_all()
    
  def register_handler(self, signalID, callback):
    """the handlers should conform to their interface defined in 
       http://doc.scrapy.org/en/latest/topics/signals.html#module-scrapy.signals"""
    if signalID == Signal.SPIDER_SWITCHED:
      self.spider_switch_handlers.append(callback)
    else:
      self.current_spider_info.add_handler(signalID, callback)
    
    return self
      
      
class SpiderInfo(object):
  """Container for spider information collected by the engine"""
  
  DEFAULT_NAME = "TestSpider"
  def __init__(self, spiderPath=None, spiderName="TestSpider", signalsToHandlersMap={}):
    self.spider_path = spiderPath
    self.spider_name = spiderName
    self.signals_handlers_map = signalsToHandlersMap
    
  def set_path(self, path):
    self.spider_path = path
    
  def add_handler(self, signalID, callback):
    self.signals_handlers_map.setdefault(signalID, [])
    self.signals_handlers_map[signalID].append(callback)
    
  def __str__(self):
    return "<SpiderInfo {0}>".format(self.spider_name)