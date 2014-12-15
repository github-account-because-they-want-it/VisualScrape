'''
Created on Jun 5, 2014
@author: Mohammed Hamdy
'''
from __future__ import print_function
from scrapy.exceptions import DropItem
from scrapy.utils.misc import load_object
from visualscrape import settings
from scrapy.contrib.pipeline.images import ImagesPipeline
from visualscrape.config.util import get_sorted_pipelines


class PipelineHandler(object):
  """Since it seems that Scrapy pipelining is tightly integrated with twisted, I'll
     do simple pipeline handling here for the items. I'll only handle the 
     process_item method
     This should only be used with non-scrapy crawlers"""
     
  def __init__(self, spider):
    """Initialize all the pipelines"""
    self.spider = spider
    pipeline_classes = get_sorted_pipelines()
    # ImagesPipeline doesn't have process_item method
    self._pipeline_objects = [pl() for pl in pipeline_classes if not pl == ImagesPipeline]
    
  def run_pipeline(self, item):
    # note: this process is exactly like folding
    if item is None: return
    for pipeline in self._pipeline_objects:
      try:
        item = pipeline.process_item(item, spider=self.spider)
        if not item: break
      except DropItem as di:
        return {} # items are dict-like
    return item