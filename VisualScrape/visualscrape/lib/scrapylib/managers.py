'''
Created on Nov 20, 2014
@author: Mohammed Hamdy
'''

from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import signals
from scrapy.utils.project import get_project_settings
from visualscrape import settings
from visualscrape.lib.data import SpiderConfigManager
from visualscrape.engine import SpiderInfo
from .crawlers import (ScrapyProductCrawler, ScrapyJSBitch, ScrapySinglePageCrawler, 
  ScrapyPageListCrawler)
from visualscrape.lib.commonspider.managers import BaseManager
from visualscrape.lib.signal import SpiderClosed
from visualscrape.config.util import get_url_generator_for,\
  get_filter_predicate_for


class ScrapyBaseManager(BaseManager):
  
  """Takes the spider information and handles launching and 
     termination of the spider(s)"""
  def __init__(self, spidersInfo=[]):
    super(ScrapyBaseManager, self).__init__()
    self.should_control_reactor = settings.getbool("SCRAPY_MANAGE_REACTOR", True)
    # set the settings directory. Use scrapy settings manager
    self.spiders_info = spidersInfo
    self.closed_spiders = 0
    self._ids_to_crawlers_map = {}
    
  def start_all(self):
    self.run_spiders()
    
  def run_spiders(self):
    """Currently, all the spiders are run within the same process"""
    for (spid, sp_info) in enumerate(self.spiders_info):
      spider = self.createSpider(spid, sp_info)
      self.config_spider(spid, spider)
    if self.should_control_reactor:
      reactor.run()
  
  def config_spider(self, spid, spider):
    """The boring startup routine"""
    proj_settings = get_project_settings()
    crawler = Crawler(proj_settings)
    self._ids_to_crawlers_map[spid] = {"spider":spider, "crawler":crawler}
    # connect each spider's closed signal to self. When all spiders done, stop the reactor
    crawler.signals.connect(self.spider_closed, signal=signals.spider_closed) # i do not really now if that is appended or overwritten
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()  
    
  def spider_closed(self, spider):
    self.closed_spiders += 1
    if spider.event_handler: spider.event_handler.emit(SpiderClosed(spider._id))
    if self.should_control_reactor and self.closed_spiders == len(self.spiders_info):
      reactor.stop()

  def spider_belongs(self, spiderID):
    return spiderID in self._ids_to_crawlers_map
  
    
  def resume_all(self):
    """This method doesn't assume all spider infos are available, and it
       runs them from configuration instead"""
    for spider_crawler in self._ids_to_crawlers_map.values():
      crawler = spider_crawler["crawler"]
      crawler.start()
    reactor.run()  
  
  def stop_spider(self, spiderID, keepState=True):
    if spiderID in self._ids_to_crawlers_map: # the _id may not belong to a scrapy spider, so check it 
      self._ids_to_crawlers_map[spiderID]["crawler"].stop() # does this emit the spider_closed signal?
      if not keepState:
        self._ids_to_crawlers_map[spiderID]["spider"].stop(keepState)
  
  def temp_pause_spider(self, spiderID):
    if spiderID in self._ids_to_crawlers_map:  
      self._ids_to_crawlers_map[spiderID]["spider"].temp_pause()
      
  def temp_resume_spider(self, spiderID):
    if spiderID in self._ids_to_crawlers_map:  
      self._ids_to_crawlers_map[spiderID]["spider"].temp_resume()

  def restart_spider(self, spiderID, keepState=True):
    # stop all spiders
    if spiderID in self._ids_to_crawlers_map:  
      for spider_id in self._ids_to_crawlers_map:
        if spider_id == spiderID: # use the keepState only for the required spider
          self.stop_spider(spider_id, keepState)
        else: # every other spider must keep state
          self.stop_spider(spider_id, keepState=True)
      # after all spiders stopped (hopefully, the reactor too), reconfigure them all
      for spider_id in self._ids_to_crawlers_map:
        self.config_spider(spider_id, self._ids_to_crawlers_map[spiderID]["spider"]) # reconfigure the spider again
      reactor.run()
    
  def pause_spider(self, spiderID):
    """Call the spider pause() method and stop it while keeping state"""
    if self.spider_belongs(spiderID):
      info_to_pause = self._ids_to_crawlers_map[spiderID]["spider"]
      spider_to_pause = info_to_pause["spider"]
      spider_to_pause.pause()
      crawler_to_stop = info_to_pause["crawler"]
      crawler_to_stop.stop()
  
  @classmethod    
  def resume_spider(cls, spiderName):
    """resume a spider from disk"""
    if SpiderConfigManager.is_scrapy_spider(spiderName):
      # stop all the current spiders and add this one to the mix
      manager = cls.getInstance()
      for spider_id in manager._ids_to_crawlers_map:
        manager.stop_spider(spider_id, keepState=True)
      if len(manager._ids_to_crawlers_map):
        next_id = max(manager._ids_to_crawlers_map.keys()) + 1
      else:
        next_id = 1
      manager.config_spider(next_id, manager.createSpider(next_id, None))
      manager.resume_all()
    
  def createSpider(self, spid, spInfo=None):
    # reimplement this in subclasses to pass spider __init__ arguments
    pass
    
class ScrapyProductCrawlerManager(ScrapyBaseManager):
 
  def createSpider(self, spid, spInfo=None):
    # None for spInfo means a resume
    spider = ScrapyProductCrawler(spInfo, spid)
    return spider
  
  def _createJSSpider(self, spid, spInfo, watcher, count):
    spider = ScrapyJSBitch(watcher, spInfo, spid, count)
    return spider
    
  @classmethod
  def run_jstest(cls, spiderPath, itemWatcher, itemCount=20):
    sp_info = SpiderInfo(spiderPath)
    manager = cls([sp_info])
    spider = manager._createJSSpider(0, sp_info, itemWatcher, itemCount)
    manager.config_spider(0, spider)
    manager.start_all()
    
class ScrapySinglePageCrawlerManager(ScrapyBaseManager):
  
  def createSpider(self, spid, spInfo=None):
    main_page = spInfo.spider_path[-1]
    url = spInfo.spider_path[0]
    item_selector = main_page.item_selector
    spider = ScrapySinglePageCrawler(url, item_selector, spid, spInfo.spider_name,
                                     handler=spInfo.handler)
    return spider
  
class ScrapyPageListCrawlerManager(ScrapyBaseManager):
  
  def createSpider(self, spid, spInfo=None):
    main_page = spInfo.spider_path[-1]
    item_selector = main_page.item_selector
    url_generator = get_url_generator_for(spInfo.spider_path[0])
    filter_predicate = get_filter_predicate_for(spInfo.spider_path[0])
    base_url = spInfo.spider_path[0]
    spider = ScrapyPageListCrawler(base_url, url_generator, item_selector, spid,
                  spInfo.spider_name, filterPredicate=filter_predicate, 
                  handler=spInfo.handler)
    return spider