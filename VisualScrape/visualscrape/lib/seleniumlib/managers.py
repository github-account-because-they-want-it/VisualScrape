'''
Created on Nov 21, 2014
@author: Mohammed Hamdy
'''

from threading import Thread
from visualscrape.lib.commonspider.managers import BaseManager
from .crawlers import SeleniumProductCrawler, SeleniumSinglePageCrawler, SeleniumPageListCrawler
from visualscrape.lib.data import SpiderConfigManager
from visualscrape.config.util import get_url_generator_for

class SeleniumBaseManager(BaseManager):
  
  def __init__(self, spidersInfo=[]):
    self.spiders_info = spidersInfo
    self.crawler_id_to_config_map = {}
    for (spid, sp_info) in enumerate(spidersInfo):
      # start ids at 100 for selenium to make it's ids distinct from scrapy. 
      # TODO: read the start _id from settings
      self.config_spider(spid, sp_info)
      
  def config_spider(self, spid, sp_info):
    crawler = self.createSpider(sp_info, spid + 100)
    crawl_thread = Thread(target=crawler.start, name="SeleniumThread#{0}".format(spid + 1))
    self.crawler_id_to_config_map[spid] = {"info":sp_info, "thread":crawl_thread, "spider":crawler}
      
  def start_all(self):
    for crawl_config in self.crawler_id_to_config_map.values(): 
      crawl_thread = crawl_config["thread"]
      crawl_thread.start()
  
  def stop_spider(self, spiderID, keepState):
    if not spiderID in self.crawler_id_to_config_map:
      return
    else:
      config_to_stop = self.crawler_id_to_config_map[spiderID]
      spider_to_stop = config_to_stop["spider"]
      spider_to_stop.terminate(keepState)    # because there's no thread termination
      
  def restart_spider(self, spiderID, keepState=True):
    if not spiderID in self.crawler_id_to_config_map:
      return
    self.stop_spider(spiderID, keepState)
    prev_config = self.crawler_id_to_config_map.pop(spiderID)
    prev_info = prev_config["info"]
    self.config_spider(spiderID, prev_info)
    self.crawler_id_to_config_map[spiderID]["thread"].start()
    
  def temp_pause_spider(self, spiderID):
    if self.spider_belongs(spiderID):
      spider_to_pause = self.crawler_id_to_config_map[spiderID]["spider"]
      spider_to_pause.data_handler.temp_pause() # avoid adding temp_pause method to the spider
      
  def temp_resume_spider(self, spiderID):
    if self.spider_belongs(spiderID):
      spider_to_resume = self.crawler_id_to_config_map[spiderID]
      spider_to_resume.data_handler.temp_resume()
      
  def spider_belongs(self, spiderID):
    return spiderID in self.crawler_id_to_config_map
  
  @classmethod
  def resume_spider(cls, spiderName):
    # the spider is resumed by it's name because this is what's on disk
    if SpiderConfigManager.is_selenium_spider(spiderName):
      manager = cls.getInstance() 
      if len(manager.crawler_id_to_config_map):
        spid = max(manager.crawler_id_to_config_map.keys()) + 1 # the new spider id
      else:
        spid = 0
      manager.config_spider(spid, sp_info=None)
      spider_config = manager.crawler_id_to_config_map[spid]
      spider_config["thread"].start()
      

  def createSpider(self, spid, spInfo):
    # to be reimplemented by subclasses
    pass

class SeleniumProductCrawlerManager(SeleniumBaseManager):      

  def createSpider(self, spid, spInfo):
    spider_path = spInfo.spider_path
    spider = SeleniumProductCrawler(spider_path, spid, spInfo.spider_name,
                                    handler=spInfo.handler)
    return spider
  
class SeleniumSinglePageCrawlerManager(SeleniumBaseManager):
  
  def createSpider(self, spid, spInfo):
    spider_path = spInfo.spider_path
    main_page = spider_path[-1]
    spider = SeleniumSinglePageCrawler(spider_path[0], main_page.item_selector,
                spid, spInfo.spider_name, handler=spInfo.handler)
    return spider
  
class SeleniumPageListCrawlerManager(SeleniumBaseManager):
  
  def createSpider(self, spid, spInfo):
    spider_path = spInfo.spider_path
    main_page = spider_path[-1]
    site_url = spider_path[0]
    url_generator = get_url_generator_for(site_url)
    spider = SeleniumPageListCrawler(url_generator, main_page.item_selector,
                spid, spInfo.spider_name, handler=spInfo.handler)
    return spider