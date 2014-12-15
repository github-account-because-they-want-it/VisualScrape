'''
Created on Jun 28, 2014
@author: Mohammed Hamdy
'''
from __future__ import division
from PySide.QtCore import Signal

class ItemWatcher(object):
  
  finished = Signal(bool)
  PERCENT_TOO_HIGH = 40 # meaning error rate too high
  
  def __init__(self):
    self._received_items = 0
    self._missing_to_total_sum = 0
    
  def take_item(self, item):
    self._received_items += 1
    item_fields = item.fields
    field_count = len(item_fields)
    empty_values = 0
    for value in item.values():
      if not value:
        empty_values += 1
    self._missing_to_total_sum += empty_values / field_count
    
  def use_scrapy(self):
    return self._missing_to_total_sum / self._received_items * 100 < self.PERCENT_TOO_HIGH
  
  def spider_done(self, spider):
    self.finished.emit(self.use_scrapy())
    