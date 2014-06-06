'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from multiprocessing import Process
from visualscrape.lib.path import URL, Form, FormElemInfo, MainPage
from visualscrape.lib.seleniumlib.handler import SeleniumDataHandler
from visualscrape.lib.signal import *
import sys

class SeleniumCrawler(object):
  
  def __init__(self, spiderPath, spiderID, name="SeleniumCrawler", *args, **kwargs):
    self.path = spiderPath
    self.id = spiderID
    self.name = name
    self.favicon_required = kwargs.get("downloadFavicon", True)
    self.event_handler = kwargs.get("eventHandler", None)
    self.event_handler.set_spider(self)
    self.data_handler = None
    
  def start(self):
    """Manages the crawling process"""
    self._prepare_browsers()
    self.event_handler.emit(SpiderStarted(self.id))
    for step in self.path:
      if isinstance(step, MainPage):
        break
      self._take_step(step)
    if self.favicon_required:
      favicon_item = self.data_handler.favicon_item() #send it to the item-scraped handler
      self.event_handler.emit(ItemScraped(), item=favicon_item)
    self._crawl_current_nav()
    more_nav = self.data_handler.more_navigation_pages()
    while more_nav:
      for nav_page in more_nav:
        self.nav_browser.get(nav_page)
        self._crawl_current_nav()
      more_nav = self.data_handler.more_navigation_pages()
    self._finishoff()
  
  def _finishoff(self):
    self.nav_browser.quit()
    self.item_browser.quit()
    self._display.stop() if self._display else None
    self.event_handler.emit(SpiderClosed(self.id))
    
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
          elem.send_keys(elem_info._value)
        elif elem_info.type == FormElemInfo.INPUT_SELECT:
          elem = Select(elem)
          elem.select_by_visible_text(elem_info._value)
  
  def _crawl_current_nav(self):
    """Scrape all items on the current items page"""
    current_item_pages = self.data_handler.item_pages()
    for item_page in current_item_pages:
      self.item_browser.get(item_page)
      item = self.data_handler.next_item()
      self.event_handler.emit(ItemScraped(), item=item)
    
  @staticmethod
  def get_manager():
    return SeleniumManager
  

class SeleniumManager(object):
  
  def __init__(self, spidersInfo):
    self.spiders_info = spidersInfo
    self.crawlers = []
    for (id, sp_info) in enumerate(spidersInfo):
      crawler = SeleniumCrawler(sp_info.spider_path, id, sp_info.spider_name, eventHandler=sp_info.event_handler)
      self.crawlers.append(crawler)
      
  def start_all(self):
    for crawler in self.crawlers: 
      crawl_process = Process(target=crawler.start, args=())
      crawl_process.start()
    #probably you want to create a process for each spider to run in. It's going to block a lot of shit
    """Now, I want to manage the multiprocessing stuff.
    With scrapy it's gonna be complicated, So I'll use the same process for all spiders.
    With selenium, A process for each spider will be optimal."""