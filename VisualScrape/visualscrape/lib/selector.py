'''
Created on May 25, 2014
@author: Mohammed Hamdy
@summary: declares selection-related classes
'''

class FieldSelector(object):
  """
  Represents a CSS or XPATH selector.
  The selector is expected to return a single element (the results won't be
  looped over).
  This corresponds to a single Item field.
  Supports looping over to obtain selector strings.
  """
  XPATH = 0
  CSS   = 1
  TEXT_CONTENT = 11
  URL_CONTENT = 12
  IMAGE_CONTENT  = 13
  
  def __init__(self, name, selectors=[], type=XPATH, contentType=TEXT_CONTENT):
    """
    Positional arguments
    name -- string to identify the selector and it's purpose
    Keyword arguments:
    selectors -- an iterable of CSS/XPATH selector(s), the second to last, if exist, are backups to the first
    type -- the selector type (xpath or css), taken from the class's constants
    contentType -- the content type of selected data (text or image), taken from
                   this class's constants
    """
    self.name = name
    self.selectors = selectors
    self.type = type
    self.content_type = contentType
    self.selector_index = 0
  
  def nextSelector(self):
    """Support explicit iteration (like with a while loop)"""
    if self.selector_index == len(self.selectors):
      return None
    else:
      next_selector = self.selectors[self.selector_index]
      self.selector_index += 1
      return next_selector
  
  def __iter__(self):
    """Support the iteration protocol"""
    self.selector_index = 0
    return self
  
  def next(self):
    next_selector = self.nextSelector()
    if next_selector: return next_selector
    else: raise StopIteration
    
  def __str__(self):
    return "<FieldSelector name=%s, selector=%s, type=%s, content_type=%s>".format(
            self.name, self.selector, 
            "xpath" if self.type == self.XPATH else "css",
            "image" if self.content_type == self.IMAGE_CONTENT else 
              "normal(text)" if self.content_type == self.TEXT_CONTENT else "url")
    
  def __unicode__(self):
    return self.__str__()
  
class ItemSelector(list):
  """This should be used to contain FieldSelector objects,
     each corresponding to an item field
  """
  pass