'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose, Identity
from visualscrape.lib.path import URL

def canonicalize(imageUrls, loader_context): #loader_context arg name must be an exact match
  response = loader_context.get("response_ctx")
  urlized = [URL(img_url) for img_url in imageUrls]
  canonicalized = [img_url.canonicalize(response.url) for img_url in urlized]
  return canonicalized

class DefaultItemLoader(ItemLoader):
  default_input_processor = MapCompose(unicode, unicode.strip) #good for string input
  default_output_processor = TakeFirst()
  
  image_urls_in = MapCompose(canonicalize)