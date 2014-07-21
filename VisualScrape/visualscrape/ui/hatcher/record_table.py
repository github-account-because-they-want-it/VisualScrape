'''
Created on Jul 16, 2014
@author: Mohammed Hamdy
'''

from PySide.QtGui import QTableView, QIcon
from PySide.QtCore import QAbstractTableModel, Qt, QModelIndex

class RecordTable(QTableView):
  
  def __init__(self, browser, parent=None):
    super(RecordTable, self).__init__(parent)
    self.setModel(RecordTableModel(browser))
    
class RecordTableModel(QAbstractTableModel):
  
  def __init__(self, browser, parent=None):
    super(RecordTableModel, self).__init__(parent)
    self._data = [] # a list of dictionaries {"action":"action", "value":"value"}, ..
    browser.url_changed.connect(self._handleUrlChanged)
    browser.form_detected.connect(self._handleFormDetect)
    browser.image_download_changed.connect(self._handleImageDownload)
    browser.element_scrape_changed.connect(self._handleElementScrapeChanged)
    browser.attribute_scrape_changed.connect(self._handleAttributeChanged)
    browser.table_scrape_changed.connect(self._handleTableChanged)
    browser.item_page_selected.connect(self._handleItemPage)
    browser.similars_selected.connect(self._handleSimialrs)
    browser.link_clicked.connect(self._handleClick)
    browser.scroll_performed.connect(self._handleScroll)

  def rowCount(self, index):
    return len(self._data)
  
  def columnCount(self, index):
    return 2
  
  def data(self, index, role):
    if index.isValid(): # I think this is not necessary for a table
      row_data = self._data[index.row()]
      if role == Qt.DisplayRole:
        if index.column() == 0:
          return self._stringByAction(row_data)
        elif index.column() == 1:
          return row_data["value"]
      elif role == Qt.DecorationRole:
        if index.column() == 0:
          return self._iconByAction(row_data["action"])
        
  def headerData(self, section, orientation, role):
    if role == Qt.DisplayRole:
      if orientation == Qt.Horizontal:
        if section == 0:
          return self.tr("Action")
        elif section == 1:
          return self.tr("Value")
      else:
        return section
      
  def flags(self, index):
    return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
  
  def _handleUrlChanged(self, url):
    self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
    self._data.append({"action":BrowserActions.ACTION_VISIT, "value": url})
    self.endInsertRows()
    
  def _handleFormDetect(self, formDict):
    self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
    self._data.append({"action":BrowserActions.ACTION_FORM, "value":formDict})
    self.endInsertRows()
    
  def _handleImageDownload(self, checked, selector):
    if checked:
      self._data.append({"action":BrowserActions.ACTION_DOWNLOAD_IMAGE, "value":selector})
    else:
      i, table_item = self._findItemByValue(selector)
      self.beginRemoveRows(QModelIndex(), i, i)
      self._data.pop(i)
      self.endRemoveRows()
      
  def _handleElementScrapeChanged(self, checked, fieldName, selector):
    if checked:
      value_str = "{0:<20} <> {1:>35}".format(fieldName, selector)
      self._add_value(BrowserActions.ACTION_SELECT, value_str)
    else:
      i, to_remove = self._findItemByValue(selector)
      self.beginRemoveRows(QModelIndex(), i, i)
      self._data.pop(i)
      self.endRemoveRows()
      
  def _handleAttributeChanged(self, checked, fieldName, selector, attrName):
    if checked:
      value_str = "{<20} <> {>35}".format(fieldName, "::".join(selector, attrName))
      self._add_value(BrowserActions.ACTION_SELECT, value_str)
    else:
      i, to_remove = self._findItemByValue(selector)
      self._removeRowByIndex(i)
      
  def _handleTableChanged(self, checked, selector, tableType):
    if checked:
      value_str = selector
      self._add_value(BrowserActions.ACTION_TABLE_SELECT, value_str)
    else:
      i, to_remove = self._findItemByValue(selector)
      self._removeRowByIndex(i)
      
  def _handleItemPage(self, selector):
    value_str = selector
    self._add_value(BrowserActions.ACTION_SELECT, value_str)
    
  def _handleSimilars(self, selector):
    self._add_value(BrowserActions.ACTION_SELECT, selector)
    
  def _handleClick(self, selector):
    self._add_value(BrowserActions.ACTION_CLICK, selector)
  
  def _handleScroll(self):
    self._add_value(BrowserActions.ACTION_SCROLL, "New scroll")
      
  def _findItemByValue(self, selector):
    for i, item in enumerate(self._data):
      if selector in item["value"]:
        return i, item
  
  def _stringByAction(self, tableAction):
    if tableAction == BrowserActions.ACTION_CLICK:
      return "Click"
    if tableAction == BrowserActions.ACTION_DOWNLOAD_IMAGE:
      return "Download image"
    if tableAction == BrowserActions.ACTION_FORM:
      return "Form fill"
    if tableAction == BrowserActions.ACTION_SCROLL:
      return "Scroll"
    if tableAction == BrowserActions.ACTION_SELECT:
      return "Select"
    if tableAction ==  BrowserActions.ACTION_TABLE_SELECT:
      return "Scrape table"
    if tableAction == BrowserActions.ACTION_VISIT:
      return "Visit"
    
  def _iconByAction(self, tableAction):
    if tableAction == BrowserActions.ACTION_SELECT:
      return QIcon("selection")
    elif tableAction == BrowserActions.ACTION_CLICK:
      return QIcon("record_click")
    elif tableAction == BrowserActions.ACTION_SCROLL:
      return QIcon("record_scroll")
    elif tableAction == BrowserActions.ACTION_DOWNLOAD_IMAGE:
      return QIcon("image_download")
    elif tableAction == BrowserActions.ACTION_FORM:
      return QIcon("form_fill")
    elif tableAction == BrowserActions.ACTION_VISIT:
      return QIcon("url_visit")
        
  def _add_value(self, action, value):
    self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
    self._data.append({"action":action, "value":value})
    self.endInsertRows()
    
  def _removeRowByIndex(self, i):
    self.beginRemoveRows(QModelIndex(), i, i)
    self._data.pop(i)
    self.endRemoveRows()
  
class BrowserActions(object):
  ACTION_VISIT = 1
  ACTION_FORM = 2
  ACTION_SELECT = 3
  ACTION_CLICK = 4
  ACTION_SCROLL = 5
  ACTION_DOWNLOAD_IMAGE = 6 # may this have an independent ICON
  ACTION_TABLE_SELECT = 7