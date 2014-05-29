'''
Created on May 25, 2014

@author: Mohammed Hamdy
'''

from scrapy.item import Item, Field
from visualscrape.lib.selector import FieldSelector

class InterestItem(Item):
  """
  Provides an automatic Item from a list of Selector objects,
  instead of having to hard-code an Item
  """
  def __init__(self, itemSelector):
    """
    Positional arguments
    itemSelector -- a list of FieldSelector objects
    """
    """
    Name fields automatically by selector names. This reflects the real matching
    between item fields and selectors
    """
    super(InterestItem, self).__init__()
    for selector in itemSelector:
      if selector.content_type == FieldSelector.IMAGE_CONTENT:
        #all image items use 2 fields. see http://doc.scrapy.org/en/latest/topics/images.html#usage-example
        if not self.fields.get("image_urls"):
          self.fields["image_urls"] = Field()
          self.fields["images"] = Field()
      elif selector.content_type == FieldSelector.TEXT_CONTENT:
        self.fields[selector.name] = Field()
    # add an id field, to identify items with their spiders
    self.fields["id"] = Field() 