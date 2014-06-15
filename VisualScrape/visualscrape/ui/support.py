'''
Created on Jun 14, 2014
@author: Mohammed Hamdy
'''

from __future__ import division
from PySide.QtGui import QWidget, QPixmap, QPainter, QPen, QHBoxLayout
from PySide.QtCore import Qt, QPointF, Signal
from os import path


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
  