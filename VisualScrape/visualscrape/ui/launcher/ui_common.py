'''
Created on Jul 20, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QGridLayout, QToolButton, QLabel, QIcon, QApplication, QDrag
from PySide.QtCore import QSize, Qt, QMimeData
from style import *

class SpiderToolButton(QToolButton):
  """A tool button that arranges the spider name and functionality in a grid
     and loads a drag with the spider name"""
  def __init__(self, spiderName, resumable=False,parent=None):
    super(SpiderToolButton, self).__init__(parent)
    self._drag_start = None
    button_play = QToolButton()
    button_play.setIcon(QIcon("play.png"))
    self.triggered.connect(button_play.triggered) # clicking the outer button run the play functionality
    button_play.setIconSize(QSize(32, 32))
    button_resume = QToolButton()
    button_resume.setEnabled(resumable)
    button_resume.setIcon(QIcon("resume.png"))
    button_resume.setIconSize(QSize(32, 32))
    button_pause = QToolButton()
    button_pause.setIcon(QIcon("pause.png"))
    button_pause.setIconSize(QSize(32, 32))
    self.label_spidername = QLabel(spiderName)
    self.label_spidername.setStyleSheet(self.stylesheet_label_spidername)
    layout = QGridLayout()
    layout.addWidget(self.label_spidername, 0, 0)
    layout.addWidget(button_pause, 1,1)
    layout.addWidget(button_resume, 1, 2)
    layout.addWidget(button_play, 1, 3)
    layout.setContentsMargins(10, 8, 10, 8)
    self.setLayout(layout)
    
  def mousePressEvent(self, mpe):
    if mpe.button() == Qt.LeftButton:
      self._drag_start = mpe.pos()
    super(SpiderToolButton, self).mousePressEvent(mpe)
    
  def mouseMoveEvent(self, mme):
    if mme.button() == Qt.NoButton and self._drag_start: # for some reason, the left button is being mapped to NoButton
      drag_distance = mme.pos() - self._drag_start
      drag_distance = drag_distance.manhattanLength()
      if drag_distance > QApplication.startDragDistance():
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.label_spidername.text())
        drag.setMimeData(mime_data)
        drag.exec_(Qt.CopyAction | Qt.MoveAction)
    super(SpiderToolButton, self).mouseMoveEvent(mme)
    
  def enterEvent(self, ee):
    self.label_spidername.setStyleSheet(style_label_spidername_hover)
    super(SpiderToolButton, self).enterEvent(ee)
    
  def leaveEvent(self, le):
    self.label_spidername.setStyleSheet(style_label_spidername_default)
    super(SpiderToolButton, self).leaveEvent(le)