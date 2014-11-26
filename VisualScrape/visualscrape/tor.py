'''
Created on Nov 26, 2014
@author: Mohammed Hamdy
'''

from stem import Signal
from stem.control import Controller

class TorManager(object):
  """
  Manages the Tor protocol for clients
  This is a singleton class
  """
  
  _instance = None
  
  def __init__(self, controlPort=9051):
    self._controller = Controller.from_port(port=controlPort)
    self._controller.authenticate()
  
  def refresh_circuit(self):
    #ref : https://stem.torproject.org/faq.html#how-do-i-request-a-new-identity-from-tor
    self._controller.signal(Signal.NEWNYM)
    
  @classmethod
  def get_instance(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = TorManager(*args, **kwargs)
    return cls._instance