'''
Created on Jun 14, 2014
@author: Mohammed Hamdy
'''

from __future__ import division
from PySide.QtGui import (QWidget, QPixmap, QPainter, QPen, QHBoxLayout, QStyledItemDelegate,
                          QLineEdit, QSizePolicy, QGridLayout, QProgressBar,QPushButton, QLabel,
                          QMessageBox, QMenu, QAction, QTabBar, QTabWidget)
from PySide.QtCore import Qt, QPointF, QAbstractTableModel, QSize, QTimer, Signal
from os import path
import json, collections
from visualscrape.ui.viewer.style import search_style
from visualscrape.ui.viewer.table import SearchTable
from visualscrape.ui.viewer.dialog import ExportDialog
from visualscrape.lib.signal import SpiderClosed
from visualscrape.lib.export import FileExporter
from visualscrape.lib.data import NamedAction

class ImageWidget(QWidget):
  """
  A widget that displays an image.
  """
  def __init__(self, imagePath, fill=True, parent=None):
    """
    Args:
      imagePath : a system path that points to an image fles
      fill : boolean that when True, makes the image fill the widget, whatever
             the current widget size. When False, just draws the image at it's original
             size.
    """
    super(ImageWidget, self).__init__(parent)
    assert imagePath != None, self.tr("Invalid image path")
    self._image_pixmap = QPixmap(path.normpath(imagePath))
    self._fill = fill
    
  def paintEvent(self, pe):
    painter = QPainter(self) 
    if self._fill:
      scaled_pixmap = self._image_pixmap.scaled(self.size(), Qt.IgnoreAspectRatio)
      painter.drawPixmap(0, 0, scaled_pixmap)
    else:
      painter.drawPixmap(0, 0, self._image_pixmap)
      
class ControlOverlay(QWidget):
  """An area with a background that has a front shape, currently an arrow.
     It's a fucking custom button!, and emits a click signal when clicked"""
  LEFT = 0
  RIGHT = 1
  ARROW_LINE_WIDTH = 5
  BACKGROUND_OPACITY = 0.25
  BACKROUND_HEIGHT_PERCENT = 0.33
  ARROW_WIDTH_PERCENT = 0.1
  ARROW_HEIGHT_PERCENT = 0.2
  clicked = Signal()
  def __init__(self, controlDirection=RIGHT,parent=None):
    super(ControlOverlay, self).__init__(parent)
    self.setMouseTracking(True)
    self.setAutoFillBackground(False) # I want it transparent
    self._direction = controlDirection
    self._normal_color = Qt.gray
    self._hover_color = Qt.darkMagenta
    self._mouse_inside = False
    self._arrow_height = 0
    self._arrow_width = 0
  
  def paintEvent(self, pe):
    # make an arrow polygon right in the middle
    painter = QPainter(self)
    painter.setPen(Qt.NoPen)
    # draw the background transparent rect
    painter.save()
    painter.setOpacity(self.BACKGROUND_OPACITY)
    # get the rectangle coordinates it should extend over the whole width with only a portion at the center
    painter.setBrush(Qt.black)
    empty_space_percent = 1 - self.BACKROUND_HEIGHT_PERCENT
    rect_top = empty_space_percent / 2 * self.height()
    rect_height = self.BACKROUND_HEIGHT_PERCENT * self.height()
    painter.drawRect(0, rect_top, self.width(), rect_height)
    painter.restore()
    painter.setRenderHint(QPainter.Antialiasing)
    pen = QPen()
    pen.setWidth(self.ARROW_LINE_WIDTH)
    pen.setCapStyle(Qt.RoundCap)
    if self._mouse_inside:
      pen.setColor(self._hover_color)
    else:
      pen.setColor(self._normal_color)
    # get the arrow coords
    painter.setPen(pen)
    self_center = QPointF(self.width() / 2, self.height() / 2) # use this as the arrow tip for now
    if self._direction == self.LEFT:
      h_shift = self._arrow_width
    elif self._direction == self.RIGHT:
      h_shift = - self._arrow_width
    v_shift = self._arrow_height / 2
    top_point = self_center + QPointF(h_shift, - v_shift)
    bottom_point = self_center + QPointF(h_shift, v_shift)
    painter.drawLine(top_point, self_center)
    painter.drawLine(self_center, bottom_point)
    
  def resizeEvent(self, re):
    self._arrow_height = self.height() * self.ARROW_HEIGHT_PERCENT
    self._arrow_width = self.width() * self.ARROW_WIDTH_PERCENT
  
  def mouseMoveEvent(self, mme):
    self._mouse_inside = True
    self.setCursor(Qt.CursorShape.PointingHandCursor)
    self.repaint()
    
  def leaveEvent(self, le):
    self._mouse_inside = False
    self.repaint()
    
  def mousePressEvent(self, pe):
    self.clicked.emit()
    
class OverlayContainer(QWidget):
  """Houses the layout that contains navigation buttons.
     Here mainly to hide itself when the mouse leaves it"""
  OVERLAY_WIDTH_PERCENT = 0.15
  OVERLAY_HEIGHT_PERCENT = 0.30
  right_clicked = Signal()
  left_clicked = Signal()
  
  def __init__(self, parent=None):
    super(OverlayContainer, self).__init__(parent)
    overlay_layout = QHBoxLayout()
    self._right_overlay = ControlOverlay()
    self._right_overlay.clicked.connect(self.right_clicked)
    self._left_overlay = ControlOverlay(controlDirection=ControlOverlay.LEFT)
    self._left_overlay.clicked.connect(self.left_clicked)
    overlay_layout.addWidget(self._left_overlay)
    overlay_layout.addStretch()
    overlay_layout.setContentsMargins(0,0,0,0)
    overlay_layout.addWidget(self._right_overlay)
    self.setLayout(overlay_layout)
    
  def resizeEvent(self, re):
    # fix the height of buttons, because they don't have a layout or size, and rely on painting
    self_height = self.height()
    self._left_overlay.setFixedHeight(self_height * self.OVERLAY_HEIGHT_PERCENT)
    self._right_overlay.setFixedHeight(self_height * self.OVERLAY_HEIGHT_PERCENT)
    self_width = self.width()
    self._left_overlay.setFixedWidth(self_width * self.OVERLAY_WIDTH_PERCENT)
    self._right_overlay.setFixedWidth(self_width * self.OVERLAY_WIDTH_PERCENT)
    super(OverlayContainer, self).resizeEvent(re)
    
  def leaveEvent(self, le):
    self.hide()
  
class ScrapeModel(QAbstractTableModel):
  """The data could be coming from a json file, database or obtained dynamically from a running spider
     Puts the image column as the first one by default."""
  def __init__(self, parent=None):
    super(ScrapeModel, self).__init__(parent)
    #read data from json
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
    # prefetch the table headers. ride some camels
    headers = []
    for key in keys:
      first, rest = key[0], key[1:]
      header = first.upper() + rest.lower()
      headers.append(header)
    self._headers = headers
    
  def rowCount(self, parent):
    return len(self.json_data)
  
  def columnCount(self, parent):
    return len(self._headers)
      
  def headerData(self, section, orientation, role=Qt.DisplayRole):
    if role == Qt.DisplayRole and orientation == Qt.Orientation.Horizontal:
      return self._headers[section]
    
  def data(self, index, role=Qt.DisplayRole):
    if role == Qt.DisplayRole:
      row = index.row(); col = index.column()
      data_row = self.json_data[row]
      data_key = data_row.keys()[col] #means a column name, but the original
      data = data_row.get(data_key, '')
      return data
    elif role == Qt.TextAlignmentRole:
      return Qt.AlignCenter
    
  def flags(self, index):
    return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class ScrapeItemDelegate(QStyledItemDelegate):
  """A delegate that displays a scaled image in the first column for a 
     table view"""
  def __init__(self, maxCellRes=(200, 200), parent=None):
    """
    Args:
      maxCellRes -- if there are images in the items, it won't be painted bigger than this resolution
    """
    super(ScrapeItemDelegate, self).__init__(parent)
    self.max_cell_res = maxCellRes
    # display images and slideshows. Be as magical as you can.
    
  def paint(self, painter, option, index):
    if index.column() != 0: # not the image column
      super(ScrapeItemDelegate, self).paint(painter, option, index)
    else:
      images = index.data(role=Qt.DisplayRole)
      if images:
        # yep. Make an image appear here
        image_data = images[0] # assuming a single image for now
        pixmap = QPixmap(image_data.get("path"))
        pixmap = pixmap.scaled(self.max_cell_res[0], self.max_cell_res[1], Qt.IgnoreAspectRatio)
        cell_rect = option.rect
        painter.drawPixmap(cell_rect.x(), cell_rect.y(), pixmap) 
      else:
        super(ScrapeItemDelegate, self).paint(painter, option, index)
  
  def sizeHint(self, option, index):
    if index.column() != 0:
      return super(ScrapeItemDelegate, self).sizeHint(option, index)
    else:
      images = index.data(role=Qt.DisplayRole)
      if images:
        return QSize(self.max_cell_res[0], self.max_cell_res[1])
      else:
        return super(ScrapeItemDelegate, self).sizeHint(option, index)


class ScrapeSearchLineEdit(QLineEdit):
  """Implements interface SearchLineEdit and handles focusing"""
  column_query_splitter = ": "
  
  def __init__(self, *args, **kwargs):
    super(ScrapeSearchLineEdit, self).__init__(*args, **kwargs)
    self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    self.setStyleSheet(search_style)
    self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    self._search_str = self.tr("Search: ")
    self.setText(self._search_str)
    
  def focusInEvent(self, fie):
    if self.text() == self._search_str:
      self.clear()
    super(ScrapeSearchLineEdit, self).focusInEvent(fie)
  
  def focusOutEvent(self, foe):
    if not self.text():
      self.setText(self._search_str)
    super(ScrapeSearchLineEdit, self).focusOutEvent(foe)
      
      
class SpiderTab(QWidget):
  """Has handlers for spider data and events. It houses the results table of the
     spider, controls for the spider and progress indication
     It implicitly conforms to IEventHandler interface"""
  TIMER_CHECK_INTERVAL = 3000
  favicon_received = Signal(str) # send the url or path to the handler, which should be the tab widget
  stop_spider_signal = Signal(int)
  became_current = Signal(bool) # tell the table it has become active. it's an interesting property for producers!
  
  def __init__(self, parent=None, **kwargs):
    super(SpiderTab, self).__init__(parent)
    self._event_queue = None
    self._data_queue = None
    self._engine = None
    self._favicon_received = False
    self._spider_id = None
    self._item_count = 0
    self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
    self.initInterface(kwargs)
    self._context_menu = None
    self._setupContextMenu()
    self.became_current.connect(self._set_table_activity)
    self._queue_check_timer = QTimer()
    self._queue_check_timer.setInterval(self.TIMER_CHECK_INTERVAL)
    self._queue_check_timer.timeout.connect(self._checkQueues)
    self._queue_check_timer.start()
    
  def initInterface(self, kwargs):
    layout = QGridLayout()
    self._data_table = SearchTable(name=kwargs.get("name"))
    self._progress_spider = QProgressBar()
    self._label_count = QLabel(self.tr("0 items scraped"))
    # make it a busy indicator. you don't know when it'll finish 
    self._progress_spider.setMinimum(0); self._progress_spider.setMaximum(0)
    self._progress_spider.setTextVisible(False)
    self._btn_stop_spider = QPushButton(self.tr("Stop Spider"))
    self._btn_stop_spider.clicked.connect(self.stop_spider)
    row = 0; col = 0;
    layout.addWidget(self._data_table, row, col, 1, 4)
    row += 1;
    layout.addWidget(self._progress_spider, row, col, 1, 1)
    col += 1
    layout.addWidget(self._label_count, row, col, 1, 2)
    col += 2
    layout.addWidget(self._btn_stop_spider, row, col, 1, 1)
    self.setLayout(layout)
    
  def _setupContextMenu(self):
    from visualscrape.lib.data import ActionStore
    self._context_menu = QMenu(self)
    # get the export action from the action store
    action_store = ActionStore.get_instance()
    for action in action_store:
      if action.get_name() == "export":
        export_action = action
        break
    self._context_menu.addAction(export_action)
    
  def export_table(self):
    export_dialog = ExportDialog()
    export_dialog.exec_()
    export_info = export_dialog.data()
    if export_info:
      data = self._data_table.get_visible_data()
      FileExporter.export(data, self._data_table.name.lower(), export_info.location, export_info.format)
  
  def contextMenuEvent(self, cme):
    rel_pos = cme.pos()
    global_pos = self.mapToGlobal(rel_pos)
    self._context_menu.popup(global_pos)
    
  def set_event_queue(self, eq):
    self._event_queue = eq
    
  def set_data_queue(self, dq):
    self._data_queue = dq
    
  def stop_spider(self):
    if self._spider_id is None: # do not stop the the spider before receiving data
      pass
    else:
      if self._queue_check_timer.isActive():
        confirm_stop = QMessageBox(self)
        confirm_stop.setIcon(QMessageBox.Warning)
        confirm_stop.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm_stop.setText(self.tr("Scraping process still running"))
        confirm_stop.setDetailedText(self.tr("Are you sure you want to stop it?"))
        ret = confirm_stop.exec_()
        if ret == QMessageBox.Yes:
          self.stop_spider_signal.emit(self._spider_id)
          return True
        else: return False # I won't whip you if you stop it accidentally
      else: return True # already over
      
  def configure_searchlineedit(self, lineEdit):
    self._data_table.configure_search_lineedit(lineEdit)
    
  def _checkQueues(self):
    while not self._event_queue.empty():
      event = self._event_queue.get(block=False, timeout=0)
      if isinstance(event, SpiderClosed):
        self._queue_check_timer.stop()
        self._progress_spider.setMinimum(0)
        self._progress_spider.setMaximum(100)
        self._progress_spider.setValue(100)
        self._btn_stop_spider.setEnabled(False)
    while not self._data_queue.empty():
      item = self._data_queue.get(block=False, timeout=0)
      if not self._favicon_received: # the first item on the data queue should be the favicon
        favicon_data = item["images"][0]
        self.favicon_received.emit(favicon_data["path"]) # note that icons are not guaranteed to have a path. Not everybody wants to save images
        self._favicon_received = True
        self._spider_id = item["_id"]
      else:
        item.pop("_id") # the table has nothing to do with spider ids
        self._data_table.addItem(item)
      self._item_count += 1
      self._label_count.setText(self.tr("{0:n} items scraped".format(self._item_count)))
      
  def _set_table_activity(self, state):
    self._data_table.set_active(state)
    

class ContextMenuTabBar(QTabBar):
  """A tab bar that responds to context menu events
    it just saves the index of tab that received the 
    context event
    Args:
      contextMenu: the context menu to show on context menu events
    """
  
  def __init__(self, contextMenu, parent=None):
    super(ContextMenuTabBar, self).__init__(parent)
    self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
    self._event_tab_index = None # the tab that received the last context menu event
    self._context_menu = contextMenu
    
  def contextMenuEvent(self, cme):
    rel_pos = cme.pos()
    global_pos = self.mapToGlobal(rel_pos)
    self._context_menu.popup(global_pos)
    # find the tab that received the mouse click
    for tab_i in range(self.count()):
      tab_rect = self.tabRect(tab_i)
      if tab_rect.contains(rel_pos):
        self._event_tab_index = tab_i
        
  def last_event_tab(self):
    return self._event_tab_index
  
class ContextMenuTabWidget(QTabWidget):
  """A tab widget witha a custom tab bar.
     Also acts as a notifier for tabs that they have become active or inactive"""
  def __init__(self, parent=None):
    super(ContextMenuTabWidget, self).__init__(parent)
    self._setupContextMenu()
    self.currentChanged.connect(self._notifyTabs)
    
  def _setupContextMenu(self):
    from visualscrape.lib.data import ActionStore
    context_menu = QMenu(self)
    export_action = NamedAction(self.tr("Export ..."), self, name="export")
    export_action.triggered.connect(self._requestTabExport)
    context_menu.addAction(export_action)
    self.setTabBar(ContextMenuTabBar(context_menu))
    action_store = ActionStore.get_instance()
    action_store.register_action(export_action)
    
  def _requestTabExport(self):
    tab_right_clicked_index = self.tabBar().last_event_tab()
    tab_right_clicked = self.widget(tab_right_clicked_index)
    tab_right_clicked.export_table()
    
  def _notifyTabs(self, tabIndex):
    for tab_index in range(self.count()):
      if tab_index == tabIndex: self.widget(tab_index).became_current.emit(True)
      else: self.widget(tab_index).became_current.emit(False)
    
class SearchHighlighterLabel(QLabel):
  """Highlights text using Qt.color instance as long as it's search_changed
     signal is emitted with search text"""
  search_changed = Signal(str)
  search_cancelled = Signal()
  
  def __init__(self, text, highlightColor=Qt.red, parent=None):
    super(SearchHighlighterLabel, self).__init__(parent)
    self._original_text = text # keep it because the internal text will have extraneous formatting
    self.setText(text)
    self.setWordWrap(True)
    self._highlight_color = highlightColor
    self.search_changed.connect(self._updateText)
    self.search_cancelled.connect(lambda: self.setText(self._original_text))
    
  def _updateText(self, searchText):
    self.setText(self._original_text)
    if not searchText: # an empty string matches everything
      return
    searchText = searchText.strip()
    string_template = self._original_text
    highlight_color_string = self._getColorString(self._highlight_color)
    string_template = string_template.replace(searchText, 
                          "<font color='{0}'>{1}</font>".format(highlight_color_string, searchText))
    self.setText(string_template)
     
  def _getColorString(self, color):
    dot_pos = str(color).rfind('.') + 1
    return str(color)[dot_pos:]   

class SearchReplaceLabel(SearchHighlighterLabel):
  
  replace_committed = Signal(str, str)
  
  def __init__(self, text, replaceColor=Qt.yellow, highlightColor=Qt.red, replaceTimeout=2):
    super(SearchReplaceLabel, self).__init__(text, highlightColor)
    self._replace_color = replaceColor
    self.replace_committed.connect(self._replaceText)
    self._replacement_fade_timer = QTimer()
    self._replacement_fade_timer.setSingleShot(replaceTimeout)
    self._replacement_fade_timer.timeout.connect(self._putOriginalText)
    
  def _replaceText(self, before, after):
    self.setText(self._original_text) # replace formatting after recent find activity
    self._original_text = self._original_text.replace(before, after)
    replacement = self._original_text.replace(before, "<font color='{0}'>{1}</font>".\
                                              format(self._getColorString(self._replace_color), after))
    self.setText(replacement)
    self._replacement_fade_timer.start()
    
  def _putOriginalText(self):
    self.setText(self._original_text)