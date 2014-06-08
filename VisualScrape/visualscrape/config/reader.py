'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''
"""
As it turns out, this module might be totally useless. 
Scrapy has scrapy._settings.Settings
"""
from scrapy.utils.misc import load_object
from visualscrape.lib.util import SingletonMeta
from visualscrape import settings
from urlparse import urlparse

class SettingsReader(object):
  __metaclass__ = SingletonMeta
  """
  Makes the _settings available for clients and controls
  the overall access
  """
  
  def __init__(self):
    pass
    
  def nextSetting(self, settingName):
    """
    Retrieves the next value of the requested setting, otherwise None, if
    no such setting or setting is exhausted
    """  
    for setting in self._settings:
      if setting.name == settingName:
        return setting.nextValue()
      
  def __getattr__(self, attr):
    """Support reading arbitrary settings by attribute access on this object"""
    if hasattr(settings, attr):
      return Setting(attr)
    else:
      raise ValueError("Setting undefined: <%s>" % attr)
    

class Setting(object):
  """Wraps a single setting from the file. Reads the
     setting and cycles through it's values when applicable
  """
  
  def __init__(self, name, settingsModule=settings, circular=False):
    self.name = name
    self.circular = circular #whether to return the first setting after exhausting all of them or not
    # read my _value from the module and configure accordingly
    self.iterable = False
    self.index = 0
    self._value = getattr(settingsModule, self.name)
    self._handler = SettingHandler(self.name, self._value)
    if type(self._value) == dict or type(self._value) == list:
      self.iterable = True
      
  def value(self):
    return self._value
    
  def valueFromIndex(self, index):
    return self._value[index]
  
  def __getattr__(self, attr):
    """"
    Any unsupported request is to be handed off to the handler 
    """
    return getattr(self._handler, attr)
      
  def __iter__(self):
    return self
  
  def next(self):
    if not self.iterable:
      raise TypeError("Setting <{0}> is not iterable".format(self.name))
    elif self.index == len(self._value):
      if not self.circular:
        raise StopIteration("Values for setting <{0}> exhausted".format(self.name))
      else:
        self.index = 0
        return self.valueFromIndex(self.index)
    elif self.index < len(self._value):
      self.index += 1
      return self.valueFromIndex(self.index - 1)
  
  def __str__(self):
    return "<Setting {0}>".format(self.name)
  
class SettingHandler(object):
  """
  Freely handlers specific settings that would otherwise have utility functions to handle their values
  """
  
  def __init__(self, name, value):
    self._name = name
    self._value = value
    
  def load_components(self):
    """for SCRAPER_CLASSES and the like. loads an object from a string"""
    assert self._name in ["SCRAPER_CLASSES", "ITEM_PIPELINES"], "Unsupported operation on {0}: {1}".\
                          format(self._name, "load_components")
    value = self._value
    if type(value) == dict:
      # turn it into a sorted list and discard the values, as we will no longet need them
      keys = list(value.keys())
      vals = list(value.values())
      keys_vals_zip = list(zip(keys, vals))
      keys_vals_zip.sort(key=lambda item: item[1]) # sort by dict values ascending
      self._value = [item[0] for item in keys_vals_zip] # our interest is the keys
    components = [load_object(component) for component in value]
    return components
  
  def by(self, url):
    """for SITE_PARAMS. Takes a url and returns suitable dict"""
    assert self._name in ["SITE_PARAMS"], "Unsupported operation on {0}: {1}".format(self._name, "by")
    parsed = urlparse(url)
    domain_in = parsed.netloc
    for url_v, params in self._value.items():
      parsed_v = urlparse(url_v)
      if parsed_v.netloc == domain_in:
        return params