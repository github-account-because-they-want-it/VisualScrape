'''
Created on Jun 18, 2014
@author: Mohammed Hamdy
'''
from scrapy.selector import Selector
from scrapy.utils.misc import load_object
from visualscrape.lib.selector import FieldSelector, ContentSelector, ImageSelector
from visualscrape.config.reader import Setting
from visualscrape.config import settings
from visualscrape import settings as setting_module
from visualscrape.lib.data import SpiderConfigManager
from visualscrape.lib.types import SpiderTypes
import re, cPickle as pickle, os

class CommonCrawler(object):
  """Operations common to spiders to avoid duplication"""
  
  def __init__(self, spiderInfo, spiderID, sleepTimeout=1, **kwargs):
    if not spiderInfo:
      self.resume()
    else:
      self._spider_info = spiderInfo
      
    self.favicon_required = settings.DOWNLOAD_FAVICON.value() 
    self.item_loader = CommonCrawler.get_item_loader_for(self._spider_info.spider_path[0])
    self.request_delay = settings.SITE_PARAMS.by(spiderInfo.spider_path[0]).get("REQUEST_DELAY", 1)
    self._spider_path = spiderInfo.spider_path
    self._id = spiderID
    self.name = spiderInfo.spider_name
    # load configuration data for the spider
    self._sleep_timeout = sleepTimeout
    self._resumed = False
    self._stopped = False # flag for the spiders to check
    self._temp_paused = False
    self._visited_urls_before_shutdown = []
  
  def temp_pause(self):
    self._temp_paused = True # this should be checked in spider code
    
  def temp_resume(self):
    self._temp_paused = False
    
  def pause(self):
    """A pause that prepares the spider for a later resume"""
    # save the spider info to disk, to be able to recover it
    info_file = open(SpiderConfigManager.get_info_file_for(self.name), "wb")
    pickle.dump(self._spider_info, info_file)
    info_file.close()
    
  def resume(self):
    """Loads the latest progress from disk"""
    self._resumed = True
    # load the pipeline progress
    config_file = open(SpiderConfigManager.get_config_file_for(self.name), "rb")
    self._visited_urls_before_shutdown = pickle.load(config_file)
    config_file.close()
    # load the spider info
    info_file = open(SpiderConfigManager.get_info_file_for(self.name), "rb")
    spider_info = pickle.load(info_file)
    self._spider_info = spider_info
    info_file.close()
    
  def stop(self, keepState=True):
    if not keepState:
      # delete the configuration file for the spider
      os.remove(SpiderConfigManager.get_config_file_for(self.name))
    self._stopped = True
  
  def get_item_info(self, kvSelectors, response):
    """Do field key preprocessing if required and return key-selector map"""
    item_info = {"keys":[], "values":[]}
    for key_value_selector in kvSelectors:
      # keys can be either strings or selectors. For the latter, obtain the key from the page
      key_selector = key_value_selector.key_selector
      if isinstance(key_selector, FieldSelector): #key_selector is a FieldSelector, use it to get the key from the response
        sel = Selector(response)
        if key_selector.type == FieldSelector.XPATH:
          key = sel.xpath(key_selector).extract()
        elif key_selector.type == FieldSelector.CSS:
          key = sel.css(key_selector).extract()
        if key: key = key[0]
        else: key = "Invalid_Key_Selector" #this may pack in all values with invalid keys with this key.
      else: 
        key = key_selector
      item_info["keys"].append(key)
      value_selector = key_value_selector.value_selector
      item_info["values"].append(value_selector)
    return item_info
  
  def fill_item_loader(self, itemLoader, itemInfo, response, ppInfo):
    """Fill an item loader with data from itemInfo and response"""
    from visualscrape.lib.scrapylib.scrapy_crawl import ScrapyCrawler
    import visualscrape.lib.seleniumlib.selenium_crawl as selenium_mod
    for (key, value_selector) in zip(itemInfo["keys"], itemInfo["values"]):
      if isinstance(value_selector, ContentSelector):
        restricted = self._selectFrom(value_selector.restrict_selector, value_selector.restrict_selector.type, response)
        if restricted: restrict_selector = restricted[0] # get the first tag that matches the restrict selector
        else: 
          from visualscrape.lib.scrapylib.log import log
          log.warn("Content restrict selector returned empty: %s" % value_selector.restrict_selector)
          continue
        # select all subelements of restricted and check them against the regex
        subs = restrict_selector.xpath("//*")
        if value_selector.selector.type == FieldSelector.WORDLIST:
          words = value_selector.selector.split(", ")
          regexp = re.compile('|'.join(words), re.IGNORECASE)
        elif value_selector.selector.type == FieldSelector.REGEX:
          regexp = re.compile(value_selector.selector, re.IGNORECASE)
        for sub_element in subs:
          subtext = sub_element.css("::text").extract()
          if subtext: subtext = subtext[0] # the text of the parent not the children
          else: continue
          match = regexp.match(subtext)
          if match:
            value = subtext
            break
        else: value = '' # no value found for the selector. empty text
        itemLoader.add_value(key, value)
      elif isinstance(value_selector, FieldSelector):
        if value_selector.type == FieldSelector.CSS:
          if isinstance(value_selector, ImageSelector):
            itemLoader.add_css("image_urls", value_selector)
          else:
            itemLoader.add_css(key, value_selector)
        elif value_selector.type == FieldSelector.XPATH:
          if isinstance(value_selector, ImageSelector):
            itemLoader.add_xpath("image_urls", value_selector)
          else:
            itemLoader.add_xpath(key, value_selector)
    if isinstance(self, selenium_mod.SeleniumCrawler):
      self._loadPageActions(itemLoader)
    itemLoader.add_value("_id", self._id)
    # add the post processing information
    itemLoader.add_value("_postinfo", ppInfo)
    spider_type = SpiderTypes.TYPE_SCRAPY if isinstance(self, ScrapyCrawler) else SpiderTypes.TYPE_SELENIUM
    itemLoader.add_value("_spidertype", spider_type)
    itemLoader.add_value("_spidername", self.name)
    # the response url. intentional because for selenium there's no requests on responses. 
    # This means if there was a redirection on the item url, the redirected-to url is the one saved
    itemLoader.add_value("_scrapedurl", response.url) 
    item = itemLoader.load_item()
    return item
  
  def _selectFrom(self, selector, selectorType, response):
    sel = Selector(response)
    if selectorType == FieldSelector.CSS:
      elems = sel.css(selector)
    elif selectorType == FieldSelector.XPATH:
      elems = sel.xpath(selector)
    return elems
  
  @staticmethod
  def get_item_loader_for(startUrl):
    """Used by spider managers to get item loaders for spiders, because it can be spider-specific"""
    site_params_setting = Setting("SITE_PARAMS")
    site_params = site_params_setting.by(startUrl)
    if site_params: 
      loader_cls = site_params.get("ITEM_LOADER", None)
      if loader_cls: # specific item loader?
        return load_object(loader_cls)
      else: return load_object(setting_module.ITEM_LOADER) #default item loader
    else: return load_object(setting_module.ITEM_LOADER) #default item loader
  
  @staticmethod  
  def get_preferred_scraper_for(startUrl):
    """Used by the engine to get the user-defined scraper for his site"""
    scraper_classes = setting_module.SCRAPER_CLASSES
    # switch keys and values, to be able to get the class by it's number
    switched = {value:key for (key, value) in scraper_classes.items()}
    #now get the index of the user-defined class, if at all
    site_params_setting = Setting("SITE_PARAMS")
    start_url_params = site_params_setting.by(startUrl)
    if start_url_params:
      scraper_index = start_url_params.get("PREFERRED_SCRAPER", None)
      if scraper_index is None: # no user-defined field, return first scraper class
        return load_object(switched[min(switched.keys())]) 
      else:
        return load_object(switched[scraper_index])
    else: # No site params for this site
      return load_object(switched[min(switched.keys())])
    