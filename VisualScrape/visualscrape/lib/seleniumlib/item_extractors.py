'''
Created on Nov 21, 2014
@author: Mohammed Hamdy
'''

import time, os
from visualscrape.lib.selector import (FieldSelector, ItemPageClickAction, 
  ItemPageScrollDistanceAction, ItemPageScrollToElementAction, 
  ItemPageActionAbsoluteWait, ItemPageScrollUntilAction, ItemPageAction)
from visualscrape.lib.util import download_image
from visualscrape import settings
from visualscrape.lib.scrapylib.item_extractors import ItemExtractor
from visualscrape.lib.commonspider.url_generator import ItemFilterMixin

class SeleniumItemExtractor(ItemExtractor):
  
  def __init__(self, browserHandler, *args, **kwargs):
    super(SeleniumItemExtractor, self).__init__(*args, **kwargs)
    self.browser_handler = browserHandler
  
  def extract_item(self, response, browser):
    item = super(SeleniumItemExtractor, self).extract_item(self, response)
    image_urls = item.pop("image_urls", None)
    if image_urls: # only add images field to the item if the results already include images. ie, no extra fields
      save_folder = self._get_image_save_path()
      downloaded_images = []
      for image_url in image_urls:
        loc = download_image(image_url, save_folder)
        if loc: downloaded_images.append((image_url, loc))
      item.fields["images"] = [{"url":url, "path":path} for (url, path) in downloaded_images] 
    self._performPageActions(browser)
    return item
  
  def extract_favicon_item(self, siteURL):
    favicon_item = super(SeleniumItemExtractor, self).extract_favicon_item(siteURL)
    favicon_url = favicon_item["image_urls"][0]
    downloaded_path = download_image(favicon_url, self._get_image_save_path())
    favicon_item["images"] = [{"path": downloaded_path, "url":favicon_url}]
    return favicon_item
  
  def _performPageActions(self, browser):
    item_selector = self.item_selector
    page_actions = []
    for selector_action in item_selector:
      if isinstance(selector_action, ItemPageAction):
        page_actions.append(selector_action)
    if not page_actions: return 
    for action in page_actions:
      if isinstance(action, ItemPageClickAction):
        action_selector = action.selector
        action_selector_type = action.selector_type
        # find the [ELEMENTS] to click or whatever
        action_elems = self._selectBy(browser, action_selector, action_selector_type)
        for action_elem in action_elems:
          action_elem.click() # wait?
          self.browser_handler.wait(browser)
      elif isinstance(action, ItemPageScrollDistanceAction):
        distance = action.distance
        browser.execute_script("window.scrollBy(0, {});".format(distance))
      elif isinstance(action, ItemPageScrollToElementAction):
        # to faciliate easier selection, enable JQuery on the browser
        self.browser_handler.enable_JQuery_on(browser)
        target_selector = action.selector
        target_selector_type = action.selector_type
        if target_selector_type == FieldSelector.CSS: # I'll assume they are all CSS for now
          browser.execute_script("$({}).get().scrollIntoView();".format(target_selector))
      elif isinstance(action, ItemPageActionAbsoluteWait):
        time.sleep(float(action.time) / 1000 )
      elif isinstance(action, ItemPageScrollUntilAction):
        # this is a crude implementation, since the content might have already been changed by this time
        original_page_source = browser.page_source
        original_len = len(original_page_source)
        # scroll the browser to the bottom, to get new content
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        timeout = action.timeout
        wait_sum = 0
        while wait_sum < timeout and len(browser.page_source) == original_len:
          time.sleep(1)
          wait_sum += 1000 # msecond   
          
  def _get_image_save_path(self):
    #read the save _spider_path from settings
    save_folder = settings.get("IMAGES_STORE")
    save_folder = os.path.join(save_folder, "selenium_images")
    return save_folder
  
  def _selectBy(self, browser, selector, selectorType):
    if selectorType == FieldSelector.CSS:
      selected = browser.find_elements_by_css_selector(selector)
    elif selectorType == FieldSelector.XPATH:
      selected = browser.find_elements_by_xpath(selector)
    return selected

class FilteringItemExtractor(SeleniumItemExtractor, ItemFilterMixin):
  
  def __init__(self, filterPredicate):
    self.predicate = filterPredicate
    
  def extract_item(self, response):
    if self.predicate is None:
      return ItemExtractor.extract_item(self, response)
    if self.page_has_item(response):
      return ItemExtractor.extract_item(self, response)
    return None