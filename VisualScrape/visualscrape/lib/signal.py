'''
Created on May 28, 2014
@author: Mohammed Hamdy
'''
class Signal(object): pass

class SpiderStarted(Signal):
  def __init__(self, id):
    self.id = id
    
class SpiderStopped(Signal):
  def __init__(self, id):
    self.id = id

class SpiderClosed(Signal):
  def __init__(self, id):
    self.id = id

class SpiderSwiched(Signal): pass

class ItemScraped(Signal): pass

