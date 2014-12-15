'''
Created on Jun 16, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import (QMainWindow, QGridLayout, QTabWidget, QIcon, QWidget, QMessageBox, QAction,
                          QKeySequence)
from PySide.QtCore import Signal
from functools import partial
from visualscrape.ui.viewer.support import ScrapeSearchLineEdit, SpiderTab, ContextMenuTabWidget
from visualscrape.ui.viewer.dialog import ExportDialog, FindReplaceDialog
from visualscrape.lib.export import FileExporter
from visualscrape.lib.data import DataStore, ProducerMixin

class VisualScrapeWindow(QMainWindow):
  """A window with a data table and a search box"""
  spider_stop_requested = Signal(int) # the spider ID as an argument. bridges the signal to a probably interested engine
  def __init__(self, parent=None):
    super(VisualScrapeWindow, self).__init__(parent)
    self._tab_index_to_lineedit_map = {}
    layout = QGridLayout()
    self._tab_widget = ContextMenuTabWidget()
    self._tab_widget.setTabsClosable(True)
    self._tab_widget.tabCloseRequested.connect(self.requestTabClose)
    self._tab_widget.currentChanged.connect(self._changeSearchLineEdit)
    row = 0; col = 0;
    row += 1; col += 2; # the positions for the line edit
    self._search_lineedit_pos = (row, col)
    row += 1; col = 0;
    layout.addWidget(self._tab_widget, row, col, 1, 4)
    central_widget = QWidget()
    central_widget.setLayout(layout)
    self.setCentralWidget(central_widget)
    self._setupMenuBar()
    self._setupFindDialog()
    
  def _setupMenuBar(self):
    menu_bar = self.menuBar()
    # setup the file menu
    file_menu = menu_bar.addMenu(self.tr("&File"))
    action_export = QAction(self.tr("&Export all ..."), self)
    action_export.triggered.connect(self._showExportDialog)
    file_menu.addAction(action_export)
    action_exit = QAction(self.tr("&Quit"), self)
    action_exit.setShortcut(QKeySequence.Quit)
    action_exit.triggered.connect(self.close)
    file_menu.addAction(action_exit)
    # setup the edit menu
    edit_menu = menu_bar.addMenu(self.tr("&Edit"))
    action_find_replace = QAction(self.tr("Find/Replace"), self)
    action_find_replace.setShortcut(QKeySequence.Find)
    action_find_replace.triggered.connect(self._showFindReplaceDialog)
    edit_menu.addAction(action_find_replace)
    # setup the help menu
    menu_help = menu_bar.addMenu(self.tr("&Help"))
    action_about = QAction(self.tr("About"), self)
    action_about.triggered.connect(self._showAboutDialog)
    menu_help.addAction(action_about) 
    
  def _setupFindDialog(self):
    self._find_dialog = FindReplaceDialog(self)
    self._find_dialog.find_text_changed.connect(self._tellActiveTableToSearch)
    self._find_dialog.replace_committed.connect(self._tellActiveTableToReplace)
    self._find_dialog.find_cancelled.connect(self._tellActiveTableSearchCancelled)
    
  def closeEvent(self, ce):
    # ask all tabs to close
    for i in range(self._tab_widget.count()):
      response = self.requestTabClose(i)
      if not response is True: # if the user cancelled in the middle, don't ask anymore for the rest of the tabs
        break
    else: # all tabs closed
      super(VisualScrapeWindow, self).closeEvent(ce)

  def addSpider(self, spiderName):
    # initiates a spider tab with it's search line edit
    spider_tab = SpiderTab(name=spiderName)
    lineedit_search = ScrapeSearchLineEdit()
    spider_tab.configure_searchlineedit(lineedit_search)
    spider_tab.stop_spider_signal.connect(self.spider_stop_requested)
    tab_index = self._tab_widget.addTab(spider_tab, QIcon("res/icons/document_blank.png"), spiderName)
    self._tab_widget.setCurrentIndex(tab_index)
    spider_tab.favicon_received.connect(partial(self._setTabIcon, tab_index)) #set the tab icon when it arrives at the tab
    self._tab_index_to_lineedit_map[tab_index] = lineedit_search
    self._changeSearchLineEdit(tab_index) # call it again, though it's called after addTab, because the line edit has not been saved yet
    return spider_tab
  
  def requestTabClose(self, tabIndex):
    tab_to_close = self._tab_widget.widget(tabIndex)
    response = tab_to_close.stop_spider()
    if response is True:
      # now make sure the user doesn't want the data
      confirm_close = QMessageBox(self)
      confirm_close.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
      confirm_close.setIcon(QMessageBox.Warning)
      confirm_close.setText(self.tr("{0} data may be lost".format(self._tab_widget.tabText(tabIndex))))
      confirm_close.setInformativeText(self.tr("Are you sure?"))
      confirm_close.setWindowTitle(self.tr("Warning"))
      ret = confirm_close.exec_()
      if ret == QMessageBox.Yes:
        self._tab_widget.removeTab(tabIndex)
        return True
      else: return False
    else: return False
  
  def _setTabIcon(self, tabIndex, iconPath): # maybe a url too
    """Pre-configured with the tab index, this handler always knows about
       it's widget"""
    self._tab_widget.setTabIcon(tabIndex, QIcon(iconPath))
    
  def _changeSearchLineEdit(self, tabIndex):
    """When the tab changes, change the search line edit to match"""
    self_layout = self.centralWidget().layout()
    for tab_index, line_edit in self._tab_index_to_lineedit_map.items():
      if self_layout.indexOf(line_edit) >= 0:
        line_edit.hide()
        self_layout.removeWidget(line_edit)
      elif tab_index == tabIndex:
        self_layout.addWidget(line_edit, self._search_lineedit_pos[0], self._search_lineedit_pos[1], 1, 2)
        line_edit.show()
  
  def _showExportDialog(self):
    # use one dialog data for all tabs
    export_dialog = ExportDialog()
    export_dialog.exec_()
    export_info = export_dialog.data()
    if export_info:
      # get all tab names and export all of them
      store = DataStore.get_instance()
      for i in range(self._tab_widget.count()):
        tab_name = self._tab_widget.tabText(i) # tab name is also the table name in the store
        # get the matching producer
        for producer in store:
          if producer.name == tab_name and producer.type == ProducerMixin.TYPE_TABLE:
            data = producer.get_visible_data()
            break
        ofile_name = tab_name.lower()
        FileExporter.export(data, ofile_name, export_info.location, export_info.format)
    else: pass # do nothing if the export info is invalid (the user chose no folder)
  
  def _showFindReplaceDialog(self):
    self._find_dialog.show()
  
  def _showAboutDialog(self):
    pass
  
  def _tellActiveTableToSearch(self, searchText):
    data_store = DataStore.get_instance()
    for producer in data_store:
      if producer.type == ProducerMixin.TYPE_TABLE and producer.is_active():
        producer.search_changed.emit(searchText)
        break
      
  def _tellActiveTableToReplace(self, before, after):
    data_store = DataStore.get_instance()
    for producer in data_store:
      if producer.type == ProducerMixin.TYPE_TABLE and producer.is_active():
        producer.replace_committed.emit(before, after)
        break
      
  def _tellActiveTableSearchCancelled(self):
    data_store = DataStore.get_instance()
    for producer in data_store:
      if producer.type == ProducerMixin.TYPE_TABLE and producer.is_active():
        producer.search_cancelled.emit()
        break