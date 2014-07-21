'''
Created on Jul 20, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QGridLayout, QToolButton, QLabel, QIcon
from PySide.QtCore import QSize
from style import *

class SpiderToolButton(QToolButton):
  """A tool button that arranges the spider name and functionality in a grid"""
  def __init__(self, spiderName, resumable=False,parent=None):
    super(SpiderToolButton, self).__init__(parent)
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
    
  def enterEvent(self, ee):
    self.label_spidername.setStyleSheet(style_label_spidername_hover)
    super(SpiderToolButton, self).enterEvent(ee)
    
  def leaveEvent(self, le):
    self.label_spidername.setStyleSheet(style_label_spidername_default)
    super(SpiderToolButton, self).leaveEvent(le)