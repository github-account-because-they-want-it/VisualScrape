'''
Created on May 26, 2014
@author: Mohammed Hamdy
'''
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from multiprocessing import Process
import urlparse
from visualscrape.lib.path import URL, Form
from visualscrape.lib.item import InterestItem, FaviconItem
from visualscrape.lib.scrapylib.itemloader import DefaultItemLoader
from visualscrape.lib.selector import FieldSelector
from visualscrape.lib.signal import *

class ScrapyCrawler(CrawlSpider):
  """
  This spider now doesn't support multiple urls per path, something 
  like start_urls=[url1, more than 1 url...]
  """
  name = "ScrapyCrawler"
  def __init__(self, spiderPath, spiderID, name="ScrapyCrawler", *args, **kwargs):
    super(ScrapyCrawler, self).__init__()
    self.name = name
    self.path = spiderPath
    self.id = spiderID # this is a public property
    self.path_index = 0
    self.favicon_required = kwargs.get("downloadFavicon", True) #the favicon for the scraped site will be added to the first item
    self.event_handler = kwargs.get("eventHandler", None)
    self.event_handler.set_spider(self)
    self.favicon_item = None
  
  def start_requests(self):
    #this might not work as per docs if it returns items. see Spiders page
    self.event_handler.emit(SpiderStarted(self.id))
    start_path = self.path.pop(0)
    # determine the callback based on next step
    callback = self.parse_intermediate if type(self.path[0]) == URL else self.parse_item_pages
    if type(start_path) == URL:
      start_url = start_path
      request = Request(start_path, callback=callback)
    elif type(start_path) == Form:
      start_url = start_path.url
      form_data = {elem.name:elem._value for elem in start_url.data} # text and select elements are the same to scrapy
      request = FormRequest(start_path.url, form_data, 
                          callback=callback)
    
    if self.favicon_required: #the first item contains only the favicon
      #obtain the favicon url
      url_components = urlparse.urlparse(start_url)
      favicon_url = urlparse.urljoin(url_components.scheme + "://" + url_components.netloc, "favicon.ico")
      favicon_item = FaviconItem()
      favicon_item["image_urls"] =  [favicon_url]
      favicon_item["id"] =  self.id
      self.favicon_item = favicon_item #assign it to be returned later. can't return here
    print request
    return [request]
  
  def parse_intermediate(self, response):
    """This should continue until there's only one item in self.path which is
       MainPage object"""
    next_step = self.path.pop(0)
    callback = self.parse_intermediate if type(next_step) == URL else self.parse_item_pages
    if type(next_step) == URL:
      next_url = next_step
      request = Request(next_url, callback=callback)
    elif type(next_step) == Form:
      next_url = next_step.url
      form_data = {elem.name:elem._value for elem in next_url.data}
      request = FormRequest(next_url, form_data, 
                          callback=callback)
      
    return [request]
    
  def parse_item_pages(self, response):
    sel = Selector(response)
    # use rules to do manual link extraction, since scrapy seems not to do it unless the rules are a class attribute
    main_page = self.path[-1]
    similar_extractor = SgmlLinkExtractor(allow=(main_page.similar_pages_selector,) if main_page.similar_pages_selector else (),
                       restrict_xpaths=(main_page.similar_pages_restrict,) if main_page.similar_pages_restrict else ())
    similar_nav = [link.url for link in similar_extractor.extract_links(response)]
    for similar_url in similar_nav:
      yield Request(similar_url, dont_filter=False, callback=self.parse_item_pages) # the extracted links can well have their crawled friends
    page_selectors = self.path[-1].item_page_selector
    for item_pages_selector in page_selectors.selectors:
      if page_selectors.type == FieldSelector.XPATH:
        item_pages = sel.xpath(item_pages_selector)
      elif page_selectors.type == FieldSelector.CSS:
        item_pages = sel.css(item_pages_selector)
      for request in [Request(page, callback=self.parse_items) for page in item_pages.extract()]:
        yield request
    
  def parse_items(self, response):
    if self.favicon_item:
      yield self.favicon_item
      self.favicon_item = None
    item_selector = self.path[-1].item_selector
    item = InterestItem(item_selector)
    item_loader = DefaultItemLoader(item, response=response, response_ctx=response) #pass the response to i/o processors
    for field_selector in item_selector:
      if field_selector.type == FieldSelector.CSS:
        if field_selector.content_type == FieldSelector.TEXT_CONTENT:
          [item_loader.add_css(field_selector.name, selector) for selector in field_selector.selectors]
        elif field_selector.content_type == FieldSelector.IMAGE_CONTENT:
          [item_loader.add_css("image_urls", selector) for selector in field_selector.selectors]
      elif field_selector.type == FieldSelector.XPATH:
        if field_selector.content_type == FieldSelector.TEXT_CONTENT:
          [item_loader.add_xpath(field_selector.name, selector) for selector in field_selector.selectors]
        elif field_selector.content_type == FieldSelector.IMAGE_CONTENT:
          [item_loader.add_xpath("image_urls", selector) for selector in field_selector.selectors]
    item_loader.add_value("id", self.id)
    item = item_loader.load_item()
    self.event_handler.emit(ItemScraped(), item=item)
    yield item
  
  @staticmethod      
  def get_manager():
    return ScrapyManager

# ------------------------------------------------------------------------- #
#two modules brought together to solve a circular import

from twisted.internet import reactor
import os
from scrapy.crawler import Crawler
from scrapy import log
from scrapy.utils.project import get_project_settings


class ScrapyManager(object):
  """Takes the spider information and handles launching and 
     termination of the spider(s)"""
  def __init__(self, spidersInfo=[]):
    # set the settings directory. Use scrapy settings manager
    os.environ["SCRAPY_SETTINGS_MODULE"] = "visualscrape.settings"
    self.spiders_info = spidersInfo
    self.closed_spiders = 0
    self.crawlers = []
    self._crawl_process = Process(target=self.run_spiders, args=())
    
  def start_all(self):
    self._crawl_process.start()
    
  def run_spiders(self):
    """Currently, all the spiders are run within the same process"""
    log.start(loglevel=log.DEBUG)
    for (id, sp_info) in enumerate(self.spiders_info):
      spider = ScrapyCrawler(sp_info.spider_path, id, sp_info.spider_name, 
                             eventHandler=sp_info.event_handler)
      settings = get_project_settings()
      crawler = Crawler(settings)
      self.crawlers.append(crawler)
      # connect each spider's closed signal to self. When all spiders done, stop the reactor
      crawler.signals.connect(self.spider_closed, signal=signals.spider_closed) # i do not really now if that is appended or overwritten
      crawler.configure()
      crawler.crawl(spider)
      crawler.start()
    reactor.run()
    
  def spider_closed(self, spider):
    self.closed_spiders += 1
    spider.event_handler.emit(SpiderClosed(spider.id))
    if self.closed_spiders == len(self.spiders_info):
      reactor.stop()
