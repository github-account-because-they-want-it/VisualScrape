'''
Created on Jun 14, 2014
@author: Mohammed Hamdy
'''
from __future__ import division
from PySide.QtGui import QWidget, QStackedWidget, QApplication, QLabel, QPixmap
from PySide.QtCore import QPoint, QPropertyAnimation, QParallelAnimationGroup, QRect,\
  QEasingCurve
import sys
    
class SlideshowWidget(QStackedWidget):
  """
  A widget that arranges a few image widgets in a row and responds to
  clicking to switch between images
  """
  def __init__(self, imageList=[], showIndicator=False, parent=None):
    from visualscrape.ui.support import ImageWidget, OverlayContainer
    super(SlideshowWidget, self).__init__(parent)
    self._cur_widget_index = 0
    self._image_widgets = []
    for image in imageList: self._image_widgets.append(ImageWidget(image, fill=True, parent=self))
    # arrange a layout for the overlaid widgets
    self._overlay_container = OverlayContainer()
    self._overlay_container.left_clicked.connect(self.prevImage)
    self._overlay_container.right_clicked.connect(self.nextImage)
    self._overlay_container.hide()
    self.addWidget(self._overlay_container)
    self.setCurrentIndex(1) # or 0 ?
    if showIndicator: # currently shows at the wrong place. disabled
      indicator_label = QLabel()
      indicator_label.setPixmap(QPixmap("show_reel_32.png"))
      self.addWidget(indicator_label)
      indicator_label.move(0, 0)
      self.setCurrentWidget(indicator_label)
    
  def resizeEvent(self, re):
    """Received when the widget is initially shown, and after resizing.
       Use that to scale all internal pixmaps, by resizing them, so they receive
       a paintEvent"""
    self_width = self.width()
    for (i, image_widget) in enumerate(self._image_widgets): 
      image_widget.resize(self.size())
      # now move each image in it's respective position. remember, each image has the size of self
      # i.e, each image fills self
      image_widget.move(self_width * i, 0)
    super(SlideshowWidget, self).resizeEvent(re)  
    
  def enterEvent(self, mme):
    """Show button that when clicked, change the visible widget"""
    self._overlay_container.show()
    return QWidget.enterEvent(self, mme)  
    
  def nextImage(self):
    #when clicking the right arrow
    self_width = self.width()
    if self._cur_widget_index == len(self._image_widgets) - 1:
      # rotate back to the first image
      for (i, image_widget) in enumerate(self._image_widgets):
        image_widget.move(self_width * i, 0)
      self._cur_widget_index = 0
    else:
      for image_widget in self._image_widgets:
        orig_x = image_widget.pos().x()
        image_widget.move(orig_x + - self_width, 0)
      self._cur_widget_index += 1
      
  def prevImage(self):
    # when clicking the left arrow, images move right
    if self._cur_widget_index == 0:
      # bring in the last image
      for _ in range(len(self._image_widgets) - 1):
        self.nextImage()
      self._cur_widget_index = len(self._image_widgets) - 1
    else:
      self_width = self.width()
      for image_widget in self._image_widgets:
        orig_x = image_widget.pos().x()
        image_widget.move(orig_x + self_width, 0)
      self._cur_widget_index -= 1
      
class AnimatedSlideshowWidget(SlideshowWidget):
  """
  Override the click handlers to create an animation
  """
  RIGHT = 0
  LEFT = 1
  ANIM_DURATION = 500
  EASING = QEasingCurve.InOutQuad
  def __init__(self, *args, **kwargs):
    super(AnimatedSlideshowWidget, self).__init__(*args, **kwargs)
    self._anim_grp = None
   
  def nextImage(self):
    self_width = self.width()
    self._anim_grp = QParallelAnimationGroup()
    if self._cur_widget_index == len(self._image_widgets) - 1:
      distance = self_width * (len(self._image_widgets) - 1)
      for image_widget in self._image_widgets:
        self.animateWidget(image_widget, distance, direction=self.RIGHT)
      self._cur_widget_index = 0 
    else:
      for image_widget in self._image_widgets:
        self.animateWidget(image_widget, self_width, direction=self.LEFT)
      self._cur_widget_index += 1
    self._anim_grp.start()
  
  def prevImage(self):
    self_width = self.width()
    self._anim_grp = QParallelAnimationGroup()
    if self._cur_widget_index == 0:
      distance = self_width * (len(self._image_widgets) - 1)
      for image_widget in self._image_widgets:
        self.animateWidget(image_widget, distance, direction=self.LEFT)
      self._cur_widget_index = len(self._image_widgets) - 1
    else:
      for image_widget in self._image_widgets:
        self.animateWidget(image_widget, self_width, direction=self.RIGHT)
      self._cur_widget_index -= 1
    self._anim_grp.start()
    
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

  @staticmethod
  def slideshowCreator(imageList):
    """Return a suitable widget according to the number of images in imageList"""
    from visualscrape.ui.support import ImageWidget
    if not imageList:
      return QWidget()
    elif len(imageList) == 1:
      return ImageWidget(imageList[0])
    else:
      return AnimatedSlideshowWidget(imageList)
  
if __name__ == "__main__":
  app = QApplication(sys.argv)
  main = AnimatedSlideshowWidget([r"D:\Vidz\Movies\Fruitvale Station (2013)\WWW.YIFY-TORRENTS.COM.jpg", r"D:\Pics\other\karla-onredcar750pxIMG_6640.jpg",
                                  r"D:\Pics\Crysis 3\crysis_3___the_hunted_becomes_the_hunter-wallpaper-1366x768.jpg"])
  main.setGeometry(100, 100, 800, 600)
  main.setWindowTitle("Animated Slideshow")
  main.show()
  sys.exit(app.exec_())
