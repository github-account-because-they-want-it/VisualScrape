'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose, Identity
from lxml import etree
import re
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
  
class RegexItemLoader(ItemLoader):
  """Incomplete"""
  def add_regex(self, fieldname, regex, tags=('a'), attrs=("href")):
    """Adds regex capabilities to the scrapy item loader."""
    response = self.context.get("reponse")
    root = etree.HTML(response.body)
    tags_match = []
    for tag in tags:
      tag_match = root.find(tag)
      tags_match.extend(tag_match if tags_match else [])
    # get attributes from tags
    attrs_match = []
    for attr in attrs:
      for tag in tags_match:
        tag_attr = tag[attr]
        if tag_attr:
          attrs_match.append(tag_attr)
    # apply now the regex against attributes
    """Do I really want this?"""
    pass
    