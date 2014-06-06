'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose, Identity
from visualscrape.lib.path import URL

def canonicalize(imageUrl, loader_context): #loader_context arg name must be an exact match
  response = loader_context.get("response_ctx")
  urlized = URL(imageUrl)
  canonicalized = urlized.canonicalize(response.url)
  return canonicalized

class DefaultItemLoader(ItemLoader):
  default_input_processor = MapCompose(unicode, unicode.strip) #good for string input
  default_output_processor = TakeFirst()
  
  image_urls_in = MapCompose(canonicalize)
  image_urls_out = Identity()