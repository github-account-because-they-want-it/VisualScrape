'''
Created on May 25, 2014
@author: Mohammed Hamdy
'''

from scrapy.item import Item, Field, DictItem

def InterestItem(nameList):
  nameList = nameList[:]
  # add the _id field. To identify items with different spiders. It also won't hurt to add the image fields, even if not used
  nameList.extend(["_id", "image_urls", "images", "_postinfo", "_spidertype", "_scrapedurl", "_spidername"]) 
  # different from the docs. But it works ;). Hail the debugger!
  return type("InterestItem", (DictItem,), {"fields":{field_name:Field() for field_name in nameList}})() #instantiate
        

class FaviconItem(Item):
  _id = Field()
  image_urls = Field()
  images = Field()