'''
Created on May 29, 2014
@author: Mohammed Hamdy
'''

from twisted.internet import reactor
import os
from scrapy.crawler import Crawler
from scrapy import log, signals
from scrapy.utils.project import get_project_settings
from visualscrape.lib.scrapy import ScrapyCrawler


class ScrapyManager(object):
  """Takes the spider information and handles launching and 
     termination of the spider(s)"""
  def __init__(self, spidersInfo=[]):
    # set the settings directory. Use scrapy settings manager
    os.environ["SCRAPY_SETTINGS_MODULE"] = "visualscrape.config.settings"
    self.spiders_info = spidersInfo
    self.closed_spiders = 0
    
  def start_all(self):
    """Currently, all the spiders are run within the same process"""
    for (id, sp_info) in enumerate(self.spiders_info):
      spider = ScrapyCrawler(sp_info.spider_path, sp_info.spider_name, id)
      spider.registerHandlers(sp_info.signals_handlers_map)
      settings = get_project_settings()
      crawler = Crawler(settings)
      # connect each spider's closed signal to self. When all spiders done, stop the reactor
      crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)
      crawler.configure()
      crawler.crawl(spider)
      crawler.start()
    log.start()
    reactor.run()
    
  def spider_closed(self):
    self.closed_spiders += 1
    if self.closed_spiders == len(self.spiders_info):
      reactor.stop()