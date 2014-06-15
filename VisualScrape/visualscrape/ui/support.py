'''
Created on Jun 14, 2014
@author: Mohammed Hamdy
'''

from __future__ import division
from PySide.QtGui import (QWidget, QPixmap, QPainter, QPen, QHBoxLayout, QStyledItemDelegate,
                          QLineEdit, QSizePolicy)
from PySide.QtCore import Qt, QPointF, Signal, QAbstractTableModel, QSize
from os import path
import json, collections
from visualscrape.ui.style import search_style

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
    assert imagePath != None, "Invalid image path"
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
    self.setText("Search: ")
    
  def focusInEvent(self, fie):
    if self.text() == "Search: ":
      self.clear()
    super(ScrapeSearchLineEdit, self).focusInEvent(fie)
  
  def focusOutEvent(self, foe):
    if not self.text():
      self.setText("Search: ")