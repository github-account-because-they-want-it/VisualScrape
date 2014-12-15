'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from visualscrape.lib.path import URL, Form, FormElemInfo, MainPage
from visualscrape.lib.seleniumlib import log
from visualscrape.lib.signal import *
import time, traceback
from visualscrape.lib.selector import UrlSelector
from visualscrape.lib.commonspider.base import SeleniumBaseCrawler
from .item_extractors import SeleniumItemExtractor, FilteringItemExtractor
from .url_generators import ProductCrawlerUrlGenerator
from visualscrape.lib.types import SpiderTypes


class SeleniumSinglePageCrawler(SeleniumBaseCrawler):
  
  def __init__(self, url, itemSelector, spiderID, spiderName, **kwargs):
    SeleniumBaseCrawler.__init__([url], spiderID, spiderName, **kwargs)
    self.url = url
    self.item_extractor = SeleniumItemExtractor(self, itemSelector, self.item_loader, 
                            SpiderTypes.TYPE_SELENIUM, spiderName, spiderID)
    
  def start(self):
    browser = self.create_browser()
    browser.get(self.url)
    browser_response = self.response_from_browser(browser)
    if self.favicon_required:
      favicon_item = self.item_extractor.extract_favicon_item(self.url)
      self.pipeline_handler.run_pipeline(favicon_item)
    item = self.item_extractor.extract_items(browser_response)
    self.pipeline_handler.run_pipeline(item)
    browser.quit()
    self.finishoff()
    
  @staticmethod
  def get_manager():
    from .managers import SeleniumSinglePageCrawlerManager
    return SeleniumSinglePageCrawlerManager
    
class SeleniumPageListCrawler(SeleniumBaseCrawler):
  
  def __init__(self, urlGenerator, itemSelector, spiderID, 
               spiderName, filterPredicate=None, **kwargs):
    url_generator = urlGenerator()
    SeleniumBaseCrawler.__init__(self, [next(url_generator)], spiderID, 
                                 spiderName, **kwargs)
    self.item_extractor = FilteringItemExtractor(self, filterPredicate, itemSelector, self.item_loader,
                            SpiderTypes.TYPE_SELENIUM, self.name, self._id)
    self.url_generator = urlGenerator()
    
  def start(self):
    browser = self.create_browser()
    start_url = next(self.url_generator)
    browser.get(start_url)
    if self.favicon_required:
      favicon_item = self.item_extractor.extract_favicon_item(start_url)
      self.pipeline_handler.run_pipeline(favicon_item)
    browser_response = self.response_from_browser(browser)
    start_item = self.item_extractor.extract_items(browser_response, browser)
    self.pipeline_handler.run_pipeline(start_item)
    for url in self.url_generator:
      browser.get(url)
      browser_response = self.response_from_browser(browser)
      item = self.item_extractor.extract_items(browser_response, browser)
      self.pipeline_handler.run_pipeline(item)
    browser.quit()
    self.finishoff()
    
  @staticmethod
  def get_manager():
    from .managers import SeleniumPageListCrawlerManager
    return SeleniumPageListCrawlerManager

class SeleniumProductCrawler(SeleniumBaseCrawler):
  
  def __init__(self, spiderPath, spiderID, spiderName, **kwargs):
    SeleniumBaseCrawler.__init__(self, spiderPath, spiderID, spiderName, **kwargs)
    main_page = spiderPath[-1]
    self.item_extractor = SeleniumItemExtractor(self, main_page.item_selector, 
                          self.item_loader, self.name, SpiderTypes.TYPE_SELENIUM, self._id)
    self.url_generator = ProductCrawlerUrlGenerator(main_page.item_page_selector,
                          main_page.similar_pages_selector, None, main_page.similar_pages_restrict)
    self.item_link_action = main_page.item_page_selector.action
    self.pagination_link_action = main_page.similar_pages_selector.action
    self._item_browser_established = False
    
  def start(self):
    """Manages the crawling process"""
    try:
      self._prepare_browsers()
      if self.event_handler: self.event_handler.emit(SpiderStarted(self._id))
      for step in self._spider_path:
        if isinstance(step, MainPage):
          break
        self._take_step(step)
      if self.favicon_required:
        favicon_item = self.item_extractor.extract_favicon_item(self.nav_browser.current_url)
        self.pipeline_handler.run_pipeline(favicon_item) # image items also run in the pipeline
      self._crawl_current_nav()
      more_pagination = self._get_pagination_from_nav_browser()
      while more_pagination:
        for nav_page in more_pagination:
          if self.pagination_link_action == UrlSelector.ACTION_VISIT:
            self.get_nav_browser().get(nav_page)
          elif self.pagination_link_action == UrlSelector.ACTION_CLICK:
            nav_page.click()
            self.wait(self.get_nav_browser())
          self._crawl_current_nav()
        more_pagination = self._get_pagination_from_nav_browser()
      self.finishoff()
    except KeyboardInterrupt:
      log.debug("Interrupted. Exiting...")
    except Exception as ex:
      log.error("{0} failed with an error : \n\t".format(self.name))
      traceback.print_exc()
      log.error("Exiting")
    finally:
      self.finishoff()
      
  def _get_pagination_from_nav_browser(self):
    browser_response = self.response_from_browser(self.nav_browser)
    more_nav = self.url_generator.parse_pagination_from_response(browser_response, self.nav_browser)
    return more_nav
  
  def _get_item_pages_from_nav_browser(self):
    browser_response = self.response_from_browser(self.nav_browser)
    more_nav = self.url_generator.parse_item_links_from_response(browser_response, 
                  self.nav_browser)
    return more_nav
  
  def finishoff(self):
    self.get_nav_browser().quit()
    self._close_item_browser()
    SeleniumBaseCrawler.finishoff(self)
    
  def _prepare_browsers(self):
    self.nav_browser = self.create_browser()
      
  def _create_profile(self):
    ff_profile = webdriver.FirefoxProfile()
    [ff_profile.set_preference(key, value) for key, value in self._profile_settings.items()]
    return ff_profile
  
  def _take_step(self, step):
    """Visit a url or fill a form and post it"""
    if isinstance(step, URL):
      self.get_nav_browser().get(step)
    elif isinstance(step, Form):
      form_url = step.url
      form_data = step.data
      self.get_nav_browser().get(form_url)
      for elem_info in form_data:
        elem = self.get_nav_browser().find_element_by_name(elem_info.name) 
        if elem_info.type == FormElemInfo.INPUT_TEXT:
          elem.send_keys(elem_info.value)
        elif elem_info.type == FormElemInfo.INPUT_SELECT:
          elem = Select(elem)
          elem.select_by_visible_text(elem_info.value)
      elem.submit()
      # wait for anything on the screen :)
      self.wait()
  
  def _crawl_current_nav(self):
    """Scrape all items on the current items page"""
    current_item_pages = self._get_item_pages_from_nav_browser()
    for item_page in current_item_pages:
      if self.item_link_action == UrlSelector.ACTION_VISIT:
        self.get_item_browser().get(item_page)
      elif self.item_link_action == UrlSelector.ACTION_CLICK:
        browser = self.get_item_browser(item_page) # this opens the link automatically
      time.sleep(self.download_delay) # get the delay from settings and apply it
      browser_reponse = self.response_from_browser(self._item_browser)
      item = self.item_extractor.extract_items(browser_reponse)
      self.pipeline_handler.run_pipeline(item)
      
  def get_item_browser(self, link=None):
    """Create the item browser if it isn't yet. 
       Under the current scheme, for each url click, the current item
       browser is closed and another one is opened for the link"""
    if not self._item_browser_established:
      if self.item_link_action == UrlSelector.ACTION_VISIT:
        self._item_browser = webdriver.Firefox(self._create_profile())
        self._item_browser_established = True
        return self._item_browser
      elif self.item_link_action == UrlSelector.ACTION_CLICK:
        # perform a shift-click on the link to create a new window handle and wait
        self._open_link_in_item_browser(link)
        self._item_browser_established = True
        return self.nav_browser
    else:
      if self.item_link_action == UrlSelector.ACTION_VISIT:
        return self._item_browser
      elif self.item_link_action == UrlSelector.ACTION_CLICK:
        if link is None: 
          return self.nav_browser
        # close the current item browser and open the link in a new one 
        self.nav_browser.switch_to.window(self.nav_browser.window_handles[1])
        self.nav_browser.close()
        self._open_link_in_item_browser(link)
        return self.nav_browser
      
  def get_nav_browser(self):
    """Ensure that the nav browser is brought to the focus"""
    self.nav_browser.switch_to.window(self.nav_browser.window_handles[0])
    return self.nav_browser
      
  def _close_item_browser(self):
    """Close the item browser if it independently exists"""
    if not self._item_browser_established: return
    else:    
      if self.item_link_action == UrlSelector.ACTION_CLICK: return
      elif self.item_link_action == UrlSelector.ACTION_VISIT: self._item_browser.quit()
      
  def _open_link_in_item_browser(self, link):
    """Create a new browser for the link and switch to it"""
    self.nav_browser.switch_to.window(self.nav_browser.window_handles[0])
    ActionChains(self.nav_browser).key_down(Keys.SHIFT).click(link).key_up(Keys.SHIFT).perform()
    # switch to the item browser to wait on it
    self.nav_browser.switch_to.window(self.nav_browser.window_handles[1])
    self.wait(self.nav_browser)
    
  @staticmethod
  def get_manager():
    from .managers import SeleniumProductCrawlerManager
    return SeleniumProductCrawlerManager
  