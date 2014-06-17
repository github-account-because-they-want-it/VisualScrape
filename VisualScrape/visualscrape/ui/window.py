'''
Created on Jun 16, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QMainWindow, QGridLayout, QTabWidget, QIcon, QWidget
from functools import partial
from visualscrape.ui.support import ScrapeSearchLineEdit, SpiderTab

class VisualScrapeWindow(QMainWindow):
  """A window with a data table and a search box"""
  def __init__(self, parent=None):
    super(VisualScrapeWindow, self).__init__(parent)
    self._tab_index_to_lineedit_map = {}
    layout = QGridLayout()
    self._tab_widget = QTabWidget()
    self._tab_widget.currentChanged.connect(self._changeSearchLineEdit)
    row = 0; col = 0;
    row += 1; col += 2; # the positions for the line edit
    self._search_lineedit_pos = (row, col)
    row += 1; col = 0;
    layout.addWidget(self._tab_widget, row, col, 1, 4)
    central_widget = QWidget()
    central_widget.setLayout(layout)
    self.setCentralWidget(central_widget)

  def addSpider(self, spiderName):
    # initiates a spider tab with it's search line edit
    spider_tab = SpiderTab()
    lineedit_search = ScrapeSearchLineEdit()
    spider_tab.configure_searchlineedit(lineedit_search)
    tab_index = self._tab_widget.addTab(spider_tab, QIcon("res/icons/document_blank.png"), spiderName)
    spider_tab.favicon_received.connect(partial(self._setTabIcon, tab_index)) #set the tab icon when it arrives at the tab
    self._tab_index_to_lineedit_map[tab_index] = lineedit_search
    self._changeSearchLineEdit(tab_index) # call it again, though it's called after addTab, because the line edit has not been saved yet
    return spider_tab
  
  def _setTabIcon(self, tabIndex, iconPath): # maybe a url too
    """Pre-configured with the tab index, this handler always knows about
       it's widget"""
    self._tab_widget.setTabIcon(tabIndex, QIcon(iconPath))
    
  def _changeSearchLineEdit(self, tabIndex):
    """When the tab changes, change the search line edit to match"""
    self_layout = self.centralWidget().layout()
    for tab_index, line_edit in self._tab_index_to_lineedit_map.items():
      if self_layout.indexOf(line_edit) >= 0:
        self_layout.removeWidget(line_edit)
      elif tab_index == tabIndex:
        self_layout.addWidget(line_edit, self._search_lineedit_pos[0], self._search_lineedit_pos[1], 1, 2)
