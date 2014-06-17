'''
Created on Jun 15, 2014
@author: Mohammed Hamdy
'''

from PySide.QtGui import QTableWidget, QTableWidgetItem, QCompleter, QTableView
from PySide.QtCore import Qt
import collections, re
from visualscrape.ui.slideshow import AnimatedSlideshowWidget

class ScrapeDataTable(QTableWidget):
  """This table imports magic but doesn't create it!"""
  
  def __init__(self, cellSize=(200, 200),parent=None):
    super(ScrapeDataTable, self).__init__(parent)
    self._cell_size = cellSize
    self._configured = False
    self._images_in_items = False
    self._orig_headers = []
    self._headers = []
      
  def addItem(self, item):
    """Means append a row with this item"""
    if not self._configured:
      self._configureTable(item)
      self._configured = True
      self.configure_search_lineedit(self._search_lineedit)
    new_row_index = self.rowCount()
    self.insertRow(new_row_index)
    values = []
    for col_name in self._orig_headers: # the orig_headers are ordered like the table columns
      if col_name in item: values.append(item[col_name])
      else: values.append('')
    if self._images_in_items:
      image_items = item.pop("images")
      image_paths = [image_item.get("path") for image_item in image_items]
      self.setColumnWidth(0, self._cell_size[0])
      self.setRowHeight(new_row_index, self._cell_size[1])
      self.setCellWidget(new_row_index, 0, AnimatedSlideshowWidget.slideshowCreator(image_paths))
    item.pop("id")
    for (col_index, text_data) in enumerate(values):
      self.setItem(new_row_index, col_index + 1, QTableWidgetItem(text_data))

  def _configureTable(self, item):
    # setup the various columns
    self.setColumnCount(len(item))
    images_in_item = "images" in item.keys() #the item may not have images_in_item
    ordered_item = collections.OrderedDict()
    keys = item.keys()
    if images_in_item : 
      keys.remove("images")
      self._images_in_items = True
    keys.sort(key=lambda key: key.lower())
    # bring the images key to be the first
    if images_in_item: keys = ["images"] + keys
    for key in keys:
      ordered_item[key] = item[key]
    headers = []
    self._orig_headers = keys[1:] if self._images_in_items else keys
    for key in keys:
      first, rest = key[0], key[1:]
      header = first.upper() + rest.lower()
      headers.append(header)
    self._headers = headers
    for (i, header) in enumerate(headers):
      self.setHorizontalHeaderItem(i, QTableWidgetItem(header))
    self.horizontalHeader().setMovable(True)
    
  def configure_search_lineedit(self, lineEdit):
    if not self._configured: # no data received yet. hold on configuration
      self._search_lineedit = lineEdit
    else:
      splitter = lineEdit.column_query_splitter
      completer = QCompleter([header+splitter for header in self._headers[1:]]) # search anything but the image column
      completer.setCaseSensitivity(Qt.CaseInsensitive)
      lineEdit.setCompleter(completer)
      lineEdit.textChanged.connect(self.query)
      self._column_query_sep = splitter
    
  def query(self, queryText):
    """Search the table using the column and search text in the query"""
    sep_pos = queryText.find(self._column_query_sep)
    if sep_pos < 0: return
    column_name, query = queryText[:sep_pos], queryText[sep_pos + len(self._column_query_sep):]
    if column_name not in self._headers[1:]:
      return
    if not query: # empty query: show all rows
      [self.showRow(i) for i in range(self.rowCount())]
      return
    # hide all rows in which the query doesn't match the specified column
    search_col_index = self._headers.index(column_name)
    query = query.lower()
    query_words = re.split("\s+", query)
    for i in range(self.rowCount()):
      col_item = self.item(i, search_col_index)
      item_text = col_item.text().lower()
      all_in = [query_word in item_text for query_word in query_words] # multi-word query support. I hope I don't reimplement Google
      if all_in:
        self.showRow(i)
      else:
        self.hideRow(i)

class ScrapeTable(QTableView):
  """The table view approach to visualization"""
  def __init__(self, parent=None):
    from visualscrape.ui.support import ScrapeModel, ScrapeItemDelegate
    super(ScrapeTable, self).__init__(parent)
    """Use a delegate that can display an image in a column"""
    self.setModel(ScrapeModel())
    self.setItemDelegate(ScrapeItemDelegate())
    self.resizeRowsToContents()
    self.resizeColumnsToContents()
    self.horizontalHeader().setMovable(True)