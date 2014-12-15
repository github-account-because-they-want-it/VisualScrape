'''
Created on Jun 10, 2014
@author: Mohammed Hamdy
'''

from scrapy.contrib.loader.processor import MapCompose, Identity
from visualscrape.lib.scrapylib import itemloader

def filter_js_func_call(image_onclick, loader_context):
  if image_onclick.startswith("FillFullSize"):
    url_components = image_onclick.split(',')
    image_url = url_components[1].strip()
    return image_url
  return image_onclick

class CarItemLoaderMeta(type):
  """Adds dynamic image magic to the car item loader"""
  def __init__(cls, name, bases, dct):
    """Customizing __init__ because it has the cls ready"""
    cls.Images_in = MapCompose(filter_js_func_call)
    cls.Images_out = Identity()
    super(CarItemLoaderMeta, cls).__init__(name, bases, dct)
    
    
class CarItemLoader(itemloader.DefaultItemLoader):
  __metaclass__ = CarItemLoaderMeta
  