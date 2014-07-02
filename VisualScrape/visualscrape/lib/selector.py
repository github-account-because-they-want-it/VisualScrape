'''
Created on May 25, 2014
@author: Mohammed Hamdy
@summary: declares selection-related classes
'''

class KeyValueSelector(object):
  """This is the class that should be used for selection. It helps when using FieldSelectors
     for both item keys and values, because it'll keep the results consistent by preserving field names
     even if some data is missing"""
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
    return "<FieldSelector selector={0}, type={0}>".format(
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


class ContentSelector(FieldSelector):
  WORDLIST = 1
  REGEX = 2
  
  def __init__(self, selector, restrictSelector, type=WORDLIST):
    """Args:
         restrictSelector : a CSS selector of an area where the search will be constrained to"""
    super(ContentSelector, self).__init__(selector, type)
    self.restrict_selector = restrictSelector
  
  def __unicode__(self):
    return FieldSelector.__unicode__(self).replace("Field", "Content")

class ItemSelector(object):
  """This should be used to contain KeyValueSelector objects. 
     along with any item post-processing information. ItemPageActions
     also belong here.
  """
  def __init__(self, kvSelectors=[], postProcessingInfo=None, itemPageActions=None):
    self.key_value_selectors = kvSelectors
    self.post_process_info = postProcessingInfo
    self.item_page_actions = itemPageActions
    

class Merge(object):
  def __init__(self, fieldNames, outputName, mergeChars=''):
    self.field_names = fieldNames
    self.output_name = outputName
    self.merge_chars = mergeChars
    
  def __unicode__(self):
    return "<Merge operation at 0x%0x>" % id(self)

class PostProcessing(list):
  """A list of post processing information objects"""
  pass
  
class ItemPageAction(object):
  """Action to perform after arriving at an item page, like clicking.
     This will be only supported for Selenium"""
  ACTION_CLICK = 1
  def __init__(self, selector, selectorType, action=ACTION_CLICK):
    """
    selector -- A selector that will yield one or more elements, on which to perform the
                action.
    selectorType -- A selector type from FieldSelector
    """
    self.type = action
    self.selector = selector
    self.selector_type = selectorType
    
class ItemPageAfterAction(object):
  pass

class ItemPageAfterActionSelect(ItemPageAfterAction):
  
  def __init__(self, selector, selectorType, outputField):
    self.selector = selector
    self.selector_type = selectorType
    self.output_field = outputField
    
class ItemPageActions(list):
  """A list of 2-tuples of (ItemPageAction, ItemPageAfterAction)"""
  pass
