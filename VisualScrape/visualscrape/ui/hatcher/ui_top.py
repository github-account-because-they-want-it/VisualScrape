'''
Created on Jul 12, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QWidget, QVBoxLayout, QGridLayout, QGroupBox
from PySide.QtCore import Signal
from browser import ActionTrackerWebView
from ui_common import ProgressLineEdit, LoadingWidget
from record_table import RecordTable
from api import BrowserWatcher
from jstest import ItemWatcher
from visualscrape.lib.scrapylib.crawlers import ScrapyProductCrawlerManager
import time

class Hatcher(QWidget):
  """
  Layouts the browser and it's output table. Emits a finished signal with
  the command line mode possibility and the spider path.
  """
  finished = Signal(bool, object)
  def __init__(self, parent=None):
    super(Hatcher, self).__init__(parent)
    browser_container = BrowserContainer()
    record_table = RecordTable(browser_container._browser)
    layout = QGridLayout()
    layout_table = QVBoxLayout()
    layout_table.addWidget(record_table)
    groupbox_table = QGroupBox()
    groupbox_table.setTitle(self.tr("Record table"))
    groupbox_table.setLayout(layout_table)
    row = 0; col = 0;
    layout.addWidget(browser_container, row, col, 1, 4)
    row += 1; col += 1
    layout.addWidget(groupbox_table, row, col, 1, 2)
    self.setLayout(layout)

class BrowserContainer(QWidget):
  """
  A widget that contains the browser and it's line edit and starts the
  javascript test when browser is finished
  """
  browser_finished = Signal(bool, object) # use scrapy, SpiderPath
  def __init__(self, parent=None):
    super(BrowserContainer, self).__init__(parent)
    self._browser = ActionTrackerWebView()
    self._browser.finished.connect(self.browser_finished)
    self._browser_watcher = BrowserWatcher(self._browser)
    self._browser.finished.connect(self._startJavascriptTest)
    self._lineedit_progress = ProgressLineEdit()
    self._browser.url_changed.connect(self._lineedit_progress.text_changed)
    self._browser.progress_changed.connect(self._lineedit_progress.setProgress)
    layout = QVBoxLayout()
    layout.addWidget(self._lineedit_progress)
    layout.addWidget(self._browser)
    self.setLayout(layout)
    
  def _startJavascriptTest(self):
    self._lineedit_progress.setEnabled(False)
    self.layout().removeWidget(self._browser)
    self._loading_widget = LoadingWidget(message=self.tr("Performing the JavaScript test to determine a suitable spider ..."))
    self.layout().addWidget(self._loading_widget)
    spider_path = self._browser_watcher.getPath()
    item_watcher = ItemWatcher()
    item_watcher.finished.connect(self._announceWatcherResults)
    ScrapyProductCrawlerManager.run_jstest(spider_path, item_watcher, itemCount=20)
    
  def _announceWatcherResults(self, useScrapy):
    if useScrapy:
      message = self.tr("Spider can be run with Scrapy (command line mode)")
    else:
      message = self.tr("Spider will have to run inside the browser")
    self._loading_widget.finished.emit(message)
    time.sleep(5)
    self.browser_finished.emit(useScrapy, self._browser_watcher.getPath())
"""
To say the last thing here is that some component will listen to the hatcher and 
instruct the config manager to initialize a new state for it. Thank myself.
"""