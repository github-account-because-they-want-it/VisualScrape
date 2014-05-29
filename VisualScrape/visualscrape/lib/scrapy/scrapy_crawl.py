'''
Created on May 26, 2014
@author: Mohammed Hamdy
'''
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from scrapy.contrib.loader import ItemLoader
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from functools import  partial
import urlparse
from visualscrape.lib.path import URL, Form
from visualscrape.lib.item import InterestItem
from visualscrape.lib.scrapy.itemloader import DefaultItemLoader
from visualscrape.lib.selector import FieldSelector, ItemSelector
from visualscrape.lib import Signal
from visualscrape.lib.scrapy.manager import ScrapyManager

class ScrapyCrawler(CrawlSpider):
  """
  This spider now doesn't support multiple urls per path, something 
  like start_urls=[url1, more than 1 url...]
  """
  def __init__(self, spiderPath, name="ScrapyCrawler", spiderID, *args, **kwargs):
    super(CrawlSpider, self).__init__(*args, **kwargs)
    self.name = name
    self.path = spiderPath
    self.id = spiderID
    self.path_index = 0
    self.favicon_required = kwargs.get("downloadFavicon", True) #the favicon for the scraped site will be added to the first item
    
  def addParser(self):
    """
    Dynamically add generalParser method to self with a name that 
    starts with parse_ and return it
    """
    #you can add just one parser and change it's arguments instead
    next_step = self.path.pop(0)
    parse_meth = partial(generalParser, self, next_step)
    meth_name = "parser_%d" % self.path_index
    self.__dict__[meth_name] = parse_meth
    self.path_index += 1
    return eval("self.{0}".format(meth_name))
    
  def start_requests(self):
    start_path = self.path.pop(0)
    self.path_index += 1
    if type(start_path) == URL:
      start_url = start_path
      request = Request(start_path)
    elif type(start_path) == Form:
      start_url = start_path.url
      request = FormRequest(start_path.url, start_path.data, 
                          callback=self.addParser())
    
    if self.favicon_required: #the first item contains only the favicon
      #obtain the favicon url
      url_components = urlparse.urlparse(start_url)
      favicon_url = urlparse.urljoin(url_components.scheme + "://" + url_components.netloc, "favicon.ico")
      favicon_item_loader = ItemLoader()
      favicon_item_loader.add_value("image_urls", [favicon_url])
      favicon_item_loader.add_value("id", self.id)
      yield [favicon_item_loader.load_item(), request]
    else:
      yield [request]
    
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
      
def generalParser(self, step, response):
  """
  A spider parser method that can deal with urls, selectors 
  and images
  """
  if type(step) == URL:
    yield [Request(step, callback=self.addParser())]
  elif type(step) == Form:
    yield [FormRequest(step.url, step.data, 
                          callback=self.addParser())]
  elif type(step) == ItemSelector:
    # Make an Item from selectors
    item_selector = step
    #check if this item selector has url content, which means that urls scraped should be followed
    url_selectors = [field_selector for field_selector in item_selector if 
                     field_selector.content_type == FieldSelector.URL_CONTENT]
    if len(url_selectors):
      sel = Selector(response)
      all_urls = []
      for selector in url_selectors:
        for sub_selector in selector.selectors: #don't forget that selectors can have backups
          if selector.type == FieldSelector.CSS:
            all_urls.extend(sel.css(sub_selector).extract())
          elif selector.type == FieldSelector.XPATH:
            all_urls.extend(sel.xpath(sub_selector).extract())
      #canonicalize urls
      urlized = [URL(url) for url in all_urls]
      canonicalized = [url.canonicalize(response.url) for url in urlized]
      new_parser = self.addParser() #is this going to be called for each response?!!
      yield [Request(url, callback=new_parser) for url in canonicalized]
    else: #not a url pass, treat as items to yield
      item = InterestItem(item_selector)
      item_loader = DefaultItemLoader(item, response, response_ctx=response)
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
    
"""
Ok. There's a problem. There's the notion of a url to just follow, and the url to extract
and apply the ItemSelectors next in line to it.
I think my program currently doesn't distinguish between them, and it needs to.
Well, this is a problem, or not. But the whole spider parsing thing must be re-written.
Currently, I add a new parsing method for each request. This is wrong. It should be added for
each spider step.
I'm thinking of a specific parse method for each type of step. I already do that
for the first step.
I can also extract them steps with type URL_CONTENT and use rules for them.
How should it go?:
After extracting all rules, request the start url, and the response ...
The urls from the rules should have their urls visited and items extracted. Review Nefsak
Let's frame it like that:
The first page will be either a URL or a Form. In either case, you can start at the url, 
and do a check based on meta attributes in the handler.
The general idea is that, there are many pages you want to parse the same, and some urls
to generate more of these pages (pagination).
So I'm lost. How to dynamically create a spider, which is also quite flexible?
You've got 2 types of extractors: PageExtractors and ItemExtractors
I need to rethink my path shit. 
Here's how it should go:
The crawler will have at it's disposal a start request, which is either a url or a form.
The crawler can go some follow up urls after that.
Then there will be the main crawling page. On this page, links to items will be extracted
(linkextractor) and pagination pages will be extracted, and handled similarly to the main
crawling page.
So we have the start url, follow up url(s) and and the main page, which has 3 components:
1- paginator (similar pages selector, probably with a restrict) 
2- item page selector
3- item extractor
This is where it all ends. No more thing will follow
"""