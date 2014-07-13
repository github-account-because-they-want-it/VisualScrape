'''
Created on Jul 12, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QWidget, QVBoxLayout
from browser import TrackerWebView
from ui_common import ProgressLineEdit, LoadingWidget
from api import BrowserWatcher
from jstest import JavaScriptTest
from visualscrape.lib.path import Form, URL

class BrowserManager(QWidget):
  """
  A widget that contains the browser and it's line edit and generally connects it
  with the outside world
  """
  
  def __init__(self, parent=None):
    super(BrowserManager, self).__init__(parent)
    self._browser = TrackerWebView()
    self._browser_watcher = BrowserWatcher(self._browser)
    self._browser.finished.connect(self._startJavascriptTest)
    lineedit_progress = ProgressLineEdit()
    self._browser.url_changed.connect(lineedit_progress.text_changed)
    self._browser.progress_changed.connect(lineedit_progress.setProgress)
    layout = QVBoxLayout()
    layout.addWidget(lineedit_progress)
    layout.addWidget(self._browser)
    
  def _startJavascriptTest(self):
    spider_path = self._browser_watcher.getPath()
    # for now, just operate on the first node of the path
    test_page = spider_path[0]
    