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

class SeleniumCrawler(EventConfigurator):
  LINK_TYPE_CLICK = 1
  LINK_TYPE_GET = 2
  
  def __init__(self, spiderInfo, spiderID, *args, **kwargs):
    super(SeleniumCrawler, self).__init__(spiderInfo, spiderID, *args, **kwargs)
    self._spider_info = spiderInfo
    self.path = spiderInfo.spider_path
    self.id = spiderID
    self.name = spiderInfo.spider_name
    self.favicon_required = kwargs.get("downloadFavicon", True)
    self.item_loader = kwargs.get("itemLoader")
    self.data_handler = None
    self._item_browser_established = False
    self._link_types = None
    
  def start(self):
    """Manages the crawling process"""
    try:
      self._prepare_browsers()
      if self.event_handler: self.event_handler.emit(SpiderStarted(self.id))
      for step in self.path:
        if isinstance(step, MainPage):
          break
        self._take_step(step)
      if self.favicon_required:
        favicon_item = self.data_handler.favicon_item() #send it to the item-scraped handler
      self._crawl_current_nav()
      more_nav, action = self.data_handler.more_navigation_pages()
      while more_nav:
        for nav_page in more_nav:
          if action == UrlSelector.ACTION_VISIT:
            self.get_nav_browser().get(nav_page)
          elif action == UrlSelector.ACTION_CLICK:
            nav_page.click()
            self._wait(self.get_nav_browser())
          self._crawl_current_nav()
        more_nav = self.data_handler.more_navigation_pages()
      self._finishoff()
    except KeyboardInterrupt:
      log.debug("Interrupted. Exiting...")
    except Exception as ex:
      log.error("{0} failed with an error : \n\t".format(self.name))
      traceback.print_exc()
      log.error("Exiting")
    finally:
      self._finishoff()
  
  def _finishoff(self):
    self.get_nav_browser().quit()
    self._close_item_browser()
    self._display.stop() if self._display else None
    if self.event_handler: self.event_handler.emit(SpiderClosed(self.id))
    
  def _prepare_browsers(self):
    # check settings for our start url
    from visualscrape.lib.seleniumlib.handler import SeleniumDataHandler
    profile=None
    if settings.SITE_PARAMS.by(self.path[0]).get("COOKIES_ENABLED", None) is False:
      profile = webdriver.FirefoxProfile(profile_directory=r"C:\Users\Tickler\AppData\Local\Temp\prof_dir")
      profile.set_preference("network.cookie.cookieBehavior", 1)
    self.nav_browser = webdriver.Firefox(firefox_profile=profile)
    self.data_handler = SeleniumDataHandler(self, self.path, 
                                            self.id, self.item_loader)
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
    current_item_pages, action = self.data_handler.item_pages()
    for item_page in current_item_pages:
      if action == UrlSelector.ACTION_VISIT:
        self.get_item_browser().get(item_page)
      elif action == UrlSelector.ACTION_CLICK:
        item_browser = self.get_item_browser(item_page, action) # this opens the link automatically
      time.sleep(settings.SITE_PARAMS.by(self.nav_browser.current_url).get("REQUEST_DELAY", 0)) # get the delay from settings and apply it
      item = self.data_handler.next_item()
      
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
        self._item_browser = webdriver.Firefox()
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
    
  @staticmethod
  def get_manager():
    return SeleniumManager
  

class SeleniumManager(object):
  
  def __init__(self, spidersInfo):
    self.spiders_info = spidersInfo
    self.crawler_id_to_thread_map = {}
    for (spid, sp_info) in enumerate(spidersInfo):
      # start ids at 100 for selenium to make it's ids distinct from scrapy. 
      # TODO: read the start id from settings
      spid = spid + 100
      crawler = SeleniumCrawler(sp_info, spid, 
                                downloadFavicon=settings.DOWNLOAD_FAVICON.value(),
                                itemLoader=settings.get_item_loader_for(sp_info.spider_path[0]))
      crawl_thread = Thread(target=crawler.start, name="SeleniumThread#{0}".format(spid + 1))
      self.crawler_id_to_thread_map[spid] = crawl_thread
      
  def start_all(self):
    for crawl_thread in self.crawler_id_to_thread_map.values(): 
      crawl_thread.start()
  
  def stop_spider(self, spiderID):
    if not spiderID in self.crawler_id_to_thread_map:
      return
    else:
      thread_to_stop = self.crawler_id_to_thread_map[spiderID]
      thread_to_stop.terminate()
      thread_to_stop.join()    