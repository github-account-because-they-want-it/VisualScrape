'''
Created on Jun 5, 2014
@author: Mohammed Hamdy
'''
from multiprocessing import Queue
import abc
from visualscrape.lib.pipeline_handler import PipelineHandler
from visualscrape.lib.signal import *


class IEventHandler(object):
  """An abstract interface to which all spider handlers should conform"""
  __metaclass__ = abc.ABCMeta
  
  @abc.abstractproperty
  def stop_spider_signal(self):
    raise NotImplemented
  
  @abc.abstractmethod
  def set_event_queue(self, queue):
    raise NotImplemented
  
  @abc.abstractmethod
  def set_data_queue(self, queue):
    raise NotImplemented
  
class EventConfigurator(object):
  """A class that configures event handlers for spiders. It should
     be inherited by them"""
    
  def __init__(self, spiderInfo, *args, **kwargs):
    self.event_handler = EventHandler(self)
    self.event_handler.register_handler(spiderInfo.handler)
    
    
class EventHandler(object):
  """Currently it supports only one handler per instance of EventHandler"""
  def __init__(self, spiderInstance):
    from visualscrape.lib.scrapylib.scrapy_crawl import ScrapyCrawler # solves a circular import between this module and scrapy_crawl
    self.signals_to_handlers_map = {}
    self.spider = spiderInstance # needed for the pipeline and also to skip the pipeline for scrapy spiders
    if isinstance(self.spider, ScrapyCrawler):
      self.run_pipeline = False
    else:
      self.pipeline_handler = PipelineHandler(self.spider)
      self.run_pipeline = True
    
  def register_handler(self, handler):
    self.event_queue = Queue()
    self.data_queue = Queue()
    handler.set_event_queue(self.event_queue)
    handler.set_data_queue(self.data_queue)
    
  def emit(self, signal, **kwargs):
    """The callers are usually either the engine or the spider.
    """
    if isinstance(signal, ItemScraped):
      if self.run_pipeline:
        item = self.pipeline_handler.run_pipeline(kwargs.get("item"))
      else: item = kwargs.get("item") 
      if item: 
        # convert the item to a dictionary so python can serialize it and send it along the queue. This might cause future problems though
        item = dict(item) # or _values. but that's implementation
        self.data_queue.put(item)
    else: self.event_queue.put(signal)