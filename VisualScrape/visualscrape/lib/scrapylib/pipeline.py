'''
Created on May 28, 2014
@author: Mohammed Hamdy
'''

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
  