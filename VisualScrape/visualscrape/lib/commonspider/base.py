'''
Created on Jun 18, 2014
@author: Mohammed Hamdy
'''
from scrapy.selector import Selector
from scrapy.utils.misc import load_object
from visualscrape.lib.selector import FieldSelector, ContentSelector, ImageSelector,\
  TableSelector
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
    table_selectors = [] # pack them because their processing differs from the rest
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
      elif isinstance(value_selector, TableSelector):
        table_selectors.append(value_selector)
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
    for table_selector in table_selectors:
      if table_selector.table_type == TableSelector.TABLE_HHEADERS:
        self._populateItemLoaderFromHTable(itemLoader, response, table_selector)
      elif table_selector.table_type == TableSelector.TABLE_VHEADERS:
        self._populateItemLoaderFromVTable(itemLoader, response, table_selector)
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
    """Apply the selector to response by selectorType without extraction"""
    sel = Selector(response)
    if selectorType == FieldSelector.CSS:
      elems = sel.css(selector)
    elif selectorType == FieldSelector.XPATH:
      elems = sel.xpath(selector)
    return elems
  
  def _populateItemLoaderFromHTable(self, itemLoader, response, tableSelector):
    table = self._selectFrom(tableSelector, tableSelector.type, response)
    # scrape the the largest even numbers of keys/values
    rows = table.css("tr")
    for row in rows:
      tds = row.css("td")
      if len(tds) == 1: continue # this can be a title data
      for tdi in range(0, len(tds), 2): # this shouldn't execute for td-less rows
        key = self._findTextWithinElement(tds[tdi]) # note that text nodes may not be directly inside td. think <td><bold>...
        key = self._filterKey(key) # only HTables are considered to be liable to have extra characters for me
        if not key:
          continue # skip non-valid keys
        try:
          value = self._findTextWithinElement(tds[tdi + 1])
        except IndexError:
          value = ''
        itemLoader.item.fields[key] = {} # hack the item loader to allow a field not in the original item
        itemLoader.add_value(key, value)
  
  def _populateItemLoaderFromVTable(self, itemLoader, response, tableSelector):
    table = self._selectFrom(tableSelector, tableSelector.type, response)
    # find a row with some th elements and take it as your keys
    # TODO: this needs debugging. There is a problem when there's more that 1 active row span 
    keys = []
    rows = table.css("tr")
    # first get the keys
    for (i, row) in enumerate(rows):
      headers = row.css("th")
      if headers:
        keys = [self._findTextWithinElement(header) for header in headers]
        break
    # search for values after where you found the keys
    data_rows = rows[i+1:]
    active_row_spans = [] # a list of 4-tuples of (rowspan, span_column, span_data, processed_rows)
    values = [] # an array of arrays (rows)
    for (row_i, data_row) in enumerate(data_rows):
      values.append([])
      tds = data_row.css("td")
      for (coli, td) in enumerate(tds):
        row_span = td.xpath("./@rowspan")
        if row_span:
          row_span = int(row_span.extract()[0])
          active_row_spans.append((row_span, coli, self._findTextWithinElement(td), 0))
        # row spans in place. Now check if (any) current td is inside a span
        for (spi, (row_span, span_column, span_data, processed_rows)) in enumerate(active_row_spans):
          if coli == span_column: # i.e, inside an active span
            values[row_i].append(span_data)
            if processed_rows != 0: # do not add the row span twice in the row you found it
              values[row_i].append(self._findTextWithinElement(td))
            processed_rows += 1
            if processed_rows == row_span:
              active_row_spans.pop(spi)
            else:
              active_row_spans[spi] = (row_span, span_column, span_data, processed_rows)
            break
        else: # td not currently in a row span
          values[row_i].append(self._findTextWithinElement(td))
    for (key, value) in zip(keys, values):
      itemLoader.item.fields[key] = {}
      itemLoader.add_value(key, value)
  
  def _findTextWithinElement(self, selector):
    """
    Joins all the texts found within element with the space character
    selector -- scrapy selector object
    """
    parent_text = self._getStrippedText(selector) # everybody has got text I think. so this shouldn't raise IndexError
    if parent_text: return parent_text
    subelements = selector.css('*')
    texts_found = []
    for element in subelements:
      elem_text = self._getStrippedText(element)
      if "CDATA" in elem_text: continue # that's a part of the document not intended to be visible
      texts_found.append(elem_text)
    return ' '.join(texts_found)
  
  def _getStrippedText(self, selector):
    text = selector.css("::text").extract()
    if text:
      text = text[0].strip()
      if text:
        return text
      else:
        return ''
    else:
      return ''
    
  def _filterKey(self, keyText):
    # removes non-character text from the end of key, like (:)
    return re.sub("[^\w]$", '', keyText, flags=re.UNICODE)
    
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
    