'''
Created on Jun 5, 2014
@author: Mohammed Hamdy
'''
from multiprocessing import Queue
from visualscrape.lib.pipeline_handler import PipelineHandler
from visualscrape.lib.signal import *
from visualscrape.lib.scrapylib.scrapy_crawl import ScrapyCrawler

class EventHandler(object):
  
  def __init__(self):
    self.signals_to_handlers_map = {}
    self.spider = None # needed for the pipeline and also to skip the pipeline for scrapy spiders
    self.pipeline_handler = None
    
  def register_event_handler(self, handler):
    self.event_queue = Queue()
    handler(self.event_queue)
    
  def register_data_handler(self, handler):
    self.data_queue = Queue()
    handler(self.data_queue)
    
  def set_spider(self, spider):
    self.spider = spider
    if isinstance(spider, ScrapyCrawler):
      self.run_pipeline = False
    else:
      self.pipeline_handler = PipelineHandler(spider)
      self.run_pipeline = True
    
  def emit(self, signal, **kwargs):
    """The callers are usually either the engine or the spider.
    """
    if isinstance(signal, ItemScraped):
      if self.run_pipeline:
        item = self.pipeline_handler.run_pipeline(kwargs.get("item"))
      else: item = kwargs.get("item") 
      if item: self.data_queue.put(item)
    else: self.event_queue.put(signal)