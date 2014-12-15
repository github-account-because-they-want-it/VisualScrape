'''
Created on Jul 14, 2014
@author: Mohammed Hamdy
'''

from PySide.QtGui import QMainWindow, QWidget, QApplication, QPainter, QHBoxLayout, QPen,\
  QPixmap
from PySide.QtCore import Qt, Signal, QSize, QPoint, QPropertyAnimation,\
  QParallelAnimationGroup, QEasingCurve, QRect, QVariantAnimation,\
  QAbstractAnimation, QObject
from collections import deque

class FlickWindow(QMainWindow):
  
  def __init__(self, windowObject):
    super(FlickWindow, self).__init__()
    self._widgets = windowObject
    self._scroller = AnimatedCentralScroller([o.widget for o in self._widgets])
    self.setCentralWidget(self._scroller)
    self._fake_parent = QWidget()
    self._scroller.window_changed.connect(self._updateFrame)
    self.setMenuBar(self._widgets[0].menubar)
    
  def _updateFrame(self, winIndex):
    self.menuBar().setParent(self._fake_parent)
    self.setMenuBar(self._widgets[winIndex].menubar)

class IconWidget(QWidget):
  """A widget that is clickable, has a fixed size and draws
     an icon which changes opacity on hover. Setting a tooltip is recommended"""
  clicked = Signal()
  def __init__(self, iconPath, hoverOpacity=1, normalOpacity=0.25, parent=None):
    super(IconWidget, self).__init__(parent)
    self.setMouseTracking(True)
    self._icon = QPixmap(iconPath)
    self.setFixedSize(QSize(self._icon.width(), self._icon.height()))
    self._hover_opacity = hoverOpacity
    self._normal_opacity = normalOpacity
    self._mouse_over = False # this is correct because when an icon appears after another, it appears where the mouse is
    self._enabled = True
    
  def paintEvent(self, pe):
    painter = QPainter(self)
    icon = QPixmap(self._icon)
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

class ButtonWidget(IconWidget):
  """A widget the changes it's icon when pressed down"""
  
  def __init__(self, normalIcon, clickIcon, parent=None):
    super(ButtonWidget, self).__init__(normalIcon, parent)
    self._icons = deque([QPixmap(normalIcon), QPixmap(clickIcon)])
    
  def mousePressEvent(self, mpe):
    super(ButtonWidget, self).mousePressEvent(mpe)
    self._icons.rotate()
    self._icon = self._icons[0]
    self.update()
    
  def mouseReleaseEvent(self, mre):
    self._icons.rotate()
    self._icon = self._icons[0]
    self.update()
    
    
class IconFlashAnimation(QVariantAnimation):
  """
  A hide and show animation that nearly works
  """
  def __init__(self, parent=None):
    super(IconFlashAnimation, self).__init__(parent)
    self.setStartValue(0)
    self.setEndValue(100)
    self.setDuration(1500)
    self.setEasingCurve(QEasingCurve.InExpo)
    
  def interpolated(self, frm, to, progress):
    current_value = (to - frm) * progress
    current_value = int(current_value)
    # from __future__ don't import division
    if (current_value / 10) % 2 == 0: # < 10, < 30....
      return True
    else: 
      return False
    
  def updateCurrentValue(self, value):
    pass

class AnimatedClickIconWidget(IconWidget):
  """Animates on clicking and to hide itself and probably also on showing, if possible"""
  def __init__(self, iconPath, iconSize=(32, 32), hoverOpacity=1, normalOpacity=0.25, parent=None):
    super(AnimatedClickIconWidget, self).__init__(iconPath, iconSize, hoverOpacity, normalOpacity, parent)
    self._anim = IconFlashAnimation()
    self._anim.valueChanged.connect(self._hideOrShow)
    self._anim.finished.connect(self._setVisualState)
    
  def mousePressEvent(self, mpe):
    IconWidget.mousePressEvent(self, mpe)
    self.setCursor(Qt.CursorShape.ArrowCursor)
    self._anim.start()
    
  def showEvent(self, se):
    # animate the showing, too. only when the hide/show anim is not running. this will cause an infinite loop
    if self._anim.state() != QAbstractAnimation.Running and self._mouse_over:
      self._anim.start()
    
  def _hideOrShow(self, boool):
    if boool: self.show()
    else: self.hide()
    
  def _setVisualState(self):
    if self._enabled: self.show()
    else: self.hide()
    
class CentralWindowScroller(QWidget):
  """Holds some widgets and animates them into view""" 
  
  window_changed = Signal(int) # the index of the changed-to widget
  
  def __init__(self, widgets, parent=None): 
    super(CentralWindowScroller, self).__init__(parent)
    self._widgets = widgets
    [widget.setParent(self) for widget in widgets]
    self._current_index = 0
    
  def resizeEvent(self, re):
    for (i, widget) in enumerate(self._widgets):
      widget.setFixedSize(self.size()) # probably allow margins between widgets. pad them with cake
      self_width = self.width()
      widget.move(QPoint((i * self_width - self._current_index * self_width), 0)) # assuming a horizontal layout
    
  def next(self):
    if self._current_index + 1 >= len(self._widgets): return
    self._current_index += 1
    for widget in self._widgets:
      widget.move(widget.pos() - QPoint(self.width(), 0))
    self.window_changed.emiy(self._current_index)
    
  def prev(self):
    if self._current_index - 1 < 0: return
    self._current_index -= 1
    for widget in self._widgets:
      widget.move(widget.pos() + QPoint(self.width(), 0))
    self.window_changed.emit(self._current_index)

class DragEnabledCentralScroller(CentralWindowScroller):
  """Adds drag-and-drop capability to CentralWindowScroller"""
  
  def __init__(self, widgets, parent=None):
    super(DragEnabledCentralScroller, self).__init__(widgets, parent)
    self._pos_press_start = None
    
  def mousePressEvent(self, mpe):
    if mpe.button() == Qt.LeftButton:
      self._pos_press_start = mpe.pos()
      self.setCursor(Qt.CursorShape.ClosedHandCursor)
    super(DragEnabledCentralScroller, self).mousePressEvent(mpe)
    
  def mouseReleaseEvent(self, mre):
    if mre.button() == Qt.LeftButton:
      final_pos = mre.pos()
      distance = QPoint(final_pos.x() - self._pos_press_start.x(), final_pos.y() - self._pos_press_start.y())
      distance = distance.manhattanLength()
      if distance > QApplication.startDragDistance():
        # then move the widget. But I really want to know whether the new point is to the right or left to the old point
        if final_pos.x() > self._pos_press_start.x():
          self.prev()
        else:
          self.next()
    self.setCursor(Qt.CursorShape.ArrowCursor)
    super(DragEnabledCentralScroller, self).mouseReleaseEvent(mre)
    
class KeyboardResponsiveCentralScroller(DragEnabledCentralScroller):
  """Adds flick responses to ALT+Left, ALT+Right"""
  def __init__(self, widgets, parent=None):
    super(KeyboardResponsiveCentralScroller, self).__init__(widgets, parent)
    self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
  
  def keyPressEvent(self, kpe):
    if kpe.key() == Qt.Key.Key_Left and kpe.modifiers() == Qt.Modifier.ALT:
      self.next()
    elif kpe.key() == Qt.Key.Key_Right and kpe.modifiers() == Qt.Modifier.ALT:
      self.prev()
      
    super(KeyboardResponsiveCentralScroller, self).keyPressEvent(kpe)

class AnimatedCentralScroller(KeyboardResponsiveCentralScroller):
  RIGHT = 0
  LEFT = 1
  ANIM_DURATION = 500
  EASING = QEasingCurve.InOutQuad
  def __init__(self, widgets, parent=None):
    super(AnimatedCentralScroller, self).__init__(widgets, parent)
    self._anim_grp = None
   
  def next(self):
    self_width = self.width()
    self._anim_grp = QParallelAnimationGroup()
    if self._current_index == len(self._widgets) - 1:
      distance = self_width * (len(self._widgets) - 1)
      for window in self._widgets:
        self.animateWidget(window, distance, direction=self.RIGHT)
      self._current_index = 0 
    else:
      for window in self._widgets:
        self.animateWidget(window, self_width, direction=self.LEFT)
      self._current_index += 1
    self._anim_grp.start()
    self.window_changed.emit(self._current_index)
  
  def prev(self):
    self_width = self.width()
    self._anim_grp = QParallelAnimationGroup()
    if self._current_index == 0:
      distance = self_width * (len(self._widgets) - 1)
      for window in self._widgets:
        self.animateWidget(window, distance, direction=self.LEFT)
      self._current_index = len(self._widgets) - 1
    else:
      for window in self._widgets:
        self.animateWidget(window, self_width, direction=self.RIGHT)
      self._current_index -= 1
    self._anim_grp.start()
    self.window_changed.emit(self._current_index)
    
  def animateWidget(self, widget, distance, direction):
    widget_anim = QPropertyAnimation(widget, "geometry")
    cur_geom = widget.geometry()
    next_geom = QRect(cur_geom)
    if direction == self.LEFT:
      next_geom.moveTo(widget.pos() - QPoint(distance, 0))
    elif direction == self.RIGHT:
      next_geom.moveTo(widget.pos() + QPoint(distance, 0))
    widget_anim.setDuration(self.ANIM_DURATION)
    widget_anim.setEasingCurve(self.EASING)
    widget_anim.setStartValue(cur_geom)
    widget_anim.setEndValue(next_geom)
    self._anim_grp.addAnimation(widget_anim)

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

class ChangeIconOnClickWidget(QWidget):
  """A widget that changes the icon on click and waits for a restore
     event to revert it back"""
     
  restored = Signal()
  
  def __init__(self, icon, clickIcon, resolution=(16, 16), parent=None):
    super(ChangeIconOnClickWidget, self).__init__(parent)
    self._icons = deque([QPixmap(icon), QPixmap(clickIcon)])
    self.setFixedSize(QSize(resolution[0], resolution[1]))
    self.restored.connect(self._restoreIcon)
    
  def mousePressEvent(self, mpe):
    self._icons.rotate()
    self.update()
    
  def paintEvent(self, pe):
    painter = QPainter(self)
    pixmap = self._icons[0]
    pixmap = pixmap.scaled(self.size(), Qt.IgnoreAspectRatio)
    painter.drawPixmap(0, 0, pixmap)
    
  def _restoreIcon(self):
    self._icons.rotate()
    self.update()
    
    
class WindowObject(QObject):
  status_update = Signal(str, int)
  def __init__(self, widget, menuBar=None, toolBar=None, parent=None):
    super(WindowObject, self).__init__(parent)
    self.widget = widget
    self.menubar = menuBar
    self.toolbar = toolBar
