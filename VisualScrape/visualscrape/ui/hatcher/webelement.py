'''
Created on Jul 5, 2014
@author: Mohammed Hamdy
'''

from PySide.QtCore import QRect, QObject
from scrapy.selector import Selector

class LocatorWebElement(QObject):
  """A web element that can return it's selector in the page"""
  
  def __init__(self, webElement, hitTestResult, pageFrame):
    """The pageFrame should be better than the element frame in finding elements"""
    super(LocatorWebElement, self).__init__()
    self._element = webElement
    self._hit_test_result = hitTestResult
    self._page_frame = pageFrame
    self._selector = None
    self._selector_searched = False
    self._current_similars = [] # this normally includes self
    self._similars_found = False
    self._similars_selector = ''
    self._geometry_calculated = False
    self._geometry = None
    
  def selector(self):
    """Return the element CSS selector as a string"""
    if self._selector_searched:
      return self._selector
    if self._element.isNull():
      return self._findSelectorByText()
    self_flatcss = self._flatCSSForElement(self._element)
    if self._isUniqueSelector(self_flatcss):
      return self_flatcss
    parent = self._element.parent()
    current_css = self_flatcss 
    while parent: # or self.parent().tagName() != "body"
      # try the parent's id. if failed, try it's classes and tag
      parent_id = parent.attribute("id")
      possible_selector_by_parent_id = self._joinSelectors(parent_id, current_css)
      if self._isUniqueSelector(possible_selector_by_parent_id):
        return self._setAndReturn(possible_selector_by_parent_id)
      parent_flatcss = self._flatCSSForElement(parent)
      possible_selector_by_parent_css = self._joinSelectors(parent_flatcss, current_css)
      if self._isUniqueSelector(possible_selector_by_parent_css):
        return self._setAndReturn(possible_selector_by_parent_css)
      # selection by this parent failed. climb up
      current_css = self._getCurrentCSSUsingParent(parent, current_css)
      parent = parent.parent()
      # OOPS!. No unique selector found by traveling up. find an ordered selector instead
    return self._getOrderedSelector() # this might fail too
  
  def absoluteGeometry(self):
    """A fix to get the element to return it's absolute geometry, instead of
       it's geometry relative to it's parent frame"""
    if self._geometry_calculated: return self._geometry
    if self._element.isNull(): return None
    elem = self._element
    elem_geom = QRect(elem.geometry())
    elem_webframe = elem.webFrame()
    elem_wf_geom = QRect(elem_webframe.geometry())
    elem_geom.moveTopLeft(elem_geom.topLeft() - elem_wf_geom.topLeft())
    wf_parent = elem_webframe.parentFrame()
    while wf_parent:
      wf_parent_geom = wf_parent.geometry()
      elem_geom.moveTopLeft(elem_geom.topLeft() - wf_parent_geom.topLeft())
    self._geometry = elem_geom
    self._geometry_calculated = True
    return elem_geom
      
  def _isUniqueSelector(self, selector):
    """Checks if selector matches a single element."""
    if not selector: return False
    self_webframe = self._page_frame
    html = self_webframe.toHtml()
    sel = Selector(text=html)
    matches = sel.css(selector)
    # the selector is coming right but the frame is not recognizing it
    if len(matches) == 1: return True
    elif len(matches) > 1 and not self._similars_found:
      possible_similars = self_webframe.findAllElements(selector)
      if self._allSimilar(possible_similars):
        self._current_similars = possible_similars
        self._similars_found = True
        self._similars_selector = selector
    else: return False
  
  def _allSimilar(self, elements):
    # returns true if all elements have the same tag, id and classes
    elements = elements.toList()
    tag = elements[0].tagName()
    id_ = elements[0].attribute("id")
    classes = elements[0].classes()
    classes.sort()
    for element in elements[1:]:
      element_classes = element.classes()
      element_classes.sort()
      if element.tagName() != tag or element_classes != classes or element.attribute("id") != id_:
        return False
    else:
      return True
  
  def _flatCSSForElement(self, webElement):
    """Returns the tagname.class1.class2... for webElement"""
    tag = webElement.tagName()
    classes = webElement.classes()
    id_ = webElement.attribute("id")
    if id_: return '#'.join([tag, id_])
    else: return '.'.join([tag] + classes)
  
  def _getCurrentCSSUsingParent(self, parent, currentCSS):
    """Joins the parent selector with currentCSS, giving higher priority
       to parent ID"""
    parent_id = parent.attribute("id")
    if parent_id:
      return ' '.join([parent_id, currentCSS])
    parent_flatcss = self._flatCSSForElement(parent)
    return ' '.join([parent_flatcss, currentCSS])
     
  def _getOrderedSelector(self):
    """Finds an ordered selector for self. Using an order for siblings
       or the siblings of one of the parents"""
    parent = self._element.parent()
    child = self._element
    child_tag = child.tagName()
    current_css = '' # just get a suitable selector for self
    while parent:
      similar_siblings = parent.findAll(child_tag)
      # find an ordered selector for the child
      if len(similar_siblings) > 1:
        for (i, sibling) in enumerate(similar_siblings):
          if sibling == child: # or is child. TODO: this check SOMETIMES yields the wrong order
            child_css = self._flatCSSForElement(child)
            ordered_child = ''.join([child_css, ":nth-child({})".format(i + 1)])
            ordered_selector = self._joinSelectors(ordered_child, current_css)
            if self._isUniqueSelector(ordered_selector):
              return self._setAndReturn(ordered_selector)
            else:
              current_css = self._joinSelectors(ordered_child, current_css)
              break
      else:
        child_selector = self._flatCSSForElement(child)
        current_css = self._joinSelectors(child_selector, current_css)
      child = parent
      child_tag = parent.tagName()
      parent = parent.parent()
      
  def _joinSelectors(self, sel1, sel2):
    return ' '.join([sel1, sel2])
  
  def _findSelectorByText(self, elem=None):
    """For Null elements. Travel up to the parent and check for non-empty text"""
    if elem is None:
      parent_non_null = self._hit_test_result.enclosingBlockElement()
      parent_text = parent_non_null.toPlainText().strip()
      if parent_text:
        self._element = parent_non_null
        return self.selector()
      children = self._findChildren(parent_non_null)
    else:
      children = self._findChildren(elem)
    for child in children:
      child_text = child.toPlainText().strip()
      if child_text:
        self._element = child
        return self.selector()
    else:
      return self._firstOf([self._findSelectorByText(elem) for elem in children])
        
  def _firstOf(self, l):
    for e in l:
      if e: return e  
  
  def _findChildren(self, webElement):
    children = []
    child1 = webElement.firstChild()
    next_child = child1.nextSibling()
    if child1:
      children.append(child1)
    while next_child:
      children.append(next_child)
      next_child = next_child.nextSibling()
    return children
  
  def selectSimilar(self):
    # find similar QWebElements, if at all, and return them
    if not self._similars_found:
      self.selector()
      
    return self._current_similars
  
  def similarsSelector(self):
    if not self._similars_found:
      self.selector()
    return self._similars_selector
  
  def _setAndReturn(self, selector):
    self._selector_searched = True
    self._selector = selector
    return selector
  
  def __getattr__(self, attr):
    return getattr(self._element, attr)
  