'''
Created on Jun 4, 2014
@author: Mohammed Hamdy
'''

from scrapy.http import TextResponse
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
import os, urlparse
from visualscrape.lib.scrapylib.itemloader import DefaultItemLoader
from visualscrape.lib.selector import FieldSelector, UrlSelector, ImageSelector
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
    return self._get_links_from_selector(item_page_selector, restrict=None, unique=False), item_page_selector.action
    
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
    # this is a duplicate from scrapy item parser. Probably refactor
    response = TextResponse(self.item_browser.current_url, body=self.item_browser.page_source, encoding="utf-8")
    item_info = {"keys":[], "values":[], "types":[]}
    # fill an item loader
    for key_value_selector in item_selector:
      # keys can be either strings or selectors
      key_selector = key_value_selector.key_selector
      if isinstance(key_selector, (str, unicode)): key = key_selector
      else: #key_selector is a FieldSelector, use it to get the key from the response
        sel = Selector(response)
        if key_selector.type == FieldSelector.XPATH:
          key = sel.xpath(key_selector).extract()
        elif key_selector.type == FieldSelector.CSS:
          key = self.css(key_selector).extract()
        if key: key = key[0]
        else: key = "Invalid_Key_Selector" #this may pack in all values with invalid keys with this key.
      item_info["keys"].append(key)
      value_selector = key_value_selector.value_selector
      item_info["values"].append(value_selector)
    # dynamically create the item from collected keys. The item must be created before the item loader
    item = InterestItem(item_info["keys"])
    item_loader = DefaultItemLoader(item, response=response, response_ctx=response) #pass the response to i/o processors
    for (key, value_selector) in zip(item_info["keys"], item_info["values"]):
      if value_selector.type == FieldSelector.CSS:
        if isinstance(value_selector, ImageSelector):
          item_loader.add_css("image_urls", value_selector)
        else:
          item_loader.add_css(key, value_selector)
      elif value_selector.type == FieldSelector.XPATH:
        if isinstance(value_selector, ImageSelector):
          item_loader.add_xpath("image_urls", value_selector)
        else:
          item_loader.add_xpath(key, value_selector)
    item_loader.add_value("id", self.spider_id)
    item = item_loader.load_item() # this should take care of canonicalizing image urls and processing stuff
    # manually download the images
    image_urls = item.pop("image_urls", None)
    if image_urls: # only add images field to the item if the results already include images. ie, no extra fields
      save_folder = self._get_image_save_path()
      downloaded_images = []
      for image_url in image_urls:
        loc = download_image(image_url, save_folder)
        if loc: downloaded_images.append((image_url, loc))
      item.fields["images"] = [{"url":url, "path":path} for (url, path) in downloaded_images] 
    return item
     
  def more_navigation_pages(self):
    """This should be called whenever visiting a new "MainPage" """
    main_page = self.path[-1]
    similar_pages_selector = main_page.similar_pages_selector
    new_links = []; action = UrlSelector.ACTION_VISIT
    if similar_pages_selector and isinstance(similar_pages_selector, UrlSelector):
      action = similar_pages_selector.action
      restrict = main_page.similar_pages_restrict
      new_links = self._get_links_from_selector(similar_pages_selector, restrict, unique=True)
    # append the current browser url to the visited nav and don't send it to the browser
    if not self.nav_browser.current_url in self.navigation_extracted:
      self.navigation_extracted.append(self.nav_browser.current_url)
    return new_links, action
    
  def _convert_selector(self, selector):
    """Convert the selector from Scrapy to Selenium version"""
    if '@' in selector and selector.type == FieldSelector.XPATH:
      #strip off the last @ attribute reference to the end
        #use the first selector that returns elements
        ref_pos = selector.rfind("/@")
        if ref_pos: selector = selector[:ref_pos]
        if len(self.nav_browser.find_elements_by_xpath(selector)):
          return selector
    elif "::" in selector and selector.type == FieldSelector.CSS:
      # strip of the last :: occurence to the end
      ref_pos = selector.rfind("/::")
      if ref_pos: 
        selector = selector[:ref_pos]
        if len(self.nav_browser.find_elements_by_css_selector(selector)):
          return selector
    else: return selector # no change
  
  def _get_image_save_path(self):
    #read the save path from settings
    save_folder = settings.IMAGES_STORE.value()
    save_folder = os.path.join(save_folder, "selenium_images")
    return save_folder
  
  def _get_links_from_selector(self, selector, restrict=None, unique=False):
    """Uses the nav_browser. Wanna pass another?
       Returns href strings or selenium webdriver elements, according to selector type"""
    if selector.type == FieldSelector.REGEX:
      """The current standing: The fucking variation between selector types and unique attributes"""
      response = TextResponse(self.nav_browser.current_url, body=self.nav_browser.page_source, encoding="utf-8")
      extractor = SgmlLinkExtractor(allow=selector,
                                  restrict_xpaths=restrict if restrict else ())
      links = extractor.extract_links(response)
    elif selector.type == FieldSelector.CSS or selector.type == FieldSelector.XPATH:
      # these kinds of links may need conversion to be suitable for selenium methods
      selenium_selector = self._convert_selector(selector)
      if selector.type == FieldSelector.XPATH:
        links = self.nav_browser.find_elements_by_xpath(selenium_selector)
      elif selector.type == FieldSelector.CSS:
        links = self.nav_browser.find_elements_by_css_selector(selenium_selector)
      if selector.action == UrlSelector.ACTION_VISIT:
        # get the hrefs from the links
        links = [link.get_attribute("href") for link in links]
    if unique: 
      new_links = self._get_unique_links_from_selector(selector, links)
      return new_links
    else: return links
  
  def _get_unique_links_from_selector(self, selector, links):
    """Uses the elements unique attribute together with self.navigation_extracted
       to get new links"""
    if selector.unique_attr == UrlSelector.UNIQUE_HREF:
        new_links = [link.url for link in links if link.url not in self.navigation_extracted]
        uniq_attrs = new_links
    elif selector.unique_attr == UrlSelector.UNIQUE_TEXT:
      new_links = [link for link in links if link.text not in self.navigation_extracted]
      uniq_attrs = [link.text for link in new_links]
    elif selector.unique_attr == UrlSelector.UNIQUE_ONCLICK:
      new_links = [link for link in links if link.get_attribute("onCLick") not in self.navigation_extracted]
      uniq_attrs = [link.get_attribute("onClick") for link in new_links]
    self.navigation_extracted.extend(uniq_attrs)
    return new_links