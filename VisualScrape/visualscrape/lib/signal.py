'''
Created on May 28, 2014
@author: Mohammed Hamdy
'''
class Signal(object):
  """Defines constants for supported signals"""
  
  SPIDER_STARTED = 1
  SPIDER_STOPPED = 2
  SPIDER_CLOSED = 3
  ITEM_SCRAPED   = 4
  SPIDER_ERROR   = 5
  SPIDER_SWITCHED = 6