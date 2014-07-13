'''
Created on Jul 6, 2014
@author: Mohammed Hamdy
'''

from PySide.QtWebKit import QWebPage
from PySide.QtCore import Signal, Qt
from PySide.QtGui import QColor
from menus import ActionTypes
from collections import deque

class FormDetectorPage(QWebPage):
  """
  A page that detects forms
  """
  form_detected = Signal(dict) # dict like {"zipcode":{"value":12345, "type":"text"}...}
  
  _form_getter_js = """
        var ret = {};
        var unwanted_inputs = ["submit"];
        for (var i = 0; i < this.length; ++i) {
          elem = this.elements[i];
          // do not include hidden elements neither submit buttons
          if ( elem.offsetParent !== null && unwanted_inputs.indexOf(elem.type) === -1 )
            ret[elem.name] = {value:elem.value, type:elem.type};
        }
        ret;
      """
      
  def acceptNavigationRequest(self, frame, netRequest, navType):
    if navType == QWebPage.NavigationType.NavigationTypeFormSubmitted:
      # try to intercept the form here
      form = frame.findFirstElement("form")
      if form:
        values = form.evaluateJavaScript(self._form_getter_js)
        self.form_detected.emit(values)
    return super(FormDetectorPage, self).acceptNavigationRequest(frame, netRequest, navType)
  
  
class FieldInfo(object):
  """Important for keeping track of selected elemnts on the page and their properties"""
  def __init__(self, fieldName, webElements=[], colourClass=ColourClasses.CLASS_TEXT_ATTRIBUTE,
               associatedAction=ActionTypes.ACTION_SCRAPE_TEXT):
    # webElements are usually LocatorWebElements
    self.field_name = fieldName
    self.web_elements = webElements
    self.colour = ColourClasses.colorByClass(colourClass)
    self.action_type = associatedAction
    
  def setActionType(self, actionType=ActionTypes.ACTION_SCRAPE_TEXT):
    self.action_type = actionType
    
  def __eq__(self, other):
    return self.field_name == other.field_name and \
           self.web_elements == other.web_elemens
  
  def __str__(self):
    return "<FieldInfo : <field name : {}>".format(self.field_name)
  
class TableInfo(object):
  def __init__(self, webElement, index):
    self.web_element = webElement
    self.index = index
    self.color = ColourClasses.colorByClass(ColourClasses.CLASS_TABLES)
    self.action_type = ActionTypes.ACTION_SCRAPE_TABLE
    
class ColourClasses(object):
  """Note the American usage"""
  CLASS_TEXT_ATTRIBUTE = 1
  CLASS_IMAGE = 2
  CLASS_ITEM_PAGE = 3
  CLASS_PAGINATION = 4
  CLASS_TABLES = 5
  CLASS_EXTRA_SIMILARS = 6 # these take similar shades of the same color
  
  _extra_shades = deque([QColor(227,12,252), QColor(192,3,214), QColor(146,2,162)]) # you may extend that
  
  @classmethod
  def colorByClass(cls, colorClass):
    if colorClass == cls.CLASS_TEXT_ATTRIBUTE:
      return Qt.red
    elif colorClass == cls.CLASS_IMAGE:
      return Qt.darkRed
    elif colorClass == cls.CLASS_ITEM_PAGE:
      return Qt.blue
    elif colorClass == cls.CLASS_PAGINATION:
      return Qt.darkBlue
    elif colorClass == cls.CLASS_TABLES:
      return QColor(255, 128, 0)
    elif colorClass == cls.CLASS_EXTRA_SIMILARS:
      shade = cls._extra_shades[0]
      cls._extra_shades.rotate()
      return shade