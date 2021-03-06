'''
Created on May 29, 2014
@author: Mohammed Hamdy
'''

from PySide.QtGui import QApplication, QGraphicsDropShadowEffect
import unittest, sys
from threading import Thread
from visualscrape.engine import CrawlEngine
from visualscrape.lib.path import SpiderPath
from visualscrape.ui.viewer.window import VisualScrapeWindow
from visualscrape.test.test_site_selectors import (nefsak_laptop_info, nefsak_main_page, nefsak_url,
                                                  egyprices_main_page, egyprices_url, cars_url, cars_main_page,
                                                  autotrader_url, autotrader_main_page,
  nefsak_content_main_page)
from visualscrape.test.test_handler import PrintingHandler
#from visualscrape.dbreceiver import MongoReceiver

class Test(unittest.TestCase):
  
  def _test_run(self):
    app = QApplication(sys.argv)
    main = VisualScrapeWindow()
    path = SpiderPath()
    path.add_step(cars_url).add_step(cars_main_page)
    engine = CrawlEngine()
    handler = main.addSpider("Cars.com")
    engine.add_spider("Cars.Com").set_path(path).register_handler(handler).start()
    main.setWindowTitle("VisualScrape")
    main.setGraphicsEffect(QGraphicsDropShadowEffect())
    main.showMaximized()
    sys.exit(app.exec_())
    
  def _test_gui_thread(self):
    # doesn't work. The GUI also loves the main thread
    self._gui_thread = Thread(target=self._test_ui)
    self._gui_thread.start()
    
  def test_ui(self):
    app = QApplication(sys.argv)
    main = VisualScrapeWindow()
    nefsak_handler = main.addSpider("NefsakLaptopSpider")
    #egyprices_handler = main.addSpider("EgypricesLaptopSpider")
    nefsak_path = SpiderPath()
    egyprices_path = SpiderPath()
    nefsak_path.add_step(nefsak_url).add_step(nefsak_main_page)
    egyprices_path.add_step(egyprices_url).add_step(egyprices_main_page)
    engine = CrawlEngine()
    engine.add_spider("NefsakLaptopSpider").set_path(nefsak_path).register_handler(nefsak_handler).start()
           #add_spider("EgypricesLaptopSpider").set_path(egyprices_path).register_handler(egyprices_handler).\
           #start()
    main.spider_stop_requested.connect(engine.stop_spider)
    main.setWindowTitle("VisualScrape")
    main.setGraphicsEffect(QGraphicsDropShadowEffect())
    main.showMaximized()
    sys.exit(app.exec_())
    
  def _test_cars_com(self):
      path = SpiderPath()
      path.add_step(cars_url).add_step(cars_main_page)
      engine = CrawlEngine()
      handler = PrintingHandler()
      engine.add_spider("AutoTraderSpider").set_path(path).register_handler(handler).start()
    
if __name__ == "__main__":
  unittest.main()