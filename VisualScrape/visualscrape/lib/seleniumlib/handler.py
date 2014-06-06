'''
Created on Jun 4, 2014
@author: Mohammed Hamdy
'''

from scrapy.http import TextResponse
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
import os, urlparse
from visualscrape.lib.scrapylib.itemloader import DefaultItemLoader
from visualscrape.lib.selector import FieldSelector
from visualscrape.lib.item import InterestItem, FaviconItem
from visualscrape.lib.util import download_image
from visualscrape.config import settings

class SeleniumDataHandler(object):
  """Takes the browser instances and the spider path. When called at the right times,
     returns items, item pages and navigation pages"""
  
  def __init__(self, navBrowser, itemBrowser, spiderPath, spiderId):
    self.nav_browser = navBrowser
    self.item_browser = itemBrowser
    self.path = spiderPath
    self.spider_id = spiderId
    self.navigation_extracted = [] #keep track of extracted navigation pages and don't return duplicates
    
  def item_pages(self):
    main_page = self.path[-1]
    item_page_selector = main_page.item_page_selector
    pure_selector = self._convert_selector(item_page_selector)
    return self._find_elements_by_selector_and_type(pure_selector, 
                                    item_page_selector.type, "href")
    
  def favicon_item(self):
    favicon_item = FaviconItem()
    favicon_item["id"] = self.spider_id
    parsed_home = urlparse.urlparse(self.nav_browser.current_url)
    favicon_url = urlparse.urljoin(parsed_home.scheme + "://" + parsed_home.netloc, "favicon.ico")
    downloaded_path = download_image(favicon_url, self._get_image_save_path())
    favicon_item["image_urls"] = [{"path": downloaded_path}]
    return favicon_item
    
  def next_item(self):
    #find an item from the item browser and return it
    item_selector = self.path[-1].item_selector
    item = InterestItem(item_selector)
    response = TextResponse(self.item_browser.current_url, body=self.item_browser.page_source, encoding="utf-8")
    item_loader = DefaultItemLoader(item, response=response, response_ctx=response)
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
    item_loader.add_value("id", self.spider_id)
    item = item_loader.load_item() # this should take care of canonicalizing image urls and processing stuff
    # manually download the images
    image_urls = item.pop("image_urls", None)
    if image_urls: # only add images field to the item if the results already include images. ie, no extra fields
      save_folder = self._get_image_save_path()
      downloaded_images = []
      for image_url in image_urls:
        loc = download_image(image_url, save_folder)
        if loc: downloaded_images.append(loc)
      item["images"] = [{"path":path} for path in loc] # only location data is added to the item
    return item
     
  def more_navigation_pages(self):
    """This should be called whenever visiting a new "MainPage" """
    main_page = self.path[-1]
    similar_pages_selector = main_page.similar_pages_selector
    similar_pages_xpath_restrict = main_page.similar_pages_restrict
    response = TextResponse(self.nav_browser.current_url, body=self.nav_browser.page_source, encoding="utf-8")
    extractor = SgmlLinkExtractor(allow=similar_pages_selector if similar_pages_selector else (),
                                  restrict_xpaths=similar_pages_xpath_restrict if similar_pages_xpath_restrict else ())
    nav_links = extractor.extract_links(response)
    new_links = [link.url for link in nav_links if link.url not in self.navigation_extracted]
    self.navigation_extracted.extend(new_links)
    # append the current browser url to the visited nav and don't send it to the browser
    if not self.nav_browser.current_url in self.navigation_extracted:
      self.navigation_extracted.append(self.nav_browser.current_url)
    return new_links
    
  def _convert_selector(self, selector):
    """Convert the selector from Scrapy to Selenium version"""
    if selector.type == FieldSelector.XPATH:
      #strip off the last @ attribute reference to the end
      for sub_selector in selector:
        #use the first selector that returns elements
        ref_pos = sub_selector.rfind("/@")
        sub_selector = sub_selector[:ref_pos]
        if len(self.nav_browser.find_elements_by_xpath(sub_selector)):
          return sub_selector
    elif selector.type == FieldSelector.CSS:
      # strip of the last :: occurence to the end
      for sub_selector in selector:
        ref_pos = sub_selector.rfind("/::")
        sub_selector = sub_selector[:ref_pos]
        if len(self.nav_browser.find_elements_by_css_selector(sub_selector)):
          return sub_selector
        
  def _find_elements_by_selector_and_type(self, selector, type, attr):
    if type == FieldSelector.XPATH:
      elems = self.nav_browser.find_elements_by_xpath(selector)
    elif type == FieldSelector.CSS:
      elems = self.nav_browser.find_elements_by_css_selector(selector)
    return [elem.get_attribute(attr) for elem in elems]
  
  def _get_image_save_path(self):
    #read the save path from settings
    save_folder = settings.IMAGES_STORE.value()
    save_folder = os.path.join(save_folder, "selenium_images")
    return save_folder