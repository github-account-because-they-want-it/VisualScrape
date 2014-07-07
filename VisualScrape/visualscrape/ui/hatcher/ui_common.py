'''
Created on Jul 6, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QWidget, QPainter, QPixmap, QPen, QColor,\
  QBrush, QFont, QLineEdit, QStyle, QStyleOptionProgressBarV2, QComboBox, QStringListModel
from PySide.QtCore import Qt, QSize, Signal, QRect, QPropertyAnimation,\
  QEasingCurve

class IconWidget(QWidget):
  """A widget that is clickable, has a fixed size and draws
     an icon. Setting a tooltip is recommended"""
  clicked = Signal()
  def __init__(self, iconPath, iconSize=(32, 32), hoverOpacity=1, normalOpacity=0.25, parent=None):
    super(IconWidget, self).__init__(parent)
    self.setFixedSize(QSize(iconSize[0], iconSize[1]))
    self.setMouseTracking(True)
    self._icon_path = iconPath
    self._hover_opacity = hoverOpacity
    self._normal_opacity = normalOpacity
    self._mouse_over = False # this is correct because when an icon appears after another, it appears where the mouse is
    self._enabled = True
    
  def paintEvent(self, pe):
    painter = QPainter(self)
    icon = QPixmap(self._icon_path)
    icon = icon.scaled(self.size(), Qt.IgnoreAspectRatio)
    if not self._mouse_over or not self._enabled:
      painter.setOpacity(self._normal_opacity)
    else:
      painter.setOpacity(self._hover_opacity)
    painter.drawPixmap(0, 0, icon)
    
  def mouseMoveEvent(self, mme):
    if self._mouse_over: return
    self._mouse_over = True
    self.setCursor(Qt.CursorShape.PointingHandCursor)
    self.repaint()
    
  def leaveEvent(self, le):
    self._mouse_over = False
    self.repaint()
    
  def mousePressEvent(self, mpe):
    self.clicked.emit()
    
  def makeEnabled(self):
    self._enabled = True
    self.show()
    
  def makeDisabled(self):
    self._enabled = False
    self.hide()


class IconChangerWidget(QWidget):
  """Same as IconWidget but changes icon on hover and doesn't use the hand pointer"""
  clicked = Signal()
  def __init__(self, normalIcon, hoverIcon, resolution=(32, 32), parent=None):
    
    super(IconChangerWidget, self).__init__(parent)
    self._normal_icon = normalIcon
    self._hover_icon = hoverIcon
    self._resolution = resolution
    self._mouse_over = False
    self.setFixedSize(QSize(resolution[0], resolution[1]))
    self.setMouseTracking(True)
    
  def mouseMoveEvent(self, mme):
    if not self._mouse_over:
      self._mouse_over = True
      self.repaint()
    super(IconChangerWidget, self).mouseMoveEvent(mme)
    
  def leaveEvent(self, le):
    self._mouse_over = False
    self.repaint()
    
  def mousePressEvent(self, mpe):
    self.clicked.emit()
    
  def paintEvent(self, pe):
    if self._mouse_over:
      icon = self._hover_icon
    else:
      icon = self._normal_icon
    painter = QPainter(self)
    pixmap = QPixmap(icon)
    pixmap = pixmap.scaled(self.size(), Qt.IgnoreAspectRatio)
    painter.drawPixmap(0, 0, pixmap)
    
class CheckIconWidget(QWidget):
  """An icon widget that operates as a checkbox"""
  NORMAL_OPACITY = .5
  HOVER_OPACITY = .85
  FIRST_ICON = 1000
  SECOND_ICON = 2000
  
  checked = Signal(bool)
  
  def __init__(self, firstIcon, secondIcon, parent=None):
    super(CheckIconWidget, self).__init__(parent)
    self.setMouseTracking(True)
    self._mouse_over = False
    self._checked = False
    self._first_icon = QPixmap(firstIcon)
    self._second_icon = QPixmap(secondIcon)
    w1, w2 = self._first_icon.width(), self._second_icon.width()
    h1, h2 = self._first_icon.height(), self._second_icon.height()
    max_w = w1 if w1 > w2 else w2
    max_h = h1 if h1 > h2 else h2
    # set the size to contain both images, but they should have the same size
    self.setFixedSize(max_w, max_h)
    
  def mousePressEvent(self, mpe):
    self._checked = not self._checked
    self.checked.emit(self._checked)
    self.repaint()
    
  def mouseMoveEvent(self, mme):
    self._mouse_over = True
    self.setCursor(Qt.CursorShape.PointingHandCursor)
    self.repaint()
    
  def leaveEvent(self, le):
    self._mouse_over = False
    self.repaint()
    
  def paintEvent(self, pe):
    painter = QPainter(self)
    if self._checked:
      pixmap = self._second_icon
    else:
      pixmap = self._first_icon
      
    if self._mouse_over:
      painter.setOpacity(self.HOVER_OPACITY)
    else:
      painter.setOpacity(self.NORMAL_OPACITY)  
    painter.drawPixmap(0, 0, pixmap)


class MessageWidget(QWidget):
  DEFAULT_MESSAGE_STRING = ''
  DEFAULT_OPACITY = 0.60
  HEIGHT = 32
  def __init__(self, messageString=DEFAULT_MESSAGE_STRING, opacity=DEFAULT_OPACITY,
               margin=4, parent=None):
    super(MessageWidget, self).__init__(parent)
    self._message_str = messageString
    self._margin = margin
    self._opacity = opacity
    self.setMaximumHeight(self.HEIGHT)
    
  def setMessage(self, message):
    self.show()
    self._message_str = message
    self.repaint()
    
  def paintEvent(self, pe):
    painter = QPainter(self)
    painter.save()
    background = QColor(55, 55, 55)
    brush = QBrush(background)
    painter.setOpacity(self._opacity)
    painter.setBrush(brush)
    painter.setPen(Qt.NoPen)
    painter.drawRect(self.rect())
    painter.restore()
    # draw a bottom border
    painter.setPen(Qt.black)
    painter.drawLine(0, self.height(), self.width(), self.height())
    # now the text
    pen = QPen(Qt.white)
    pen.setWidth(16)
    painter.setPen(pen)
    painter.setFont(QFont("Trebuchet MS", 16, QFont.Bold))
    text_rect = QRect(self.rect())
    text_rect.adjust(self._margin, self._margin, self._margin, self._margin)
    painter.drawText(text_rect, Qt.AlignLeft, self._message_str)
    
class ClosableMessage(MessageWidget):
  def __init__(self, closeWidget, messageString='', 
               opacity=0.60, parent=None):
    super(ClosableMessage, self).__init__(messageString, opacity, parent=parent)
    self._close_widget = closeWidget
    self._close_widget.setParent(self)
    self._close_widget.clicked.connect(self._closeMessage)
    
  def _closeMessage(self):
    self.hide()
    
  def resizeEvent(self, re):
    self._close_widget.move(self.width() - self._close_widget.width() - self._margin, self._margin)
    
class AnimatedClosableMessage(ClosableMessage):
  
  def __init__(self, closeWidget, messageString='',
               opacity=0.60, parent=None):
    super(AnimatedClosableMessage, self).__init__(closeWidget, messageString, opacity, parent=parent)
    self._show_hide_anim = QPropertyAnimation(self, "maximumHeight")
    self._show_hide_anim.setDuration(200)
    self._show_hide_anim.setEasingCurve(QEasingCurve.InSine)
    
  def setMessage(self, message):
    self._message_str = message
    if not message:
      self._closeMessage()
      return
    self._show_hide_anim.setStartValue(0)
    self._show_hide_anim.setEndValue(self.HEIGHT)
    self._show_hide_anim.finished.connect(self.repaint)
    self._show_hide_anim.start()
    
  def _closeMessage(self):
    self._show_hide_anim.setStartValue(self.HEIGHT)
    self._show_hide_anim.setEndValue(0)
    self._show_hide_anim.start() 

class ProgressLineEdit(QLineEdit):
  INITIAL_PROGRESS_OPACITY = 0.25
  def __init__(self, parent=None):
    super(ProgressLineEdit, self).__init__(parent)
    self._progress = 0
    self.setProperty("_progress_opacity", self.INITIAL_PROGRESS_OPACITY)
    self._progress_finished_anim = QPropertyAnimation(self, "_progress_opacity")
    self._progress_finished_anim.setStartValue(self.INITIAL_PROGRESS_OPACITY)
    self._progress_finished_anim.setEndValue(0)
    self._progress_finished_anim.setDuration(1000)
    self._progress_finished_anim.valueChanged.connect(self.repaint)
    
  def setProgress(self, progress):
    self._progress = progress
    if progress == 100:
      self._progress_finished_anim.start()
    else:
      self.setProperty("_progress_opacity", self.INITIAL_PROGRESS_OPACITY)
      self.repaint()
  
  def paintEvent(self, pe):
    super(ProgressLineEdit, self).paintEvent(pe)
    painter = QPainter(self)
    painter.setOpacity(self.property("_progress_opacity"))
    sopb = QStyleOptionProgressBarV2()
    sopb.minimum = 0
    sopb.maximum = 100
    sopb.progress = self._progress
    sopb.initFrom(self)
    self.style().drawControl(QStyle.CE_ProgressBarContents, sopb, painter, self)
  
class SingleEditCombobox(QComboBox):
  """Combobox that is editable and inserts items at top"""
  def __init__(self, currentItems=[], parent=None):
    super(SingleEditCombobox, self).__init__(parent)
    self._items = currentItems
    self.setEditable(True)
    self.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
    self.textChanged.connect(self._reinitializeFields)
    
  def _reinitializeFields(self, text):
    """Only one field is allowed to be added per dialog. If user wants to add another,
       erase the previous one he/she added"""
    self._items.pop(0)
    self._items.insert(0, text)
    self.combo_output_field.setModel(QStringListModel(self._items))