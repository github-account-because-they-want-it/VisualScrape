'''
Created on May 25, 2014s
@author: Mohammed Hamdy
'''
import urlparse

class SpiderPath(list):
  """
  Collect information about the path that the spider will travel. 
  add_step should be called by the sequence in which the
  spider will move.
  Supports iteration. Returns Paths and/or Forms successively
  """
    
  def add_step(self, step):
    """A step could be a URL, Form or MainPage"""
    self.append(step)
    return self
    
  def __str__(self):
    return "<SpiderPath: {0}>".format(" *>".join(self))
    
    
class URL(str):
  
  def canonicalize(self, parentURL):
    parsed_self = urlparse.urlparse(self)
    if parsed_self.scheme:
      return self[:] #string copy?
    else:
      parsed_parent = urlparse.urlparse(parentURL)
      return urlparse.urljoin(parsed_parent.scheme + "://" + parsed_parent.netloc, self)
  
  def __str__(self):
    return "<URL : " + self + " >"

class FormElemInfo(object):
  INPUT_TEXT = 1
  INPUT_SELECT = 2
  
  def __init__(self, elemName, elemValue, elemType=INPUT_TEXT):
    self.name = elemName
    self.value = elemValue
    self.type = elemType
    
  def __str__(self):
    return "<FormElemInfo name=%s - _value=%s - type=%s>" % (self.name, self.value, 
                "text-input" if self.type == self.INPUT_TEXT else "select-input")
  
class Form(object):
  
  def __init__(self, formUrl, formData=[]):
    """
    formData -- An iterable of FormElemInfo objects
    """
    self.url = formUrl
    self.data = formData #a list of FormElemInfo objects
    
  def add_field(self, fieldName, fieldValue):
    self.data.setdefault(fieldName, fieldValue)
    
  def __str__(self):
    return "<Form: {0}>".format(self.url)

  
class MainPage(object):
  """This is the final destination of the spider and the reason for the crawling process"""
  def __init__(self, itemPageSelector=None, itemSelector=None, similarPagesSelector=None, similarPagesXpathRestrict=None):
    """
    itemPageSelector -- a UrlSelector
    itemSelector -- an ItemSelector object
    similarPagesSelector -- a UrlSelector
    similarPagesXpathRestrict -- xpath selector string
    """
    self.item_page_selector = itemPageSelector
    self.item_selector = itemSelector
    self.similar_pages_selector = similarPagesSelector 
    self.similar_pages_restrict = similarPagesXpathRestrict 
    
  def __str__(self):
    return "<MainPage: at %d>".format(id(self))