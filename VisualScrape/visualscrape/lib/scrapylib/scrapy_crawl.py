'''
Created on May 26, 2014
@author: Mohammed Hamdy
'''
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy import signals
from threading import Thread
import urlparse, time
from visualscrape.lib.path import URL, Form
from visualscrape.lib.commonspider.base import CommonCrawler, BaseManager
from visualscrape.config import settings
from visualscrape.lib.item import InterestItem, FaviconItem
from visualscrape.lib.selector import FieldSelector
from visualscrape.lib.signal import SpiderStarted, SpiderClosed
from visualscrape.lib.event_handler import EventConfigurator
from visualscrape.lib.data import SpiderConfigManager
from scrapy.exceptions import CloseSpider
from visualscrape.engine import SpiderInfo

class ScrapyCrawler(CrawlSpider, CommonCrawler, EventConfigurator):
  """
  This spider now doesn't support multiple urls per _spider_path, something 
  like start_urls=[url1, more than 1 url...]
  """
  name = "ScrapyCrawler"
  def __init__(self, spiderInfo, spiderID, name="ScrapyCrawler", **kwargs):
    EventConfigurator.__init__(self, spiderInfo, spiderID, name, **kwargs)
    CommonCrawler.__init__(self, spiderInfo, spiderID, name, **kwargs)
    self.path_index = 0
    self.favicon_item = None
  
  def start_requests(self):
    #this might not work as per docs if it returns items. see Spiders page
    if self.event_handler: self.event_handler.emit(SpiderStarted(self._id))
    start_path = self._spider_path[0]
    if self.favicon_required: #the first item contains only the favicon
      #obtain the favicon url
      start_url = start_path if isinstance(start_path, URL) else start_path.url
      url_components = urlparse.urlparse(start_url)
      favicon_url = urlparse.urljoin(url_components.scheme + "://" + url_components.netloc, "favicon.ico")
      favicon_item = FaviconItem()
      favicon_item["image_urls"] =  [favicon_url]
      favicon_item["_id"] =  self._id
      self.favicon_item = favicon_item #assign it to be returned later. can't return here
    return self._take_step()
  
  def parse_intermediate(self, response):
    """This should continue until there's only one item in self._spider_path which is
       MainPage object"""
    return self._take_step()
    
  def parse_item_pages(self, response):
    """Gets the pages of items from a MainPage"""
    main_page = self._spider_path[-1]
    similar_pages_selector = main_page.similar_pages_selector
    similar_pages_restrict = main_page.similar_pages_restrict
    # i think yield from syntax would've helped me refactor the next section. But it's only in 3.3
    if similar_pages_selector:
      similar_nav = self._links_from_selector(response, similar_pages_selector, similar_pages_restrict)
      for nav in similar_nav: yield Request(nav, dont_filter=False, callback=self.parse_item_pages) # the extracted links can well have their crawled friends
      
    item_page_selector = self._spider_path[-1].item_page_selector
    item_pages = self._links_from_selector(response, item_page_selector, restrict=None)
    for request in [Request(page, callback=self.parse_items) for page in item_pages]:
      yield request
    
  def parse_items(self, response):
    if self.favicon_item:
      yield self.favicon_item
      self.favicon_item = None
    # check temporary pausing
    while self._temp_paused:
      time.sleep(self._sleep_timeout)
      if self._stopped: break
    if self._stopped: raise CloseSpider()
    self._visited_urls_before_shutdown.add(response.url)
    item_selector = self._spider_path[-1].item_selector
    selectors_actions = item_selector.selectors_actions
    item_info = self.get_item_info(selectors_actions, response)
    item = InterestItem(item_info["keys"])
    item_loader = self.item_loader(item, response=response, response_ctx=response) #pass the response to i/o processors
    item = self.fill_item_loader(item_loader, item_info, response, item_selector.post_process_info)
    yield item
    
  def _take_step(self):
    step = self._spider_path.pop(0)
    next_step = self._spider_path[0]
    callback = self.parse_intermediate if isinstance(next_step, (URL, Form)) \
       else self.parse_item_pages
    if isinstance(step, URL):
      next_url = step
      request = Request(next_url, callback=callback)
    elif isinstance(step, Form):
      next_url = step.url
      form_data = {elem.name:elem.value for elem in step.data}
      request = FormRequest(next_url, form_data, 
                          callback=callback)
      
    return [request]
  
  def _links_from_selector(self, response, selector, restrict=None):
    if selector.type == FieldSelector.REGEX:
      # use rules to do manual link extraction, since scrapy seems not to do it unless the rules are a class attribute
      similar_extractor = SgmlLinkExtractor(allow=(selector,),
                         restrict_xpaths=(restrict,) if restrict else ())
      links = [link.url for link in similar_extractor.extract_links(response)]
    else:
      sel = Selector(response)
      if selector.type == FieldSelector.CSS:
        if not "::href" in selector: selector = selector + "::attr(href)"
        links = sel.css(selector).extract()
      elif selector.type == FieldSelector.XPATH:
        if not "@href" in selector: selector = selector + "/@href"
        links = sel.xpath(selector).extract()
      # canonicalize ...
      links = [URL(link).canonicalize(response.url) for link in links]
      links = [link for link in links if link not in self._visited_urls_before_shutdown]
    return links  
  
  @staticmethod      
  def get_manager():
    return ScrapyManager
  
class ScrapyJSBitch(ScrapyCrawler):
  """A subclass that collects for only some items to test a site's JS requirements"""
  
  def __init__(self, watcher, spiderInfo, spiderID, itemCount=20, name="ScrapyCrawler", **kwargs):
    """The watcher is sent each item collected"""
    super(ScrapyJSBitch, self).__init__(spiderInfo, spiderID, name, **kwargs)
    self._item_count = itemCount
    self._scraped_count = 0
    self._item_watcher = watcher
    self.crawler().signals.connect(self._item_watcher.spider_done, signal=signals.spider_closed)
    
  def parse_items(self, response):
    item = super(ScrapyJSBitch, self).parse_items(response)
    self._item_watcher.take_item(item)
    self._scraped_count += 1
    if self._scraped_count == self._item_count:
      raise CloseSpider()
    else:
      yield item
# ------------------------------------------------------------------------- #
#two modules brought together to solve a circular import

from twisted.internet import reactor
import os
from scrapy.crawler import Crawler
from scrapy import log
from scrapy.utils.project import get_project_settings


class ScrapyManager(BaseManager):
  """Takes the spider information and handles launching and 
     termination of the spider(s)"""
  def __init__(self, spidersInfo=[]):
    # set the settings directory. Use scrapy settings manager
    os.environ["SCRAPY_SETTINGS_MODULE"] = "visualscrape.settings"
    self.spiders_info = spidersInfo
    self.closed_spiders = 0
    self._ids_to_crawlers_map = {} # id : {spider, crawler}
    self._crawl_thread = Thread(target=self.run_spiders)
    
  def start_all(self):
    self._crawl_thread.start() # it seems that twisted has done a good job releasing the GIL. This remains responsive
    
  def run_spiders(self):
    """Currently, all the spiders are run within the same process"""
    log.start(loglevel=log.DEBUG)
    for (spid, sp_info) in enumerate(self.spiders_info):
      spider = self._createSpider(spid, sp_info)
      self.config_spider(spid, spider)
    reactor.run()
  
  def _createSpider(self, spid, spInfo=None):
    # None for spInfo means a resume
    spider = ScrapyCrawler(spInfo, spid)
    return spider
  
  def _createJSSpider(self, spid, spInfo, watcher, count):
    spider = ScrapyJSBitch(watcher, spInfo, spid, count)
    return spider
  
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
  
  def spider_closed(self, spider):
    self.closed_spiders += 1
    if spider.event_handler: spider.event_handler.emit(SpiderClosed(spider._id))
    if self.closed_spiders == len(self.spiders_info):
      reactor.stop()

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
      manager.config_spider(next_id, manager._createSpider(next_id, None))
      manager.resume_all()
    
  def spider_belongs(self, spiderID):
    return spiderID in self._ids_to_crawlers_map
  
  @classmethod
  def run_jstest(cls, spiderPath, itemWatcher, itemCount=20):
    sp_info = SpiderInfo(spiderPath)
    manager = cls([sp_info])
    spider = manager._createJSSpider(0, sp_info, itemWatcher, itemCount)
    manager.config_spider(0, spider)
    manager.start_all()