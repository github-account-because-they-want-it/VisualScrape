'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from multiprocessing import Process
from visualscrape.lib.path import URL, Form, FormElemInfo, MainPage
from visualscrape.lib.seleniumlib.handler import SeleniumDataHandler
from visualscrape.lib.seleniumlib import log
from visualscrape.lib.signal import *
import sys
from visualscrape.lib.selector import UrlSelector

class SeleniumCrawler(object):
  
  def __init__(self, spiderPath, spiderID, name="SeleniumCrawler", *args, **kwargs):
    self.path = spiderPath
    self.id = spiderID
    self.name = name
    self.favicon_required = kwargs.get("downloadFavicon", True)
    self.event_handler = kwargs.get("eventHandler", None)
    if self.event_handler: self.event_handler.set_spider(self)
    self.data_handler = None
    
  def start(self):
    """Manages the crawling process"""
    self._prepare_browsers()
    if self.event_handler: self.event_handler.emit(SpiderStarted(self.id))
    for step in self.path:
      if isinstance(step, MainPage):
        break
      self._take_step(step)
    if self.favicon_required:
      favicon_item = self.data_handler.favicon_item() #send it to the item-scraped handler
      if self.event_handler: self.event_handler.emit(ItemScraped(), item=favicon_item)
    self._crawl_current_nav()
    more_nav, action = self.data_handler.more_navigation_pages()
    while more_nav:
      for nav_page in more_nav:
        if action == UrlSelector.ACTION_VISIT:
          self.nav_browser.get(nav_page)
        elif action == UrlSelector.ACTION_CLICK:
          nav_page.click()
          self._wait(self.nav_browser)
        self._crawl_current_nav()
      more_nav = self.data_handler.more_navigation_pages()
    self._finishoff()
  
  def _finishoff(self):
    self.nav_browser.quit()
    self.item_browser.quit()
    self._display.stop() if self._display else None
    if self.event_handler: self.event_handler.emit(SpiderClosed(self.id))
    
  def _prepare_browsers(self):
    self.nav_browser = webdriver.Firefox()
    self.item_browser = webdriver.Firefox()
    self.data_handler = SeleniumDataHandler(self.nav_browser, self.item_browser, self.path, self.id)
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
      self.nav_browser.get(step)
    elif isinstance(step, Form):
      form_url = step.url
      form_data = step.data
      self.nav_browser.get(form_url)
      for elem_info in form_data:
        elem = self.nav_browser.find_element_by_name(elem_info.name) 
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
        self.item_browser.get(item_page)
      elif action == UrlSelector.ACTION_CLICK:
        item_page.click()
        self._wait(self.item_browser)
      item = self.data_handler.next_item()
      if self.data_handler: self.event_handler.emit(ItemScraped(), item=item)
      
  def _wait(self, browser, elem="body"):
    try: 
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.TAG_NAME, elem)))
    except TimeoutException:
      log.error("Scraping timed out for: %s ... exiting" % browser.current_url)
      self._finishoff()
      sys.exit(1)
    
  @staticmethod
  def get_manager():
    return SeleniumManager
  

class SeleniumManager(object):
  
  def __init__(self, spidersInfo):
    self.spiders_info = spidersInfo
    self.crawlers = []
    for (id, sp_info) in enumerate(spidersInfo):
      # start ids at 100 for selenium to make it's ids distinct from scrapy. 
      # TODO: read the start id from settings
      crawler = SeleniumCrawler(sp_info.spider_path, id+100, sp_info.spider_name, eventHandler=sp_info.event_handler)
      self.crawlers.append(crawler)
      
  def start_all(self):
    for crawler in self.crawlers: 
      #crawl_process = Process(target=crawler.start, args=())
      #crawl_process.start()
      crawler.start()