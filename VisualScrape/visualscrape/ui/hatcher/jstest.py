'''
Created on Jun 28, 2014
@author: Mohammed Hamdy
'''
from PySide.QtCore import Signal, QUrl, Qt
from PySide.QtWebKit import QWebView
from PySide.QtGui import QVBoxLayout, QDialog
import urllib2

class JavaScriptTest(object):
  """
  Run a test and emit a bool signal when finished. True means test succeeded, we can
  use scrapy. False means test failed, so using Selenium or the like is necessary.
  How can I set up a scrapy run for a path?.
  """
  finished = Signal(bool)
  FAIL_PERCENT = 0.50
  def __init__(self, itemUrl):
    self._item_url = itemUrl
    self.js_enabled_test = JavaScriptTestBrowserWindow(self._item_url)
    self.js_disabled_test = BasicJavascriptTest(self._item_url)
    
  def runTests(self):
    self._runTest1()
    self._runTest2()
    js_content = self.js_enabled_test.getContent()
    non_js_content = self.js_disabled_test.getContent()
    if len(non_js_content) > self.FAIL_PERCENT * len(js_content):
      self.finished.emit(False)
    else: self.finished.emit(True)
    
  def _runTest1(self):
    win = self.js_enabled_test
    win.show()
    win.run()
    
  def runTest2(self):
    self.js_disabled_test.run()
    
class JavaScriptTestBrowserWindow(QDialog):
  
  def __init__(self, itemUrl):
    super(JavaScriptTestBrowserWindow, self).__init__()
    self.setWindowModality(Qt.WindowModality.NonModal)
    self._item_url = itemUrl
    self._content = ''
    layout = QVBoxLayout()
    self.browser = QWebView()
    self.browser.loadFinished.connect(self._setContentAndClose)
    self.setLayout(layout)
    
  def run(self):
    self.browser.setUrl(QUrl(self._item_url))
  
  def _setContentAndClose(self, ok):
    if ok:
      self._content = self.browser.page().bytesReceived()
    else: self._content = ''
    self.close()
    
  def getContent(self):
    return self._content
  
class BasicJavascriptTest(object):
  def __init__(self, itemUrl):
    self._item_url = itemUrl
    self._content = ''
    
  def run(self):
    f = urllib2.urlopen(self._item_url)
    self._content = f.read()
    
  def getContent(self):
    return self._content