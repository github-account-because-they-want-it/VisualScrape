'''
Created on Jun 15, 2014
@author: Mohammed Hamdy
'''

from PySide.QtGui import QTableWidget, QTableWidgetItem, QCompleter, QTableView
from PySide.QtCore import Qt
import collections
from visualscrape.ui.slideshow import AnimatedSlideshowWidget

class ScrapeDataTable(QTableWidget):
  """This table imports magic but doesn't create it!"""
  
  def __init__(self, cellSize=(200, 200),parent=None):
    super(ScrapeDataTable, self).__init__(parent)
    self._cell_size = cellSize
    self._configured = False
      
  def addItem(self, item):
    """Means append a row with this item"""
    if not self._configured:
      self._configureTable(item)
      self._configured = True
      self.configure_search_lineedit(self._search_lineedit)
    new_row_index = self.rowCount()
    values = item.values()
    image_items = values[0]
    image_paths = [image_item.get("path") for image_item in image_items]
    self.setCellWidget(new_row_index, 0, AnimatedSlideshowWidget.slideshowCreator(image_paths))
    for (col_index, text_data) in enumerate(values[1:]):
      self.setItem(new_row_index, col_index + 1, QTableWidgetItem(text_data))
    self.setColumnWidth(0, self._cell_size[0])
    self.setRowHeight(new_row_index, self._cell_size[1])

  def _configureTable(self, item):
    # setup the various columns
    self.setColumnCount(len(item))
    images_in_item = "images" in item.keys() #the item may not have images_in_item
    ordered_item = collections.OrderedDict()
    keys = item.keys()
    if images_in_item : keys.remove("images")
    keys.sort(key=lambda key: key.lower())
    # bring the images key to be the first
    if images_in_item: keys = ["images"] + keys
    for key in keys:
      ordered_item[key] = item[key]
    headers = []
    for key in keys:
      first, rest = key[0], key[1:]
      header = first.upper() + rest.lower()
      headers.append(header)
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
    for i in range(self.rowCount()):
      col_item = self.item(i, search_col_index)
      item_text = col_item.text().lower()
      if query in item_text:
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