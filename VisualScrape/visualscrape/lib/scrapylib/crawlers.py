'''
Created on May 26, 2014
@author: Mohammed Hamdy
'''

from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request, FormRequest
from scrapy import signals
from scrapy.exceptions import CloseSpider
from visualscrape.lib.path import URL, Form
from visualscrape.lib.commonspider.base import BaseCrawler
from visualscrape.lib.signal import SpiderStarted
from .item_extractors import ItemExtractor, FilteringItemExtractor
from .url_generators import ProductCrawlerURLGenerator
from visualscrape.lib.types import SpiderTypes

class ScrapySinglePageCrawler(CrawlSpider, BaseCrawler):
  """
  Visits a page and parses and item from it
  """
  
  def __init__(self, url, itemSelector, spiderID, spiderName="ScrapySinglePageCrawler", **kwargs):
    BaseCrawler.__init__(self, [url], spiderName, spiderID, **kwargs)
    CrawlSpider.__init__(self)
    self.item_extractor = ItemExtractor(itemSelector, self.item_loader,
                            SpiderTypes.TYPE_SCRAPY, spiderName, self._id)
    self.url = url
    self.start_urls = [url]
    
  def parse(self, response):
    if self.favicon_required:
      yield self.item_extractor.extract_favicon_item(self.url)
    yield self.item_extractor.extract_item(response)
    
  @staticmethod
  def get_manager():
    from .managers import ScrapySinglePageCrawlerManager
    return ScrapySinglePageCrawlerManager
  
class ScrapyPageListCrawler(BaseCrawler, CrawlSpider):
  """
  A crawler that crawls an arbitrary URL list, based on a URL generator, which is 
    just a Python generator
  """
  
  def __init__(self, urlGenerator, itemSelector, spiderID, 
               spiderName="ScrapyPageListCrawler", filterPredicate=None, 
               **kwargs):
    # get a url from the generator for BaseCrawler to be able to get URL_PARAMS
    BaseCrawler.__init__(self, ["dummy-unused"], spiderName, spiderID, **kwargs)
    CrawlSpider.__init__(self)
    self.start_urls  = urlGenerator()
    self.item_extractor = FilteringItemExtractor(itemSelector, self.item_loader, 
                            SpiderTypes.TYPE_SCRAPY, self.name, self._id, 
                            filterPredicate=filterPredicate)
    
  def parse(self, response):
    if self.favicon_required:
      self.favicon_required = False
      yield self.item_extractor.extract_favicon_item(response.url)
    yield self.item_extractor.extract_item(response)
    
  @staticmethod
  def get_manager():
    from .managers import ScrapyPageListCrawlerManager
    return ScrapyPageListCrawlerManager
  
class ScrapyProductCrawler(CrawlSpider, BaseCrawler):
  """
  This spider now doesn't support multiple urls per _spider_path, something 
  like start_urls=[url1, more than 1 url...]
  """
  name = "ScrapyProductCrawler"
  def __init__(self, spiderPath, spiderID, spiderName="ScrapyProductCrawler", **kwargs):
    BaseCrawler.__init__(self, spiderPath, spiderID, spiderName, **kwargs)
    main_page = spiderPath[-1]
    self.item_extractor = ItemExtractor(main_page.item_selector, self.item_loader,
                                        SpiderTypes.TYPE_SCRAPY, self.name, self._id)
    self.url_generator = ProductCrawlerURLGenerator(main_page.item_page_selector,
                          main_page.similar_pages_selector, None, 
                          main_page.similar_pages_restrict)
    self.path_index = 0
    self.favicon_item = None
  
  def start_requests(self):
    #this might not work as per docs if it returns items. see Spiders page
    if self.event_handler: self.event_handler.emit(SpiderStarted(self._id))
    start_path = self._spider_path[0]
    if self.favicon_required: #the first item contains only the favicon
      favicon_item = self.item_extractor.extract_favicon_item(start_path)
      self.favicon_item = favicon_item #assign it to be returned later. can't return here
    return self._take_step()
  
  def parse_intermediate(self, response):
    """This should continue until there's only one item in self._spider_path which is
       MainPage object"""
    return self._take_step()
    
  def parse_item_pages(self, response):
    """Gets the pages of items from a MainPage"""
    similar_nav = self.url_generator.parse_pagination_from_response(response)
    for nav in similar_nav: yield Request(nav, dont_filter=False, callback=self.parse_item_pages) # the extracted links can well have their crawled friends
    item_pages = self.url_generator.parse_pagination_from_response(response)
    for request in [Request(page, callback=self.parse_items) for page in item_pages]:
      yield request
    
  def parse_items(self, response):
    if self.favicon_item:
      yield self.favicon_item
      self.favicon_item = None
    item = self.item_extractor.extract_item(response)
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
  
  @staticmethod      
  def get_manager():
    from .managers import ScrapyProductCrawlerManager
    return ScrapyProductCrawlerManager
  
class ScrapyJSBitch(ScrapyProductCrawler):
  """A subclass that collects for only some items to test a site's JS requirements"""
  
  def __init__(self, watcher, spiderInfo, spiderID, itemCount=20, name="ScrapyProductCrawler", **kwargs):
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