'''
Created on Jun 15, 2014
@author: Mohammed Hamdy
'''

from PySide.QtGui import QTableWidget, QTableWidgetItem, QCompleter, QTableView
from PySide.QtCore import Qt, Signal
import collections, re
from visualscrape.ui.viewer.slideshow import AnimatedSlideshowWidget
from visualscrape.lib.data import ProducerMixin, DataStore

class ScrapeDataTable(QTableWidget, ProducerMixin):
  """This table imports magic but doesn't create it!"""
  
  def __init__(self, cellSize=(200, 200), name='', parent=None):
    # the table gets it's name as the spider name
    QTableWidget.__init__(self, parent)
    ProducerMixin.__init__(self, type=ProducerMixin.TYPE_TABLE, name=name)
    self._cell_size = cellSize
    self._configured = False
    self._images_in_items = False
    self._orig_headers = []
    self._headers = []
    self._visible_rows = "all" # a list of ints. "all" means no searches done yet
    self._items = []
    self._active = False
      
  def addItem(self, item):
    """Means append a row with this item"""
    if not self._configured:
      self._configureTable(item)
      self._configured = True
      self.configure_search_lineedit(self._search_lineedit)
    self._items.append(item)
    new_row_index = self.rowCount()
    self.insertRow(new_row_index)
    values = [] # values to insert in a table row
    for col_name in self._orig_headers: # the orig_headers are ordered like the table columns
      if col_name in item: values.append(item[col_name])
      else: values.append('')
    if self._images_in_items:
      image_items = item.pop("images")
      image_paths = [image_item.get("path") for image_item in image_items]
      self.setColumnWidth(0, self._cell_size[0])
      self.setRowHeight(new_row_index, self._cell_size[1])
      self.setCellWidget(new_row_index, 0, AnimatedSlideshowWidget.slideshowCreator(image_paths))
    self._insertColumns(new_row_index, values)
    
  def _insertColumns(self, row, values):
    for (col_index, text_data) in enumerate(values):
      col_index = col_index + 1 if self._images_in_items else col_index
      self.setItem(row, col_index, QTableWidgetItem(str(text_data)))
      
  def is_active(self):
    return self._active
  
  def set_active(self, state):
    self._active = state

  def _configureTable(self, item):
    # setup the various columns
    self.setColumnCount(len(item)) # TODO: this might be buggy to set the columns only from the first item, which might be incomplete
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
    self._orig_headers = keys[1:] if self._images_in_items else keys # those are the headers before using capital first and so on
    for key in keys:
        first, rest = key[0], key[1:]
        header = first.upper() + rest.lower()
        headers.append(header)
    self._headers = headers
    for (i, header) in enumerate(headers):
      self.setHorizontalHeaderItem(i, QTableWidgetItem(header))
    self.horizontalHeader().setMovable(True)
    

class SearchTable(ScrapeDataTable):
  """Extends ScrapeDataTable with some dirty search functionality
     Works as a signal bridge for internal display labels"""
  search_changed = Signal(str)
  search_cancelled = Signal()
  replace_committed = Signal(str, str)
  
  def _insertColumns(self, row, values):
    """Overrides same method from parent to replace table cells with wicked labels"""
    from visualscrape.ui.viewer.support import SearchReplaceLabel
    for (col_index, text_data) in enumerate(values):
      if not isinstance(text_data, (str, unicode)):
        text_data = unicode(text_data)
      highlighter = SearchReplaceLabel(text_data)
      self.search_changed.connect(highlighter.search_changed)
      self.search_cancelled.connect(highlighter.search_cancelled)
      self.replace_committed.connect(highlighter.replace_committed)
      col_index = col_index + 1 if self._images_in_items else col_index
      self.setCellWidget(row, col_index, highlighter)
    
  def configure_search_lineedit(self, lineEdit):
    if not self._configured: # no data received yet. hold on configuration
      self._search_lineedit = lineEdit
    else:
      splitter = lineEdit.column_query_splitter
      completer = QCompleter([header+splitter for header in self._headers[1:]]) # search anything but the image column
      completer.setCaseSensitivity(Qt.CaseInsensitive)
      lineEdit.setCompleter(completer)
      lineEdit.textEdited.connect(self.query)
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
    self._visible_rows = []
    search_col_index = self._headers._index(column_name)
    query = query.lower()
    query_words = re.split("\s+", query)
    for i in range(self.rowCount()):
      col_item = self.cellWidget(i, search_col_index)
      item_text = col_item.text().lower()
      all_in = all([query_word in item_text for query_word in query_words]) # multi-word query support. I hope I don't reimplement Google
      if all_in:
        self.showRow(i)
        self._visible_rows.append(i)
      else:
        self.hideRow(i)
    
  def get_visible_data(self):
    """Return a list of dictionaries of the currently visible rows"""
    if self._visible_rows == "all":
      return self._items
    else:
      visible_data = []
      for row_i in self._visible_rows:
        visible_data.append(self._items[row_i])
      return visible_data
  
class ScrapeTable(QTableView):
  """The table view approach to visualization"""
  def __init__(self, parent=None):
    from visualscrape.ui.viewer.support import ScrapeModel, ScrapeItemDelegate
    super(ScrapeTable, self).__init__(parent)
    """Use a delegate that can display an image in a column"""
    self.setModel(ScrapeModel())
    self.setItemDelegate(ScrapeItemDelegate())
    self.resizeRowsToContents()
    self.resizeColumnsToContents()
    self.horizontalHeader().setMovable(True)