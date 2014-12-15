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
  WORDLIST = 3
  
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
    
  @classmethod  
  def attrFromUniqueConst(cls, uniqueAttr):
    """Return attribute name suitable with web_element.get_attribute() or empty
       string for unique text"""
    if uniqueAttr == cls.UNIQUE_HREF: return "href"
    elif uniqueAttr == cls.UNIQUE_ONCLICK: return "onclick"
    elif uniqueAttr == cls.UNIQUE_TEXT: return ''
  
  def __unicode__(self):
    return "<UrlSelector selector=%s, type=%s, action=%s>".format(
            super(FieldSelector, self).__unicode__(), 
            "xpath" if self.type == self.XPATH else "css", 
            "click" if self.action == self.ACTION_CLICK else "visit")

class ImageSelector(FieldSelector):
  
  def __unicode__(self):
    return super(ImageSelector, self).__unicode__().replace("Field", "Image")

class TableSelector(FieldSelector):
  """Automatic table scraping to avoid tedious and error-prone key-value selection"""
  TABLE_VHEADERS = 1 # keys top, values downwards. can have rowspan
  TABLE_HHEADERS = 2 # keys left, values right. even column count
  
  def __init__(self, selector, type, tableType=TABLE_HHEADERS):
    super(TableSelector, self).__init__(selector, type)
    self.table_type = tableType

class ContentSelector(object):
  
  def __init__(self, selector, restrictSelector):
    """Args:
         selector : A FieldSelector of type REGEX or WORDLIST
         restrictSelector : a FieldSelector of an area where the search will be constrained to
    """
    self.selector = selector
    self.restrict_selector = restrictSelector
  
  def __unicode__(self):
    return u"<ContentSelector : selector={0}, restrict={1}>".format(self.selector, self.restrict_selector)

class ItemSelector(object):
  """This should be used to contain KeyValueSelectors/ItemPageActions objects. 
     along with any item post-processing information.
  """
  def __init__(self, selectorsActions=[], postProcessingInfo=None):
    self.selectors_actions = selectorsActions
    self.post_process_info = postProcessingInfo

class PostProcessing(list):
  """A list of post processing actions"""
  pass

class PostProcessingAction(object):
  pass

class Merge(PostProcessingAction):
  def __init__(self, fieldNames, outputName, mergeChars=''):
    self.field_names = fieldNames
    self.output_name = outputName
    self.merge_chars = mergeChars
    
  def __unicode__(self):
    return "<Merge operation at 0x%0x>" % id(self)
  
class ItemPageAction(object):
  """Action to perform after arriving at an item page, like clicking.
     This will be only supported for Selenium"""
  pass
    
class ItemPageClickAction(ItemPageAction):
  def __init__(self, selector, selectorType):
    """
    selector -- A selector that will yield one or more elements, on which to perform the
                action.
    selectorType -- A selector type from FieldSelector
    """
    self.selector = selector
    self.selector_type = selectorType

class ItemPageScrollAction(ItemPageAction):
  pass

class ItemPageScrollDistanceAction(ItemPageScrollAction):
  """Represents an absolute scroll action on the page."""
  def __init__(self, distance):
    """
    distance -- an integer amount of pixels to scroll
    """
    super(ItemPageScrollDistanceAction, self).__init__()
    self.distance = distance
    
class ItemPageScrollToElementAction(ItemPageScrollAction):
  """Represents a scroll to a specific element on the page"""
  def __init__(self, selector, selectorType):
    self.selector = selector
    self.selector_type = selectorType
      
class ItemPageActionWait(ItemPageAction):
  pass

class ItemPageActionAbsoluteWait(ItemPageActionWait):
  def __init__(self, waitTime):
    # waitTime is in milliseconds
    self.time = waitTime
    
class ItemPageScrollUntilAction(ItemPageActionWait):
  """Represents a wait until new content becomes available"""
  def __init__(self, timeOut=30000):
    self.timeout = timeOut
    
class ItemPageActions(list):
  """A list of ItemPageAction objects"""
  pass
