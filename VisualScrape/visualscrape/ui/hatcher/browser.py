'''
Created on Jul 5, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QPainter, QPen, QColor
from PySide.QtWebKit import QWebView
from PySide.QtCore import Qt, Signal, QUrl
from webelement import LocatorWebElement
from menus import ImageRightclickMenu, ElementRightClickMenu
from dialogs import ScrapeAttributeDialog, FieldNameDialog
from ui_common import AnimatedClosableMessage, IconChangerWidget, CheckIconWidget
from web_common import FieldInfo, FormDetectorPage, ColourClasses
from menus import ActionTypes
from visualscrape.lib.path import URL


class MouseSensitiveWebView(QWebView):
  """A browser that faciliates selecting elements"""
  progress_changed = Signal(int) # emitted whenever the progress changes
  url_changed = Signal(QUrl)
  form_detected = Signal(dict)
  image_download_changed = Signal(bool, str) # emit the image selector
  element_scrape_changed = Signal(bool, str, str) # enabled, fieldname, selector
  # for non-image elements. enabled, fieldname, selector, attribute name (can be empty when deleting selectors)
  attribute_scrape_changed = Signal(bool, str, str, str) 
  
  def __init__(self, parent=None):
    super(MouseSensitiveWebView, self).__init__(parent)
    self.setPage(FormDetectorPage())
    self.urlChanged.connect(self.url_changed) # just a rename
    self.page().loadProgress.connect(self.progress_changed)
    self.page().form_detected.connect(self.form_detected)
    self._configureMenus()
    self._hover_rect = None
    self._hit_test_result = None
    self._fields_info = []  
    
  def mousePressEvent(self, mpe):
    """Draw a box around the pressed element"""
    #if self._hover_rect.contains(mpe.pos()): # strangely, this causes some valid clicks to be ignored
    mouse_pos = mpe.pos()
    hit_test_result = self.page().mainFrame().hitTestContent(mouse_pos) # this avoids strange c++ object already deleted errors for the web frame
    if hit_test_result:
      # this geometry is relative to the parent, this has consequences when the page has scrolling
      new_rect = hit_test_result.boundingRect()
      self._hover_rect = new_rect  
      self._hit_test_result = hit_test_result
      self.update()
    else:
      self._hover_rect = None
        
  def contextMenuEvent(self, cme):
    hit_elem = self._hitElemLocator()
    action_type = None
    # check if the clicked element was previously operated upon
    for field_info in self._fields_info:
      web_element = field_info.web_element
      if hit_elem == web_element:
        action_type = field_info.action_type
        break
    if hit_elem.tagName() == "IMG":
      menu = self._image_menu
    else:
      menu = self._element_menu
    if action_type is not None: # the element was selected before. Enable it's previously chosen action and reset the rest
      menu.resetExcept(action_type)
    else:
      menu.reset()
    # check if that element is already selected
    menu.popup(cme.globalPos())
      
  def paintEvent(self, pe):
    if not self._hover_rect:
      super(MouseSensitiveWebView, self).paintEvent(pe)
    else:
      super(MouseSensitiveWebView, self).paintEvent(pe)
      hover_rect = self._hover_rect
      self._fixRectForScroll(hover_rect)
      painter = QPainter(self)
      painter.save()
      pen = QPen(Qt.red)
      pen.setWidth(2)
      painter.setPen(pen)
      painter.drawRect(hover_rect)
      painter.restore()
      # draw green rects around the similar elements
      painter.save()
      pen = QPen(QColor(0, 128, 255))
      pen.setWidth(2)
      painter.setPen(pen)
      for field_info in self._fields_info:
        # draw selected elements with the same color.
        web_element = field_info.web_element
        elem_rect = web_element.absoluteGeometry()
        painter.drawRoundedRect(self._fixRectForScroll(elem_rect), 2, 2) # just slight rounding
      painter.restore()
      # Each similars group should be drawn with it's own shade
      for field_info in self._fields_info:
        if field_info.similars_selected:
          similars = field_info.web_element.selectSimilars()
          similars_shade = field_info.similars_shade
          for similar in similars:
            pen = QPen(similars_shade)
            pen.setWidth(2)
            painter.setPen(pen)
            elem_rect = similar.absoluteGeometry()
            self._fixRectForScroll(elem_rect)
            painter.drawRoundedRect(elem_rect, 2, 2)
              
  def _fixRectForScroll(self, rect):
    main_frame = self.page().mainFrame()
    hor_pos, ver_pos = main_frame.scrollBarValue(Qt.Horizontal), main_frame.scrollBarValue(Qt.Vertical)
    rect.moveTop(rect.top() - ver_pos)
    rect.moveLeft(rect.left() - hor_pos)
  
  def _configureMenus(self):
    self._image_menu = ImageRightclickMenu(parent=self)
    self._element_menu = ElementRightClickMenu(parent=self)
    self._image_menu.action_download_image.toggled.connect(self._downloadImage)
    self._image_menu.action_scrape_attribute.toggled.connect(self._showAttributeDialog)
    self._element_menu.action_scrape_attribute.toggled.connect(self._showAttributeDialog)
    self._element_menu.action_scrape_text.toggled.connect(self._scrapeText)
    self._element_menu.action_select_similar.toggled.connect(self._selectSimilar)
    
  def _downloadImage(self, checked):
    # I hope that the hit result doesn't change between right-clicking on the element and choosing the menu option
    hit_elem = self._hitElemLocator()
    if checked:
      self._fields_info.append(FieldInfo("images", hit_elem, colourClass=ColourClasses.CLASS_IMAGE, 
                                         associatedAction=ActionTypes.ACTION_DOWNLAOD_IMAGE))
    else:
      self._popElement(hit_elem)
      self.update()
    selector = hit_elem.selector()
    self.image_download_changed.emit(checked, selector)
    
  def _showAttributeDialog(self, checked):
    hit_elem = self._hitElemLocator()
    if checked:
      # get the attributes of the selected element, to allow the user to select from them
      attr_dict = self._getAttrDict(hit_elem)
      field_names = self._getFieldNames()
      dialog = ScrapeAttributeDialog(attr_dict, field_names)
      result = dialog.exec_()
      if result == dialog.Accepted: # do nothing otherwise
        choices = dialog.getChoices()
        self._fields_info.append(FieldInfo(choices["field_name"], hit_elem, 
                                           associatedAction=ActionTypes.ACTION_SCRAPE_ATTRIBUTE))
        self.attribute_scrape_changed.emit(checked, choices["field_name"], hit_elem.selector(), choices["attr_name"])
        self.update()
    else: # remove the element from the field list
      field_info = self._popElement(hit_elem)
      self.attribute_scrape_changed.emit(checked, field_info.field_name, field_info.web_element.selector(), '')
      self.update()
    
  def _scrapeText(self, checked):
    hit_elem = self._hitElemLocator()
    if checked:
      # get the field name to add the selector to
      field_names = self._getFieldNames()
      dialog = FieldNameDialog(field_names)
      result = dialog.exec_()
      if result == dialog.Accepted:
        selector = hit_elem.selector()
        output_field = dialog.getField()
        self._fields_info.append(FieldInfo(output_field, hit_elem, colourClass=ColourClasses.CLASS_TEXT_ATTRIBUTE))
        self.element_scrape_changed.emit(checked, output_field, selector)
        self.update()
    else:
      removed_field = self._popElement(hit_elem)
      selector = removed_field.web_element.selector()
      self.element_scrape_changed.emit(checked, removed_field.field_name, selector) # the selector is not needed here, I guess
      self.update()
      
  def _selectSimilar(self, checked):
    # this doesn't update the scraped fields. It's just a visual indication
    hit_elem = self._hitElemLocator()
    # if already selected, do nothing
    for (i, field_info) in enumerate(self._fields_info):
      web_element = field_info.web_element
      if web_element == hit_elem:
        return
    if checked:
      color_shade = ColourClasses.colorByClass(field_info.colour_class)
    else:
      pass
    field_info.setSimilarsSelected(checked)
    self.update()
      
  def _hitElemLocator(self):
    hit_elem = self._hit_test_result.element()
    hit_elem = LocatorWebElement(hit_elem, self._hit_test_result, self.page().mainFrame())
    return hit_elem
  
  def _getAttrDict(self, webElement):
    attr_names = webElement.attributeNames()
    attr_dict = {}
    for attr_name in attr_names:
      attr_dict[attr_name] = webElement.attribute(attr_name)
    return attr_dict
  
  def _getFieldNames(self):
    return [field_info.field_name for field_info in self._fields_info]
  
  def _popElement(self, webElement):
    """Untrack a web view selection and return it"""
    for (i, field_info) in enumerate(self._fields_info):
      web_element = field_info.web_element
      if web_element == webElement:
        self._fields_info.pop(i)
        break
    return field_info
  
  
class NotifierWebView(MouseSensitiveWebView):
  """A web view with a notification message"""
  
  item_page_selected = Signal(str)
  similars_selected = Signal(str)
  
  def __init__(self, parent=None):
    super(NotifierWebView, self).__init__(parent)
    close_widget = IconChangerWidget("../res/icons/close_btn_hover.png", "../res/icons/close_btn_nohover.png", resolution=(16, 16))
    self._message_widget = AnimatedClosableMessage(close_widget, parent=self)
    self._mainpage_checker = CheckIconWidget("../res/mark_as_main.png", "../res/unmark_as_main.png", parent=self)
    self._mainpage_checker.checked.connect(self._markMainClicked)
    self._main_page_marked = False
    self._item_pages_selected = False
    self._pagination_selected = False
    
  def _configureMenus(self):
    MouseSensitiveWebView._configureMenus(self)
    # add the mark as menu when the checker button is clicked
    self._mainpage_checker.checked.connect(self._element_menu.addMarkMenu)
    self._element_menu.mark_menu.action_mark_item_link.triggered.connect(self._markItemLinks)
    self._element_menu.mark_menu.action_mark_pagination_link.triggered.connect(self._markActionLinks)
    
  def resizeEvent(self):
    self._message_widget.move(0, 0)
    self._message_widget.setFixedWidth(self.width())
    self._mainpage_checker.move(self.width() - self._mainpage_checker.width(),
                                self.height() - self._mainpage_checker.height())
  
  def _markMainClicked(self, marked):
    if marked:
      self._message_widget.setMessage(self.tr("Now you can select an example link to your items and a pagination link from the context menu..."))
      self._main_page_marked = True 
    # TODO: use the menu bar action Skip pagination links
    
  def _markItemLinks(self):
    hit_elem = self._hitElemLocator()
    hit_elem.selectSimilar()
    elem_field_info = FieldInfo("item_pages", hit_elem, colourClass=ColourClasses.CLASS_ITEM_PAGE,
                                similarsSelected=True, associatedAction=ActionTypes.ACTION_MARK_ITEM_PAGE)
    self._fields_info.append(elem_field_info)
    self.item_page_selected.emit(hit_elem.selector())
    self.update()
    self._item_pages_selected = True
    self._checkGoToItemPage()
    
  def _markActionLinks(self):
    hit_elem = self._hitElemLocator()
    hit_elem.selectSimilar()
    elem_field_info = FieldInfo("pagination", hit_elem, colourClass=ColourClasses.CLASS_PAGINATION,
                                similarsSelected=True, associatedAction=ActionTypes.ACTION_MARK_PAGINATION)
    self._fields_info.append(elem_field_info)
    self.similars_selected.emit(hit_elem.selector()) 
    self._pagination_selected = True
    self.update()
    self._checkGoToItemPage()
    
  def _checkGoToItemPage(self):
    if self._item_pages_selected and self._pagination_selected:
      # select an item page and go there
      self._message_widget.setMessage(self.tr("Taking you to an item page ..."))
      for field_info in self._fields_info:
        if field_info.action_type == ActionTypes.ACTION_MARK_ITEM_PAGE:
          break
      web_element = field_info.web_element
      url = URL(web_element.attribute("href")) # this can be not absolute
      url = url.canonicalize(self.url())
      self._mainpage_checker.hide()
      self.setUrl(url)