'''
Created on Jun 19, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QAction

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