'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''
"""
As it turns out, this module might be totally useless. 
Scrapy has scrapy.settings.Settings
"""
from visualscrape.lib.util import Singleton
from visualscrape import settings

@Singleton
class SettingsReader(object):
  """
  Makes the settings available for clients and controls
  the overall access
  """
  SCRAPER_CLASSES = "SCRAPER_CLASSES"
  ITEM_LOADER = "ITEM_LOADER"
  def __init__(self):
    self.settings = [Setting(setting_name) for setting_name in settings.__dict__ 
                     if not setting_name.startswith("__")] #skip Python's special attributes
    
  def nextSetting(self, setting):
    """
    Retrieves the next value of the requested setting, otherwise None, if
    no such setting or setting is exhasted
    """  
    for setting in self.settings:
      if setting.name == setting:
        return setting.nextValue()
      
  def __getattr__(self, attr):
    """Support reading arbitrary settings by attribute access on this object"""
    if attr.startswith('_'):
      return self.__dict__[attr] 
    if getattr(settings, attr):
      return getattr(settings, attr)
    else:
      raise ValueError("Setting undefined: <%s>" % attr)
    

class Setting(object):
  """Wraps a single setting from the file. Reads the
     setting and cycles through it's values when applicable
  """
  
  def __init__(self, name, settingsModule=settings, circular=False):
    self.name = name
    self.circular = circular #whether to return the first setting after exhausting all of them or not
    # read my value from the module and configure accordingly
    self.iterable = False
    self.index = 0
    self.value = getattr(settingsModule, self.name)
    if type(self.value) == dict or type(self.value) == list:
      self.iterable = True
    
  def nextValue(self):
    if not self.iterable:
      raise TypeError("Setting <{0}> is not iterable".format(self.name))
    elif self.index == len(self.value):
      if not self.circular:
        raise StopIteration("Values for setting <{0}> exhausted".format(self.name))
      else:
        self.index = 0
        return self.valueFromIndex(self.index)
    elif self.index < len(self.value):
      self.index += 1
      return self.valueFromIndex(self.index - 1)
    
  def valueFromIndex(self, index):
    for (key, value) in self.value.items():
      if key == index:
        return value
      
  def __iter__(self):
    return self
  
  def next(self):
    return self.nextValue()