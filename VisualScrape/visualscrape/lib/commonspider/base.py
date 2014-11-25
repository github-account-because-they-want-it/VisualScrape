'''
Created on Jun 18, 2014
@author: Mohammed Hamdy
'''

import cPickle as pickle, os, sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from scrapy.http import TextResponse
from visualscrape import settings
from visualscrape.config.util import get_url_params, get_item_loader_for
from visualscrape.lib.data import SpiderConfigManager
from visualscrape.lib.event_handler import EventConfigurator
from visualscrape.lib.pipeline_handler import PipelineHandler
from visualscrape.lib.signal import SpiderClosed
from visualscrape.lib.seleniumlib import log

class BaseCrawler(EventConfigurator):
  """Operations and attributes common to spiders"""
  
  def __init__(self, spiderPath=[], spiderName='', spiderID=-1, **kwargs):
    EventConfigurator.__init__(self, kwargs.get("handler"))
    self.favicon_required = settings.getbool("DOWNLOAD_FAVICON") 
    self.item_loader = get_item_loader_for(spiderPath[0])
    self.conf = get_url_params(spiderPath[0])
    self.download_delay = self.conf.getint("DOWNLOAD_DELAY", 1)
    self._spider_path = spiderPath
    self._id = spiderID
    self.name = spiderName
  
  def temp_pause(self):
    self._temp_paused = True # this should be checked in spider code
    
  def temp_resume(self):
    self._temp_paused = False
    
  def pause(self):
    """A pause that prepares the spider for a later resume"""
    # save the spider info to disk, to be able to recover it
    info_file = open(SpiderConfigManager.get_info_file_for(self.name), "wb")
    pickle.dump(self._spider_info, info_file)
    info_file.close()
    
  @staticmethod
  def resume(spiderName):
    # you may want to enlist all your crawlers here
    """
    SeleniumManager.resume_spider(spiderName)
    ScrapyProductCrawlerManager.resume_spider(spiderName)
    """
    
  def stop(self, keepState=True):
    if not keepState:
      # delete the configuration file for the spider
      os.remove(SpiderConfigManager.get_config_file_for(self.name))
    self._stopped = True

class SeleniumBaseCrawler(BaseCrawler): 
  """
  Adds pipeline handling capabilities needed by selenium spiders
  """ 
  
  def __init__(self, spiderPath=[], spiderName='', spiderID=-1, **kwargs):
    BaseCrawler.__init__(spiderPath, spiderName, spiderID, **kwargs)
    self.pipeline_handler = PipelineHandler(self) # the pipelines need access to the spider
    self._profile_settings = {}
    # get browser profile-influencing options 
    crawl_params = get_url_params(self._spider_path[0])
    if crawl_params.get("COOKIES_ENABLED", True) is False:
      self._profile_settings["network.cookie.cookieBehavior"] = 1
    if crawl_params.get("IMAGES_ENABLED", True) is False:
      self._profile_settings["permissions.default.image"] = 2 # could also be 1 with some older firefox versions
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
    
  def create_browser(self):
    # check conf for our start url
    return webdriver.Firefox(self._create_profile())
      
  def _create_profile(self):
    ff_profile = webdriver.FirefoxProfile()
    [ff_profile.set_preference(key, value) for key, value in self._profile_settings.items()]
    return ff_profile
  
  def response_from_browser(self, browser):
    response = TextResponse(browser.current_url, body=browser.page_source, encoding="utf-8")
    return response
  
  def enable_JQuery_on(self, browser):
    already_jquery =  browser.execute_script("return typeof jQuery == 'undefined'")
    if not already_jquery:
      browser.execute_script("""var jq = document.createElement('script');
      jq.src = '//code.jquery.com/jquery-1.11.0.min.js';
      document.getElementsByTagName('head')[0].appendChild(jq);
      """)
  
  def wait(self, browser, elem="body"):
    try: 
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.TAG_NAME, elem)))
    except TimeoutException:
      log.error("Scraping timed out for: %s ... exiting" % browser.current_url)
      self.finishoff()
      sys.exit(1)
  
  def finishoff(self):
    self._display.stop() if self._display else None
    self.event_handler.emit(SpiderClosed(self._id))