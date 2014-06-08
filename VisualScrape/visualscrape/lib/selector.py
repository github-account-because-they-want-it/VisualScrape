'''
Created on May 25, 2014
@author: Mohammed Hamdy
@summary: declares selection-related classes
'''

class KeyValueSelector(object):
  """This is the class that should be used for selection"""
  def __init__(self, key, value):
    self.key_selector = key       # can be a string or FieldSelector
    self.value_selector = value   # ditto, for more flexibility. It's a far possibility though that it's a hard string

class FieldSelector(unicode):
  """
  Represents a CSS, XPATH or REGEX selector.
  This corresponds to a single Item field.
  """
  XPATH = 0
  CSS   = 1
  REGEX = 2 
  def __new__(cls, selector, *args, **kwargs): #override new to accept an extra argument
    return unicode.__new__(cls, selector)
  
  
  def __init__(self, selector, type=XPATH):
    """
    Positional arguments
    Keyword arguments:
    selector -- a CSS/XPATH selector string
    type -- the selector type (xpath or css), taken from the class's constants
    """
    self.type = type
    
  def __unicode__(self):
    return "<FieldSelector selector=%s, type=%s>".format(
            super(FieldSelector, self).__str__().decode("utf-8"), 
            "xpath" if self.type == self.XPATH else "css")
    
  
class UrlSelector(FieldSelector):
  ACTION_VISIT = 1
  ACTION_CLICK = 2
  UNIQUE_HREF = 11
  UNIQUE_TEXT = 12
  UNIQUE_ONCLICK = 13
  
  def __init__(self, selector, type, action=ACTION_VISIT, uniqueAttr=UNIQUE_HREF):
    """
    Args:
      action : Whether the link should be clicked, or href extracted and visited
      uniqueAttr : The link attribute that makes the link special. This helps me keep track of duplicates
    """
    super(UrlSelector, self).__init__(selector, type)
    self.action = action
    self.unique_attr = uniqueAttr
    
  def __unicode__(self):
    return "<UrlSelector selector=%s, type=%s, action=%s>".format(
            super(FieldSelector, self).__unicode__(), 
            "xpath" if self.type == self.XPATH else "css", 
            "click" if self.action == self.ACTION_CLICK else "visit")

class ImageSelector(FieldSelector):
  
  def __unicode__(self):
    return super(ImageSelector, self).__unicode__().replace("Field", "Image")


class ItemSelector(list):
  """This should be used to contain FieldSelector objects,
     each corresponding to an item field
  """
  pass