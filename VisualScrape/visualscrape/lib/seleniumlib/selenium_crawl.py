'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from threading import Thread
from visualscrape.config import settings
from visualscrape.lib.path import URL, Form, FormElemInfo, MainPage
from visualscrape.lib.seleniumlib import log
from visualscrape.lib.signal import *
import sys, time, traceback
from visualscrape.lib.selector import UrlSelector
from visualscrape.lib.event_handler import EventConfigurator
from visualscrape.lib.commonspider.base import CommonCrawler
from visualscrape.lib.seleniumlib.handler import SeleniumDataHandlerMixin
from visualscrape.lib.data import SpiderConfigManager

class SeleniumCrawler(EventConfigurator, CommonCrawler, SeleniumDataHandlerMixin):
  LINK_TYPE_CLICK = 1
  LINK_TYPE_GET = 2
  
  def __init__(self, spiderInfo, spiderID, **kwargs):
    EventConfigurator.__init__(self, spiderInfo, spiderID, **kwargs)
    CommonCrawler.__init__(self, spiderInfo, spiderID, kwargs)
    SeleniumDataHandlerMixin.__init__(self)
    self._profile_settings = {}
    self._item_browser_established = False
    self._link_types = None
    self._terminated = False
    
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
        favicon_item = self.favicon_item() #send it to the item-scraped handler
      self._crawl_current_nav()
      more_nav, action = self.more_navigation_pages()
      while more_nav:
        for nav_page in more_nav:
          if action == UrlSelector.ACTION_VISIT:
            self.get_nav_browser().get(nav_page)
          elif action == UrlSelector.ACTION_CLICK:
            nav_page.click()
            self._wait(self.get_nav_browser())
          self._crawl_current_nav()
        more_nav = self.more_navigation_pages()
      self._finishoff()
    except KeyboardInterrupt:
      log.debug("Interrupted. Exiting...")
    except Exception as ex:
      log.error("{0} failed with an error : \n\t".format(self.name))
      traceback.print_exc()
      log.error("Exiting")
    finally:
      self._finishoff()
  
  def resume(self):
    self._prepare_browsers()
    self.resume()
    self.start()
  
  def _finishoff(self):
    self.get_nav_browser().quit()
    self._close_item_browser()
    self._display.stop() if self._display else None
    self._stop()
    if self.event_handler: self.event_handler.emit(SpiderClosed(self._id))
    
  def _prepare_browsers(self):
    # check settings for our start url
    if settings.SITE_PARAMS.by(self._spider_path[0]).get("COOKIES_ENABLED", True) is False:
      self._profile_settings["network.cookie.cookieBehavior"] = 1
    if settings.SITE_PARAMS.by(self._spider_path[0]).get("IMAGES_ENABLED", True) is False:
      self._profile_settings["permissions.default.image"] = 2 # could also be 1 with some older firefox versions
    self.nav_browser = webdriver.Firefox(self._create_profile())
    #try to run headless on linux
    if sys.platform.startswith("linux"):
      try:
        from pyvirtualdisplay import Display
        self._display = Display(visible=0, size=(800, 600)) 
        self._display.start()
      except ImportError: #linux but no pyvirtualdisplay
        self._display = None
    else:
      self._display = None
      
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
      self._wait()
  
  def _crawl_current_nav(self):
    """Scrape all items on the current items page"""
    current_item_pages, action = self.item_pages()
    for item_page in current_item_pages:
      # clean termination
      if self._terminated:
        self._finishoff()
        return
      if action == UrlSelector.ACTION_VISIT:
        self.get_item_browser().get(item_page)
      elif action == UrlSelector.ACTION_CLICK:
        item_browser = self.get_item_browser(item_page, action) # this opens the link automatically
      time.sleep(self.request_delay) # get the delay from settings and apply it
      item = self.next_item()
      
  def _wait(self, browser, elem="body"):
    try: 
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.TAG_NAME, elem)))
    except TimeoutException:
      log.error("Scraping timed out for: %s ... exiting" % browser.current_url)
      self._finishoff()
      sys.exit(1)
      
  def get_item_browser(self, link=None, action=UrlSelector.ACTION_VISIT):
    """Create the item browser if it isn't yet. 
       Under the current scheme, for each url click, the current item
       browser is closed and another one is opened for the link"""
    if not self._item_browser_established:
      if action == UrlSelector.ACTION_VISIT:
        self._item_browser = webdriver.Firefox(self._create_profile())
        self._link_types = self.LINK_TYPE_GET
        self._item_browser_established = True
        return self._item_browser
      elif action == UrlSelector.ACTION_CLICK:
        self._link_types = self.LINK_TYPE_CLICK
        # perform a shift-click on the link to create a new window handle and wait
        self._open_link_in_item_browser(link)
        self._item_browser_established = True
        return self.nav_browser
    else:
      if self._link_types == self.LINK_TYPE_GET:
        return self._item_browser
      elif self._link_types == self.LINK_TYPE_CLICK:
        if link is None: # this request comes from the data handler. So the link is already opened and on the front
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
      if self._link_types == self.LINK_TYPE_CLICK: return
      elif self._link_types == self.LINK_TYPE_GET: self._item_browser.quit()
      
  def _open_link_in_item_browser(self, link):
    """Create a new browser for the link and switch to it"""
    self.nav_browser.switch_to.window(self.nav_browser.window_handles[0])
    ActionChains(self.nav_browser).key_down(Keys.SHIFT).click(link).key_up(Keys.SHIFT).perform()
    # switch to the item browser to wait on it
    self.nav_browser.switch_to.window(self.nav_browser.window_handles[1])
    self._wait(self.nav_browser)
    
  def terminate(self):
    # terminate without keeping state
    self._terminated = True
    
  @staticmethod
  def get_manager():
    return SeleniumManager
  

class SeleniumManager(object):
  
  def __init__(self, spidersInfo):
    self.spiders_info = spidersInfo
    self.crawler_id_to_config_map = {}
    for (spid, sp_info) in enumerate(spidersInfo):
      # start ids at 100 for selenium to make it's ids distinct from scrapy. 
      # TODO: read the start _id from settings
      self.config_spider(spid, sp_info)
      
  def config_spider(self, spid, sp_info):
    crawler = SeleniumCrawler(sp_info, spid + 100)
    crawl_thread = Thread(target=crawler.start, name="SeleniumThread#{0}".format(spid + 1))
    self.crawler_id_to_config_map[spid] = {"info":sp_info, "thread":crawl_thread, "spider":crawler}
      
  def start_all(self):
    for crawl_config in self.crawler_id_to_config_map.values(): 
      crawl_thread = crawl_config["thread"]
      crawl_thread.start()
  
  def stop_spider(self, spiderID, keepState):
    if not spiderID in self.crawler_id_to_config_map:
      return
    else:
      config_to_stop = self.crawler_id_to_config_map[spiderID]
      spider_to_stop = config_to_stop["spider"]
      spider_to_stop.terminate(keepState)    # because there's no thread termination
      
  def restart_spider(self, spiderID, keepState=True):
    if not spiderID in self.crawler_id_to_config_map:
      return
    self.stop_spider(spiderID, keepState)
    prev_config = self.crawler_id_to_config_map.pop(spiderID)
    prev_info = prev_config["info"]
    self.config_spider(spiderID, prev_info)
    self.crawler_id_to_config_map[spiderID]["thread"].start()
    
  def temp_pause_spider(self, spiderID):
    if self.spider_belongs(spiderID):
      spider_to_pause = self.crawler_id_to_config_map[spiderID]["spider"]
      spider_to_pause.data_handler.temp_pause() # avoid adding temp_pause method to the spider
      
  def temp_resume_spider(self, spiderID):
    if self.spider_belongs(spiderID):
      spider_to_resume = self.crawler_id_to_config_map[spiderID]
      spider_to_resume.data_handler.temp_resume()
      
  def spider_belongs(self, spiderID):
    return spiderID in self.crawler_id_to_config_map
  
  def resume_spider(self, spiderName):
    # the spider is resumed by it's name because this is what's on disk
    if SpiderConfigManager.is_selenium_spider(spiderName):
      spid = max(self.crawler_id_to_config_map.keys()) + 1 # the new spider id
      self.config_spider(spid, sp_info=None)
      spider_config = self.crawler_id_to_config_map[spid]
      spider_config["thread"].start()