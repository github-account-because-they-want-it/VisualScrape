'''
Created on May 28, 2014
@author: Mohammed Hamdy
'''
import os
from visualscrape.config import settings
from visualscrape.lib.signal import ItemScraped

class FilterFieldsPipeline(object):
  """
  Remove unwanted? fields in the result like image_urls
  Assuming the images from the image pipeline get processed
  immediately, not after the whole pipeline is traversed.
  """
  
  def process_item(self, item, spider):
    if item.get("image_urls"):
      item.pop("image_urls")
      
    return item


class CanonicalizeImagePathPipeline(object):
  """Images "path" field returned from scrapy is not canonicalized, making
     it useless to locate the image"""
  
  def process_item(self, item, spider):
    images = item.get("images", None)
    if images:
      for image in images:
        image_path = os.path.normpath(image.get("path"))
        parent_folder = os.path.normpath(settings.IMAGES_STORE.value())
        if not parent_folder in image_path:
          image_path = os.path.join(parent_folder, image_path)
          image["path"] = image_path
    return item

class PushToHandlerPipeline(object):
  
  def process_item(self, item, spider):
    spider.event_handler.emit(ItemScraped(), item=item)
    return item