'''
Created on Jun 4, 2014
@author: Mohammed Hamdy
'''

from scrapy.http import TextResponse
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
import os, urlparse, sys, time
from visualscrape.lib.selector import FieldSelector, UrlSelector, ItemPageAction, ItemPageAfterActionSelect
from visualscrape.lib.pipeline_handler import PipelineHandler
from visualscrape.lib.item import InterestItem, FaviconItem
from visualscrape.lib.util import download_image
from visualscrape.lib.path import URL
from visualscrape.config import settings

class SeleniumDataHandlerMixin(object):
  """Takes the browser instances and the spider _spider_path. When called at the right times,
     returns items, item pages and navigation pages"""
  
  def __init__(self):
    self.pipeline_handler = PipelineHandler(self)
    self.navigation_extracted = [] #keep track of extracted navigation pages and don't return duplicates
    
  def item_pages(self):
    main_page = self._spider_path[-1]
    item_page_selector = main_page.item_page_selector
    return self._get_links_from_selector(item_page_selector, restrict=None, unique=False), item_page_selector.action
    
  def favicon_item(self):
    favicon_item = FaviconItem()
    favicon_item["_id"] = self._id
    parsed_home = urlparse.urlparse(self.get_nav_browser().current_url)
    favicon_url = urlparse.urljoin(parsed_home.scheme + "://" + parsed_home.netloc, "favicon.ico")
    downloaded_path = download_image(favicon_url, self._get_image_save_path())
    favicon_item["images"] = [{"path": downloaded_path, "url":favicon_url}]
    self.pipeline_handler.run_pipeline(favicon_item)
    return favicon_item
    
  def next_item(self):
    # enable pausing and resuming
    while self._temp_paused:
      time.sleep(self._sleep_timeout)
    #find an item from the item browser and return it
    item_selector = self._spider_path[-1].item_selector
    key_value_selectors = item_selector.key_value_selectors
    item_browser = self.get_item_browser()
    response = TextResponse(item_browser.current_url, body=item_browser.page_source, encoding="utf-8")
    item_info = self.get_item_info(key_value_selectors, response)
    # dynamically create the item from collected keys. The item must be created before the item loader
    item = InterestItem(item_info["keys"])
    item_loader = self.item_loader(item, response=response, response_ctx=response) #pass the response to i/o processors
    item = self.fill_item_loader(item_loader, item_info, response, item_selector.post_process_info)
    # manually download the images
    image_urls = item.pop("image_urls", None)
    if image_urls: # only add images field to the item if the results already include images. ie, no extra fields
      save_folder = self._get_image_save_path()
      downloaded_images = []
      for image_url in image_urls:
        loc = download_image(image_url, save_folder)
        if loc: downloaded_images.append((image_url, loc))
      item.fields["images"] = [{"url":url, "path":path} for (url, path) in downloaded_images] 
    self.pipeline_handler.run_pipeline(item)
    return item
     
  def more_navigation_pages(self):
    """This should be called whenever visiting a new "MainPage" """
    main_page = self._spider_path[-1]
    similar_pages_selector = main_page.similar_pages_selector
    new_links = []; action = UrlSelector.ACTION_VISIT
    if similar_pages_selector and isinstance(similar_pages_selector, UrlSelector):
      action = similar_pages_selector.action
      restrict = main_page.similar_pages_restrict
      new_links = self._get_links_from_selector(similar_pages_selector, restrict, unique=True)
    # append the current browser url to the visited nav and don't send it to the browser
    if not self.get_nav_browser().current_url in self.navigation_extracted:
      self.navigation_extracted.append(self.get_nav_browser().current_url)
    return new_links, action
    
  def _convert_selector(self, selector):
    """Convert the selector from Scrapy to Selenium version"""
    if '@' in selector and selector.type == FieldSelector.XPATH:
      #strip off the last @ attribute reference to the end
        #use the first selector that returns elements
        ref_pos = selector.rfind("/@")
        if ref_pos: selector = selector[:ref_pos]
        if len(self.get_nav_browser().find_elements_by_xpath(selector)):
          return selector
    elif "::" in selector and selector.type == FieldSelector.CSS:
      # strip of the last :: occurence to the end
      ref_pos = selector.rfind("::")
      if ref_pos: 
        selector = selector[:ref_pos]
        if len(self.get_nav_browser().find_elements_by_css_selector(selector)):
          return selector
    else: return selector # no change
  
  def _get_image_save_path(self):
    #read the save _spider_path from settings
    save_folder = settings.IMAGES_STORE.value()
    save_folder = os.path.join(save_folder, "selenium_images")
    return save_folder
  
  def _get_links_from_selector(self, selector, restrict=None, unique=False):
    """Uses the nav_browser. Wanna pass another?
       Returns href strings or selenium webdriver elements, according to selector type"""
    if selector.action == UrlSelector.ACTION_VISIT:
      #use scrapy facilities to extract your hrefs. Also, the visit action implies that hrefs are unique
      response = TextResponse(self.get_nav_browser().current_url, body=self.get_nav_browser().page_source, encoding="utf-8")
      if selector.type == FieldSelector.REGEX:
        extractor = SgmlLinkExtractor(allow=selector,
                                    restrict_xpaths=restrict if restrict else ())
        links = extractor.extract_links(response)
        links = [link.url for link in links]
      elif selector.type == FieldSelector.CSS or selector.type == FieldSelector.XPATH:
        sel = Selector(response)
        if selector.type == FieldSelector.CSS:
          if not "::href" in selector: selector = selector + "::attr(href)"
          links = sel.css(selector).extract()
        elif selector.type == FieldSelector.XPATH:
          if not "/@href" in selector: selector = selector + "/@href"
          links = sel.xpath(selector).extract()
        # after all, canonicalize, because css and xpath are not canoned automatically like sgml...
        links = [URL(link).canonicalize(self.get_nav_browser().current_url) for link in links]
      if unique:
        new_links = [link for link in links if link not in self.navigation_extracted]
        self.navigation_extracted.extend(new_links)
        return new_links
      else: return links
    elif selector.action == UrlSelector.ACTION_CLICK:
      # now you have to operate on web elements so that the browser can click them. 
      # Probably because of the links having js attached
      if selector.type == FieldSelector.REGEX:
        pass # no regex links for selenium for now
      elif selector.type == FieldSelector.CSS:
        links = self.get_nav_browser().find_elements_by_css_selector(selector)
      elif selector.type == FieldSelector.XPATH:
        links = self.get_nav_browser().find_elements_by_xpath(selector)
      if unique:
        links = self._filter_unique_and_save(selector, links)
      return links
      
  def _filter_unique_and_save(self, selector, links):
    """Uses the elements unique attribute together with self.navigation_extracted
       to get new links
       links : must be selenium WebElements"""
    if selector.unique_attr == UrlSelector.UNIQUE_HREF:
        new_links = [link for link in links if link.get_attribute("href") not in self.navigation_extracted]
        uniq_attrs = [link.get_attribute("href") for link in new_links]
    elif selector.unique_attr == UrlSelector.UNIQUE_TEXT:
      new_links = [link for link in links if link.text not in self.navigation_extracted]
      uniq_attrs = [link.text for link in new_links]
    elif selector.unique_attr == UrlSelector.UNIQUE_ONCLICK:
      new_links = [link for link in links if link.get_attribute("onCLick") not in self.navigation_extracted]
      uniq_attrs = [link.get_attribute("onClick") for link in new_links]
    self.navigation_extracted.extend(uniq_attrs)
    if self._resumed:
      new_links = [link for link in new_links if not link in self._visited_urls_before_shutdown]
    return new_links
  
  def _loadPageActions(self, itemLoader):
    page_actions = self._spider_path[-1].item_selector.item_page_actions
    if not page_actions: return itemLoader
    for action, after_action in page_actions:
      after_selector = after_action.selector
      after_selector_type = after_action.selector_type
      output_field = after_action.output_field
      after_selector, after_attribute = self._splitSelector(after_selector, after_selector_type)
      if action.type == ItemPageAction.ACTION_CLICK:
        item_browser = self.get_item_browser()
        action_selector = action.selector
        action_selector_type = action.selector_type
        # find the [ELEMENTS] to click or whatever
        if action_selector_type == FieldSelector.CSS:
          action_elems = item_browser.find_elements_by_css_selector(action_selector)
        elif action_selector_type == FieldSelector.XPATH:
          action_elems = item_browser.find_elements_by_xpath(action_selector)
        for action_elem in action_elems:
          action_elem.click() # wait?
          self._wait(item_browser)
          if isinstance(after_action, ItemPageAfterActionSelect):
            if after_selector_type == FieldSelector.CSS:
              extra_elems = item_browser.find_elements_by_css_selector(after_selector)
            elif after_selector_type == FieldSelector.XPATH:
              extra_elems = item_browser.find_elements_by_xpath(after_selector)
            if after_attribute == "text" or not after_attribute:
              extra_values = [extra_elem.text for extra_elem in extra_elems]
            else:
              extra_values = [extra_elem.get_attribute(after_attribute) for extra_elem in extra_elems]
            
            itemLoader.add_value(output_field, extra_values)
  
  def _splitSelector(self, selector, selectorType):
    if selectorType == FieldSelector.CSS:
      attr_start = selector.rfind("::")
      if attr_start < 0: return selector, ''
      attr = selector[attr_start+2:]
      selector = selector[:attr_start]
      return selector, attr
    elif selectorType == FieldSelector.XPATH:
      if selector.endswith("/text()"):
        selector = selector[:selector.rfind("/text()")]
        attr = "text"
        return selector, attr
      elif selector.rfind("/@") > 0: # the slash here is important, since @ can appear in attribute lookups
        attr_start = selector.rfind("/@")
        attr = selector[attr_start+2:]
        selector = selector[:attr_start]
        return selector, attr
      else: return selector, ''
  
  def make_profile_dir(self):
    """Create a profile folder with a prefix and randomized name part. The bug is within selenium.
    Not mine. So this function won't work."""
    if sys.platform.startswith("win32"):
      pass