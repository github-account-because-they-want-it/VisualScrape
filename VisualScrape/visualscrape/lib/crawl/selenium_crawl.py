'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys

class SeleniumCrawler(object):
  
  def __init__(self, spiderPath, name="SeleniumCrawler"):
    self._path = spiderPath
    self.name = name
    self.browser = webdriver.Firefox()
    #try to run headless on linux
    if sys.platform.startswith("linux"):
      try:
        from pyvirtualdisplay import Display
        self._display = Display(visible=0, size=(800, 600)) 
        self._display.start()
      except ImportError: #linux but no pyvirtualdisplay
        self._display = None
    