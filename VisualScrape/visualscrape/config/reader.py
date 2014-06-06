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

class SettingsReader(object):
  __metaclass__ = SingletonMeta
  """
  Makes the _settings available for clients and controls
  the overall access
  """
  
  def __init__(self):
    self._settings = [Setting(setting_name) for setting_name in settings.__dict__ 
                     if not setting_name.startswith("__")] #skip Python's special attributes
    
  def nextSetting(self, settingName):
    """
    Retrieves the next _value of the requested setting, otherwise None, if
    no such setting or setting is exhausted
    """  
    for setting in self._settings:
      if setting.name == settingName:
        return setting.nextValue()
      
  def __getattr__(self, attr):
    """Support reading arbitrary settings by attribute access on this object"""
    if getattr(settings, attr):
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
    if type(self._value) == dict or type(self._value) == list:
      self.iterable = True
    if type(self._value) == dict:
      # turn it into a sorted list and discard the values, as we will no longet need them
      keys = list(self._value.keys())
      vals = list(self._value.values())
      keys_vals_zip = list(zip(keys, vals))
      keys_vals_zip.sort(key=lambda item: item[1]) # sort by dict values
      self._value = [item[0] for item in keys_vals_zip] # our interest is the keys
      
  def value(self):
    return self._value
  
  def nextValue(self):
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
    
  def valueFromIndex(self, index):
    return self._value[index]
  
  def load_components(self):
    components = [load_object(component) for component in self]
    return components
      
  def __iter__(self):
    return self
  
  def next(self):
    return self.nextValue()
  
  def __str__(self):
    return "<Setting {0}>".format(self.name)