'''
Created on May 28, 2014
@author: Mohammed Hamdy
'''
import os
from visualscrape.lib.signal import ItemScraped
from visualscrape.lib.selector import Merge
from visualscrape.lib.data import SpiderConfigManager
from visualscrape import settings

class FilterFieldsPipeline(object):
  """
  Remove unwanted? fields in the result like image_urls
  Assuming the images from the image pipeline get processed
  immediately, not after the whole pipeline is traversed.
  """
  
  def process_item(self, item, spider):
    if item.get("image_urls"):
      item.pop("image_urls")
    if item.get("_postinfo"):
      item.pop("_postinfo")
      
    return item


class CanonicalizeImagePathPipeline(object):
  """Images "path" field returned from scrapy is not canonicalized, making
     it useless to locate the image"""
  
  def process_item(self, item, spider):
    images = item.get("images", None)
    if images:
      for image in images:
        image_path = os.path.normpath(image.get("path"))
        parent_folder = os.path.normpath(settings.get("IMAGES_STORE"))
        if not parent_folder in image_path:
          image_path = os.path.join(parent_folder, image_path)
          image["path"] = image_path
    return item

class PushToHandlerPipeline(object):
  
  def process_item(self, item, spider):
    spider.event_handler.emit(ItemScraped(), item=item)
    return item
  
class ItemPostProcessor(object):
  
  def process_item(self, item, spider):
    pp_info = item.get("_postinfo")
    if pp_info:
      for operation in pp_info:
        if isinstance(operation, Merge):
          to_merge = []
          for field_name in operation.field_names:
            to_merge.append(item.pop(field_name))
          merged = operation.merge_chars.join(to_merge)
          item.fields[operation.output_name] = {}
          item[operation.output_name] = merged
    return item
  
class SaveSpiderProgressPipeline(object):
  
  def process_item(self, item, spider):
    SpiderConfigManager.updateSpiderInformation(item)