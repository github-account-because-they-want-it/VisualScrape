'''
Created on Jun 5, 2014
@author: Mohammed Hamdy
'''
from __future__ import print_function
import sys
from scrapy.exceptions import DropItem
from visualscrape.config import settings
from scrapy.contrib.pipeline.images import ImagesPipeline

class PipelineHandler(object):
  """Since it seems that Scrapy pipelining is tightly integrated with it, I'll
     do simple pipeline handling here for the items. I'll only handle the 
     process_item method
     This should only be used with non-scrapy crawlers"""
     
  def __init__(self, spider):
    """Initialize all the pipelines"""
    self.spider = spider
    pipelines = settings.ITEM_PIPELINES
    pipeline_classes = pipelines.load_components()
    self._pipeline_objects = [pl() for pl in pipeline_classes if not pl == ImagesPipeline]
    
  def run_pipeline(self, item):
    # note: this process is exactly like folding
    for pipeline in self._pipeline_objects:
      try:
        item = pipeline.process_item(item, spider=self.spider)
        if not item: break
      except DropItem as di:
        break
    return item #whether an item or None