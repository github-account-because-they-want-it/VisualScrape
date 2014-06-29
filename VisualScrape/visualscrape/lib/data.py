'''
Created on Jun 19, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QAction
import cPickle as pickle, os.path as pth
import visualscrape.config as config
from visualscrape.lib.types import SpiderTypes

class ProducerMixin(object):
  """
  Defines defaults properties and methods for data producers.
  All producers that register with the data store should inherit
  from ProducerMixin
  """
  TYPE_SCALAR = 1
  TYPE_LIST = 2
  TYPE_TABLE = 3
  TYPE_TREE = 4
  
  @staticmethod
  def get_data():
    return None
  
  @staticmethod
  def get_visible_data():
    return None
  
  @staticmethod
  def is_active():
    return False
  
  @staticmethod
  def set_active():
    pass
  
  def __init__(self, *args, **kwargs):
    # producer properties that might interest consumers
    self.name = kwargs.get("name", '')
    self.type = kwargs.get("type", self.TYPE_SCALAR)
    store = DataStore.get_instance()
    store.register_producer(self)
    
  
class DataStore(list):
  """
  A place where objects interested in data meet with producers
  Acts as a list 
  """
  _instance = None
  
  def register_producer(self, producer):
    self.append(producer)
  
  @classmethod
  def get_instance(cls):
    if not cls._instance:
      cls._instance = DataStore()
    return cls._instance
  
class NamedAction(QAction):
  """The actions that need to be shared between widgets should inherit
     from this class"""
  def __init__(self, text, parent=None, **kwargs):
    super(NamedAction, self).__init__(text, parent)
    self._name = kwargs.get("name")
    
  def get_name(self):
    return self._name
  
  
class ActionStore(list):
  """A list of NamedAction instances"""
  _instance = None
  
  def register_action(self, action):
    self.append(action)
    
  @classmethod
  def get_instance(cls):
    if not cls._instance:
      cls._instance = ActionStore()
    return cls._instance
 
class SpiderConfigManager(object):
  """
  Provides an interface to spider state 
  """
  SPIDERNAME_ORDER = 1
  SPIDERTYPE_ORDER = 2
  VISITED_ORDER = 3
  @classmethod
  def updateSpiderInformation(cls, item):
    pickled_info = cls.get_config_file_for(item.get("_spidername"))
    if pth.exists(pickled_info):
      f = open(pickled_info, "rb")
      current_visited = cls._get_scraped_urls(f)
      f.close()
    else:
      current_visited = []
    new_scraped = item.get("_scrapedurl")
    current_visited.append(new_scraped)
    pickled_out = open(pickled_info, "wb")
    cls._dump_stuff(pickled_out, item, scraped=current_visited)
    pickled_out.close()
    
  @classmethod
  def is_scrapy_spider(cls, spiderName):
    config_file = open(cls.get_config_file_for(spiderName), "rb")
    spider_type = cls._get_spider_type(config_file)
    return spider_type == SpiderTypes.TYPE_SCRAPY
  
  @classmethod
  def is_selenium_spider(cls, spiderName):
    return not cls.is_scrapy_spider(spiderName)
  
  @staticmethod
  def get_config_path():
    return config.settings._CONFIG_PATH
  
  @classmethod
  def get_config_file_for(cls, spiderName):
    config_file = spiderName.lower() + ".bin"
    return pth.join(cls.get_config_path(), config_file)
    
  @classmethod
  def get_info_file_for(cls, spiderName):
    """The info file contains currently the SpiderInfo object"""
    info_file = spiderName.lower() + "_info.bin" # this info file holds the SpiderInfo object
    return pth.join(cls.get_config_path(), info_file)
    
  @classmethod
  def config_exists_for(cls, spiderName):
    return pth.exists(cls.get_config_file_for(spiderName))
    
  @classmethod
  def _get_spider_type(cls, configFile):
    pickle.load(configFile)
    return pickle.load(configFile)
  
  @classmethod
  def _get_scraped_urls(cls, configFile):
    for _ in range(cls.VISITED_ORDER):
      res = pickle.load(configFile)
    return res
  
  @classmethod
  def _dump_stuff(cls, pickleFile, item, **kwargs):
    """The central function to make a complete config dump"""
    pickleFile.dump(item.get("_spidername"))
    pickleFile.dump(item.get("_spidertype"))
    visited = kwargs.get("scraped")
    if visited: pickleFile.dump(visited)
    