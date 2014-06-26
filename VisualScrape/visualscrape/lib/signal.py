'''
Created on May 28, 2014
@author: Mohammed Hamdy
'''
class Signal(object): pass

class SpiderStarted(Signal):
  def __init__(self, _id):
    self._id = _id
    
class SpiderStopped(Signal):
  def __init__(self, _id):
    self._id = _id

class SpiderClosed(Signal):
  def __init__(self, _id):
    self._id = _id

class SpiderSwiched(Signal): pass

class ItemScraped(Signal): pass

