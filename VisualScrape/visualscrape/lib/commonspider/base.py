'''
Created on Jun 18, 2014
@author: Mohammed Hamdy
'''
from scrapy.selector import Selector
from visualscrape.lib.selector import FieldSelector, ContentSelector, ImageSelector
from visualscrape.lib.scrapylib.log import log
import re

class CommonCrawler(object):
  """Operations common to spiders to avoid duplication"""
  
  def get_item_info(self, kvSelectors, response):
    """Do field key preprocessing if required and return key-selector map"""
    item_info = {"keys":[], "values":[]}
    for key_value_selector in kvSelectors:
      # keys can be either strings or selectors
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
    for (key, value_selector) in zip(itemInfo["keys"], itemInfo["values"]):
      if isinstance(value_selector, ContentSelector):
        sel = Selector(response)
        restricted = sel.css(value_selector.restrict_selector)
        if restricted: restrict_selector = restricted[0] # get the first tag that matches the restrict selector
        else: 
          log.warn("Content restrict selector returned empty: %s" % value_selector.restrict_selector)
          continue
        # select all subelements of restricted and check them against the regex
        subs = restrict_selector.xpath("//*")
        if value_selector.type == ContentSelector.WORDLIST:
          words = value_selector.split()
          regexp = re.compile(words.join('|'), re.IGNORECASE)
        elif value_selector.type == ContentSelector.REGEX:
          regexp = re.compile(value_selector, re.IGNORECASE)
        for sub_element in subs:
          subtext = sub_element.css("::text")
          match = regexp.match(subtext)
          if match:
            value = subtext[match.start():match.end()]
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
    itemLoader.add_value("id", self.id)
    # add the post processing information
    itemLoader.add_value("postinfo", ppInfo)
    item = itemLoader.load_item()
    return item