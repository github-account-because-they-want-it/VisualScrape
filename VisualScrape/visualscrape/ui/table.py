'''
Created on Jun 15, 2014
@author: Mohammed Hamdy
'''

from PySide.QtGui import QTableWidget, QTableWidgetItem, QCompleter, QTableView
from PySide.QtCore import Qt
import json, collections
from visualscrape.ui.slideshow import AnimatedSlideshowWidget
from visualscrape.ui.support import ScrapeModel, ScrapeItemDelegate

class ScrapeDataTable(QTableWidget):
  """This table imports magic but doesn't create it!"""
  
  def __init__(self, cellSize=(200, 200),parent=None):
    super(ScrapeDataTable, self).__init__(parent)
    self._cell_size = cellSize
    f = open("example.json")
    self.json_data = json.load(f) # this is an array of dicts
    for i, item in enumerate(self.json_data):
      images_in_item = "images" in item.keys() #the item may not have images_in_item
      ordered_item = collections.OrderedDict()
      favicon_item = images_in_item and len(item.get("images")) == 1 and \
        "favicon.ico" in item.get("images")[0].get("url")
      # filter the favicon item if it exists. This belongs to the UI, not to the table
      if favicon_item: self.json_data.pop(i)
      else: # ok, not a favicon. process it's keys and sort them for display
        keys = item.keys()
        if images_in_item : keys.remove("images")
        keys.sort(key=lambda key: key.lower())
        # bring the images key to be the first
        if images_in_item: keys = ["images"] + keys
        for key in keys:
          ordered_item[key] = item[key]
        # replace data using this sorted keys
        self.json_data[i] = ordered_item
    f.close()
    # prefetch the table headers. ride some camels
    headers = []
    for key in keys:
      first, rest = key[0], key[1:]
      header = first.upper() + rest.lower()
      headers.append(header)
    self._headers = headers
    self.setRowCount(len(self.json_data))
    self.setColumnCount(len(item)) # the last item
    for (i, header) in enumerate(headers):
      self.setHorizontalHeaderItem(i, QTableWidgetItem(header))
    self.horizontalHeader().setMovable(True)
    self.populateTable()
    
  def populateTable(self):
    for (i, data_row) in enumerate(self.json_data):
      values = data_row.values()
      image_items = values[0]
      image_paths = [image_item.get("path") for image_item in image_items]
      self.setCellWidget(i, 0, AnimatedSlideshowWidget.slideshowCreator(image_paths))
      for (j, text_data) in enumerate(values[1:]):
        self.setItem(i, j + 1, QTableWidgetItem(text_data))
      self.setColumnWidth(0, self._cell_size[0])
      self.setRowHeight(i, self._cell_size[1])

  def configure_lineedit(self, lineEdit):
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
    super(ScrapeTable, self).__init__(parent)
    """Use a delegate that can display an image in a column"""
    self.setModel(ScrapeModel())
    self.setItemDelegate(ScrapeItemDelegate())
    self.resizeRowsToContents()
    self.resizeColumnsToContents()
    self.horizontalHeader().setMovable(True)