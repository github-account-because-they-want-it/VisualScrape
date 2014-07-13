'''
Created on Jul 5, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QMenu, QAction, QActionGroup

class ImageActionGroup(QActionGroup):
  def __init__(self, parent=None):
    super(ImageActionGroup, self).__init__(parent)
    self.action_download_image = DownloadImageAction()
    self.addAction(self.action_download_image)
    self.action_scrape_attribute = ScrapeAttributeAction()
    self.addAction(self.action_scrape_attribute)
    self.setExclusive(True)

class ScrapeAttributeAction(QAction):
  def __init__(self, parent=None):
    super(ScrapeAttributeAction, self).__init__(parent)
    self.setText(self.tr("Scrape Attribute ..."))
    self.setToolTip(self.tr("Scrape an HTML attribute"))
    self.setCheckable(True)
    
class ScrapeTextAction(QAction):
  def __init__(self, parent=None):
    super(ScrapeTextAction, self).__init__(parent)
    self.setText(self.tr("Scrape Text ..."))
    self.setToolTip(self.tr("Scrape the element text node"))
    self.setCheckable(True)
    
class SelectSimilarAction(QAction):
  def __init__(self, parent=None):
    super(SelectSimilarAction, self).__init__(parent)
    self.setText(self.tr("Select Similar"))
    self.setToolTip(self.tr("Find and select elements similar to this element on the page"))
    self.setCheckable(True)

class DownloadImageAction(QAction):
  def __init__(self, parent=None):
    super(DownloadImageAction, self).__init__(parent)
    self.setText(self.tr("Download Image"))
    self.setToolTip(self.tr("The image will be displayed in the Viewer"))
    self.setCheckable(True)
    
class MarkAsItemLinkAction(QAction):
  def __init__(self, parent=None):
    super(MarkAsItemLinkAction, self).__init__(parent)
    self.setText(self.tr("Item link"))
    self.setToolTip(self.tr("The final target of the scraping process"))
    
class MarkAsPaginationLinkAction(QAction):
  def __init__(self, parent=None):
    super(MarkAsPaginationLinkAction, self).__init__(parent)
    self.setText(self.tr("Pagniation link"))
    self.setToolTip(self.tr("A link that leads to more pages like this page"))
    
class NewActionWizardAction(QAction):
  
  def __init__(self, parent=None):
    super(NewActionWizardAction, self).__init__(parent)
    self.setText(self.tr("New Action Wizard ..."))
    self.setShortcut(self.tr("Ctrl+Shift+A", "Action|New Action Wizard ..."))
    self.triggered.connect(self._openActionWizard)
  def _openActionWizard(self):
    pass

class SkipPaginationAction(QAction):
  def __init__(self, parent=None):
    super(SkipPaginationAction, self).__init__(parent)
    self.setText(self.tr("Skip pagination links"))
    self.setShortcut(self.tr("Ctrl+SHIFT+P", "Options|Skip pagination links"))
    self.setCheckable(True)
    
class HighlightTablesAction(QAction):
  def __init__(self, parent=None):
    super(HighlightTablesAction, self).__init__(parent)
    self.setText(self.tr("Highlight tables"))
    
class ScrapeTableAction(QAction):
  def __init__(self, parent=None):
    super(ScrapeTableAction, self).__init__(parent)
    self.setText(self.tr("Scrape table"))
    self.setToolTip(self.tr("Attempt scraping the table's keys and values"))
    self.setCheckable(True)
    
#------------------------ MENUS --------------------------------#
class ActionMenu(QMenu):
  
  def __init__(self, parent=None):
    super(ActionMenu, self).__init__(parent)
    self.addAction(NewActionWizardAction(parent=self))
    
class ResettableMenu(QMenu):
  """A menu with a convenience method to reset all checked actions"""
  def __init__(self, parent=None):
    super(ResettableMenu, self).__init__(parent)
    self._checkable_actions = [] # subclasses should fill this
    self._action_types = []
    
  def reset(self):
    for action in self._checkable_actions:
      action.setChecked(False)
      
  def resetExcept(self, actionType):
    """Uncheck all checkable actions except the one of ActionType actionType"""
    raise NotImplemented("Subclasses of ResettableMenu should re-implement resetExcept")

class ImageRightclickMenu(ResettableMenu):
  
  def __init__(self, parent=None):
    super(ImageRightclickMenu, self).__init__(parent)
    self._action_group_image = ImageActionGroup(self)
    self.addAction(self._action_group_image.action_download_image)
    self.addAction(self._action_group_image.action_scrape_attribute)
    self.action_download_image = self._action_group_image.action_download_image
    self.action_scrape_attribute = self._action_group_image.action_scrape_attribute
    self._checkable_actions = [self.action_download_image, self.action_scrape_attribute]
    
  def resetExcept(self, actionType):
    self.reset()
    if actionType == ActionTypes.ACTION_DOWNLAOD_IMAGE:
      self.action_download_image.setChecked(True)
    elif actionType == ActionTypes.ACTION_SCRAPE_ATTRIBUTE:
      self.action_scrape_attribute.setChecked(True)
    

class ElementRightClickMenu(ResettableMenu):
  def __init__(self, parent=None):
    super(ElementRightClickMenu, self).__init__(parent)
    self.action_scrape_text = ScrapeTextAction()
    self.addAction(self.action_scrape_text)
    self.action_scrape_attribute = ScrapeAttributeAction()
    self.addAction(self.action_scrape_attribute)
    self.action_select_similar = SelectSimilarAction()
    self.addAction(self.action_select_similar)
    self.action_highlight_tables = HighlightTablesAction()
    self.addAction(self.action_highlight_tables)
    self.mark_menu = MarkAsMenu(self)
    self._checkable_actions = [self.action_scrape_text, self.action_scrape_attribute]
    
  def resetExcept(self, actionType):
    self.reset()
    if actionType == ActionTypes.ACTION_SCRAPE_TEXT:
      self.action_scrape_text.setChecked(True)
    elif actionType == ActionTypes.ACTION_SCRAPE_ATTRIBUTE:
      self.action_scrape_attribute.setChecked(False)

  def addMarkMenu(self, enabled):
    if enabled:
      self.addMenu(self.mark_menu)
    else:
      self.mark_menu.setEnabled(False) #TODO: delete the menu instead
      
class MarkAsMenu(QMenu):
  def __init__(self, parent=None):
    super(MarkAsMenu, self).__init__(parent)
    self._mark_as_submenu = MarkAsSubmenu(self)
    menu_action = self.addMenu(self._mark_as_submenu)
    menu_action.setTitle(self.tr("Mark as"))
    self.action_mark_item_link = self._mark_as_submenu.action_mark_item_link
    self.action_mark_pagination_link = self._mark_as_submenu.action_mark_pagination_link
    
class MarkAsSubmenu(QMenu):
  def __init__(self, parent=None):
    super(MarkAsSubmenu, self).__init__(parent)
    self.action_mark_item_link = MarkAsItemLinkAction(self)
    self.action_mark_pagination_link = MarkAsPaginationLinkAction(self)
    self.addAction(self.action_mark_item_link)
    self.addAction(self.action_mark_pagination_link)

class ActionTypes(object):
  """Action types associated with different selected elements on the page"""
  ACTION_SCRAPE_ATTRIBUTE = 0
  ACTION_SCRAPE_TEXT = 1
  ACTION_DOWNLAOD_IMAGE = 2
  ACTION_MARK_ITEM_PAGE = 3
  ACTION_MARK_PAGINATION = 4
  ACTION_HIGHLIGHT_TABLES = 5
  ACTION_SCRAPE_TABLE = 6
  
class ScrapeTableMenu(QMenu):
  def __init__(self, parent=None):
    super(ScrapeTableMenu, self).__init__(parent)
    self.action_scrape_table = ScrapeTableAction()
    self.addAction(self.action_scrape_table)