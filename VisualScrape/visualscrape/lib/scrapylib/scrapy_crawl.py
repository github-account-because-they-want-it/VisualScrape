'''
Created on May 26, 2014
@author: Mohammed Hamdy
'''
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.spider import Spider
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import urlparse
from visualscrape.lib.path import URL, Form
from visualscrape.lib.item import InterestItem, FaviconItem
from visualscrape.lib.scrapylib.itemloader import DefaultItemLoader
from visualscrape.lib.selector import FieldSelector
from visualscrape.lib import Signal

class ScrapyCrawler(Spider):
  """
  This spider now doesn't support multiple urls per path, something 
  like start_urls=[url1, more than 1 url...]
  """
  name = "ScrapyCrawler"
  def __init__(self, spiderPath, spiderID, name="ScrapyCrawler", *args, **kwargs):
    super(ScrapyCrawler, self).__init__()
    self.name = name
    self.path = spiderPath
    self.id = spiderID
    self.path_index = 0
    self.favicon_required = kwargs.get("downloadFavicon", True) #the favicon for the scraped site will be added to the first item
    self.favicon_item = None
    # use rules to obtain navigation urls
    main_page = self.path[-1]
    # use start_urls instead of start_requests
    first_step = self.path[0]
    self.start_urls = [first_step if type(first_step) == URL else first_step.url]
    self.rules = [Rule(SgmlLinkExtractor(allow=(main_page.similar_pages_selector,) if main_page.similar_pages_selector else (),
                       restrict_xpaths=(main_page.similar_pages_restrict,) if main_page.similar_pages_restrict else ()),
                        callback=self.parse_item_pages)]
    
  def parse_start_url(self, response):
    """First parse will need to differentiate between URL and form requests. With this method, I
       can't pass meta argument with the request to help tell the difference"""
    first_step = self.path.pop(0)
    if type(first_step) == URL:
      start_url = first_step
    elif type(first_step) == Form:
      callback = self.parse_intermediate if type(self.path[0]) == URL else self.parse_item_pages
      request = FormRequest.from_response(response, formdata=first_step.data,
                                          callback=callback)  
      start_url =  first_step.url
      yield request
    if self.favicon_required: #the first item contains only the favicon
      #obtain the favicon url
      url_components = urlparse.urlparse(start_url)
      favicon_url = urlparse.urljoin(url_components.scheme + "://" + url_components.netloc, "favicon.ico")
      favicon_item = FaviconItem()
      favicon_item["image_urls"] =  [favicon_url]
      favicon_item["id"] =  self.id
      self.favicon_item = favicon_item #assign it to be returned later. can't return here
    yield Request("http://www.google.com", callback=self.parse_item_pages)
    
  def parse(self):
    print "Fuck Off!"  
  
  """  
  def start_requests(self):
    #this might not work as per docs if it returns items. see Spiders page
    start_path = self.path.pop(0)
    # determine the callback based on next step
    callback = self.parse_intermediate if type(self.path[0]) == URL else self.parse_item_pages
    if type(start_path) == URL:
      start_url = start_path
      request = Request(start_path, callback=callback)
    elif type(start_path) == Form:
      start_url = start_path.url
      request = FormRequest(start_path.url, start_path.data, 
                          callback=callback)
    
    if self.favicon_required: #the first item contains only the favicon
      #obtain the favicon url
      url_components = urlparse.urlparse(start_url)
      favicon_url = urlparse.urljoin(url_components.scheme + "://" + url_components.netloc, "favicon.ico")
      favicon_item = FaviconItem()
      favicon_item["image_urls"] =  [favicon_url]
      favicon_item["id"] =  self.id
      self.favicon_item = favicon_item #assign it to be returned later. can't return here
    return [request]
  """
  
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
      request = FormRequest(next_url, next_step.data, 
                          callback=callback)
      
    return [request]
    
  def parse_item_pages(self, response):
    sel = Selector(response)
    page_selectors = self.path[-1].item_page_selector
    for item_pages_selector in page_selectors.selectors:
      if page_selectors.type == FieldSelector.XPATH:
        item_pages = sel.xpath(item_pages_selector)
      elif page_selectors.type == FieldSelector.CSS:
        item_pages = sel.css(item_pages_selector)
      yield [Request(page, callback=self.parse_items) for page in item_pages.extract()]
    
  def parse_items(self, response):
    if self.favicon_item:
      yield self.favicon_item
      self.favicon_item = None
    item_selector = self.path[-1].item_selector
    item = InterestItem(item_selector)
    item_loader = DefaultItemLoader(item, response, response_ctx=response) #pass the response to i/o processors
    for field_selector in item_selector:
      if field_selector.type == FieldSelector.CSS:
        if field_selector.content_type == FieldSelector.TEXT_CONTENT:
          [item_loader.add_css(selector.name, selector.selector) for selector in field_selector.selectors]
        elif field_selector.content_type == FieldSelector.IMAGE_CONTENT:
          [item_loader.add_css("image_urls", selector.selector) for selector in field_selector.selectors]
      elif field_selector.type == FieldSelector.XPATH:
        if field_selector.content_type == FieldSelector.TEXT_CONTENT:
          [item_loader.add_xpath(selector.name, selector.selector) for selector in field_selector.selectors]
        elif field_selector.content_type == FieldSelector.IMAGE_CONTENT:
          [item_loader.add_xpath("image_urls", selector.selector) for selector in field_selector.selectors]
    item_loader.add_value("id", self.id)
    yield item_loader.load_item()
  
  def registerHandlers(self, signalsToHandlersMap):
    """
    This is a part of the Spider interface
    signalsToHandlersMap -- a dict that maps visualscrape.lib.Signal constants
                            to a list of handler methods.
    """
    for (signal_id, handlers) in signalsToHandlersMap:
      if signal_id == Signal.SPIDER_STARTED:
        signal = signals.spider_opened
      elif signal_id == Signal.SPIDER_STOPPED:
        signal = signals.spider_closed
      elif signal_id == Signal.SPIDER_ERROR:
        signal = signals.spider_error
      elif signal_id == Signal.ITEM_SCRAPED:
        signal = signals.item_scraped
      for handler in handlers:
        dispatcher.connect(handler, signal=signal)
  
  @staticmethod      
  def get_manager():
    return ScrapyManager

# ------------------------------------------------------------------------- #
#two modules brought together to solve a circular import

from twisted.internet import reactor
import os
from scrapy.crawler import Crawler
from scrapy import log, signals
from scrapy.utils.project import get_project_settings


class ScrapyManager(object):
  """Takes the spider information and handles launching and 
     termination of the spider(s)"""
  def __init__(self, spidersInfo=[]):
    # set the settings directory. Use scrapy settings manager
    os.environ["SCRAPY_SETTINGS_MODULE"] = "visualscrape.settings"
    self.spiders_info = spidersInfo
    self.closed_spiders = 0
    
  def start_all(self):
    """Currently, all the spiders are run within the same process"""
    log.start()
    for (id, sp_info) in enumerate(self.spiders_info):
      spider = ScrapyCrawler(sp_info.spider_path, id, sp_info.spider_name)
      spider.registerHandlers(sp_info.signals_handlers_map)
      settings = get_project_settings()
      crawler = Crawler(settings)
      # connect each spider's closed signal to self. When all spiders done, stop the reactor
      crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)
      crawler.configure()
      crawler.crawl(spider)
      crawler.start()
    reactor.run()
    
  def spider_closed(self):
    self.closed_spiders += 1
    if self.closed_spiders == len(self.spiders_info):
      reactor.stop()
