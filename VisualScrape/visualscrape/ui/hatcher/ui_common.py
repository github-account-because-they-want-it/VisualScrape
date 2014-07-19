'''
Created on Jul 6, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QWidget, QPainter, QPixmap, QPen, QColor,\
  QBrush, QFont, QLineEdit, QStyle, QStyleOptionProgressBarV2, QComboBox, QStringListModel,\
  QPainterPath, QMenu, QLinearGradient, QAction, QLabel, QVBoxLayout, QMovie
from PySide.QtCore import Qt, QSize, Signal, QRect, QPropertyAnimation,\
  QEasingCurve, QPoint
from collections import deque
from visualscrape.ui.hatcher.menus import ScrapeTableMenu    

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
  """A lineedit with a progress bar overlaid"""
  INITIAL_PROGRESS_OPACITY = 0.25
  text_changed = Signal(str)
  
  def __init__(self, parent=None):
    super(ProgressLineEdit, self).__init__(parent)
    self._progress = 0
    self.text_changed.connect(self.setText)
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
    

class HideNotifierMenu(QMenu):
  """A menu with a hide signal so that my arrow could flip itself back when the menu is gone"""
  hidden = Signal()
  
  def hideEvent(self, he):
    self.hidden.emit()
    super(HideNotifierMenu, self).hideEvent(he)
    
class ContextualizedChangeOnClickWidget(ChangeIconOnClickWidget): # this name is a programming crime
  
  def __init__(self, icon, clickIcon, resolution, contextMenu, parent=None):
    super(ContextualizedChangeOnClickWidget, self).__init__(icon, clickIcon, resolution, parent)
    self._context_menu = contextMenu
    # restore the icon whenever 
    self._context_menu.hidden.connect(self.restored)

  def mousePressEvent(self, mpe):
    if mpe.button() == Qt.MouseButton.LeftButton:
      self._context_menu.popup(mpe.globalPos())
      super(ContextualizedChangeOnClickWidget, self).mousePressEvent(mpe)
    
class DropDownLabel(QWidget):
  """A widget with an arrow that when clicked shows a context menu"""
  
  def __init__(self, clickIcon1, clickIcon2, text, width, parent=None):
    """Set the width according to the text length"""
    super(DropDownLabel, self).__init__(parent)
    self._text = text
    self._setupContextMenu()
    self._drop_icon = ContextualizedChangeOnClickWidget(clickIcon1, clickIcon2, resolution=(10, 8),
                             contextMenu=self._context_menu, parent=self)
    self.setFixedSize(QSize(width, 20))
    self._setupContextMenu()
    self._painter_path = None
    self._setupPainterPath()
    self._calculateMeasures()
    
  def _setupContextMenu(self):# you may use objects here instead
    """Override this method and create your context menu as self._context_menu"""
    self._context_menu = HideNotifierMenu(self)
    self._action = QAction("Test Action", self._context_menu)
    self._context_menu.addAction(self._action)
   
  def _setupPainterPath(self):
    painter_path = QPainterPath()
    painter_path.moveTo(0, 15) #left
    painter_path.lineTo(0, 0) #up
    painter_path.lineTo(self.width() - 1, 0) # right
    painter_path.lineTo(self.width() - 1, 15) # down
    painter_path.arcTo(QRect(self.width() - 6, 15, 5, 4), 0, -90) # control point1, cp2, destPoint
    painter_path.lineTo(5, 19) # left
    painter_path.arcTo(QRect(1, 15, 5, 4), 270, -90) #arc left up
    painter_path.closeSubpath()
    self._painter_path = painter_path
    
  def _calculateMeasures(self):
    self._hor_margin = 4
    self._ver_margin = (self.height() - self._drop_icon.height()) // 2
    self._drop_icon_pos = QPoint(self.width() - self._drop_icon.width() - self._hor_margin, self._ver_margin)
    self._grad_start = QPoint(self.width() // 2, self.height()) # bottom-up gradient
    self._grad_end = QPoint(self.width() // 2, 0)
    
  def resizeEvent(self, re):
    self._drop_icon.move(self._drop_icon_pos) 
    
  def paintEvent(self, pe):
    painter = QPainter(self)
    painter.save()
    gradient = QLinearGradient()
    gradient.setStart(self._grad_start)
    gradient.setFinalStop(self._grad_end)
    gradient.setColorAt(0, QColor(230, 230, 230))
    gradient.setColorAt(1, QColor(247, 247, 247))
    brush = QBrush(gradient)
    painter.setBrush(brush)
    pen = QPen(Qt.black)
    pen.setWidth(1)
    painter.setPen(pen)
    painter.drawPath(self._painter_path)
    painter.restore()
    font = QFont()
    font.setFamily("Tahoma")
    font.setPixelSize(11)
    font.setBold(True)
    pen = QPen(Qt.darkGray)
    painter.setPen(pen)
    painter.setFont(font)
    self_rect = QRect(self.rect())
    self_rect.moveTo(self._hor_margin, self._ver_margin // 2)
    painter.drawText(self_rect, Qt.AlignLeft, self._text)

class ScrapeTableDropDownLabel(DropDownLabel):
  
  associated_table_scraped = Signal(bool, int) # scraped/unscraped, table _index
  
  def __init__(self, icon1, icon2, text, width, index, parent=None):
    # _index signifies the _index of the table associated with this label in the collection of web tables
    super(ScrapeTableDropDownLabel, self).__init__(icon1, icon2, text, width, parent)
    self._index = index
  
  def _setupContextMenu(self):
    self._context_menu = ScrapeTableMenu(self.parent()) # menus should have their parents up the main window
    self.action_scrape_table = self._context_menu.action_scrape_table
    self.action_scrape_table.toggled.connect(self._emitTableScraped)
    
  def _emitTableScraped(self, yes):
    self.associated_table_scraped.emit(yes, self._index)

class LoadingWidget(QWidget):
  """A widget with a little animation for showing progress.
    Call setMessage to change the secondary message and emit
    the finished signal with an appropriate string to set as the
    primary message when done.
  """
  finished = Signal(str)
  animation_finished = Signal()
  
  def __init__(self, loadIcon="loading_bar", primaryMessage="Please, Wait", message='', parent=None):
    super(LoadingWidget, self).__init__(parent)
    self.finished.connect(self._updateUI)
    self.setStyleSheet("""
      QWidget {
        background-color: #ffffff
      }
    """)
    self._icon_load = loadIcon
    self._primary_message = primaryMessage
    self._label_message = QLabel(message)
    self._label_message.setWordWrap(True)
    self._label_message.setAlignment(Qt.AlignCenter)
    self._label_primary_message = QLabel(self._primary_message)
    self._label_primary_message.setStyleSheet("""
      QLabel {
        font-size: 20px;
        font-weight:bold;
        color: rgb(65,65,65);
      }
    """)
    self._label_primary_message.setAlignment(Qt.AlignCenter)
    self._label_movie = QLabel()
    self._label_movie.setAlignment(Qt.AlignCenter)
    self._movie = QMovie(self._icon_load)
    self._label_movie.setMovie(self._movie)
    self._movie.start()
    layout = QVBoxLayout()
    layout.addWidget(self._label_primary_message)
    layout.addSpacing(5)
    layout.addWidget(self._label_message)
    layout.addSpacing(5)
    layout.addWidget(self._label_movie)
    layout.addStretch()
    #self._setupAnimation() # this should be done after showing everything to get correct geometries
    self.setLayout(layout)
  
  def _setupAnimation(self):
    self._load_animation = QPropertyAnimation(self._label_movie, "geometry")
    # since the opacity is failing, make it run out of the area!
    anim_label_geom = self._label_movie.geometry()
    self._load_animation.setStartValue(anim_label_geom)
    target_anim_geom = QRect(anim_label_geom)
    target_anim_geom.moveTop(self.height())
    # make the animation target a rectangle that's directly under it but shifted downwards outside of parent
    self._load_animation.setEndValue(target_anim_geom)
    self._load_animation.setEasingCurve(QEasingCurve.InBack)
    self._load_animation.setDuration(1000)
    self._load_animation.finished.connect(self.animation_finished)
    self._load_animation.finished.connect(self._hideAnimLabel)
  
  def setMessage(self, message):
    self._label_message.setText(message)
    
  def _updateUI(self, message=''):
    if not message:
      message = "All Done!"
    self._label_primary_message.setText(message)
    self._label_message.setText('')
    self._movie.stop()
    self._setupAnimation()
    self.layout().removeWidget(self._label_movie)
    self._label_movie.setGeometry(self._load_animation.startValue())
    self._load_animation.start()
    
  def _hideAnimLabel(self):
    self._label_movie.hide()
    