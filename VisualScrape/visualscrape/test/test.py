'''
Created on May 29, 2014
@author: Mohammed Hamdy
'''

from PySide.QtGui import QApplication, QGraphicsDropShadowEffect
import unittest, sys
from threading import Thread
from visualscrape.engine import CrawlEngine
from visualscrape.lib.path import SpiderPath, URL, Form, MainPage
from visualscrape.lib.selector import ItemSelector, FieldSelector, KeyValueSelector, ImageSelector, UrlSelector, PostProcessing, Merge
from visualscrape.test.test_handler import Handler
from visualscrape.ui.viewer.window import VisualScrapeWindow

nefsak_url = URL("http://www.nefsak.com/15-17-Screen/")

nefsak_laptop_info = ItemSelector([
  KeyValueSelector("Laptop", FieldSelector('//h1[@class="pr_title"]/text()', FieldSelector.XPATH)),
  KeyValueSelector("Nefsak Price", FieldSelector('//div[@class="pr_page_ofs_comment"]/text()', FieldSelector.XPATH)),
  KeyValueSelector("SKU", FieldSelector('//td[@id="product_code"]/text()', FieldSelector.XPATH)),
  KeyValueSelector("Product Weight", FieldSelector('//span[@id="product_weight"]/text()', FieldSelector.XPATH)),
  KeyValueSelector("Processor", FieldSelector("table.product-properties tr:nth-child(10) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Screen Size", FieldSelector("table.product-properties tr:nth-child(11) td.property-value::text", FieldSelector.CSS)) ,
  KeyValueSelector("Graphics Card", FieldSelector("table.product-properties tr:nth-child(12) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Memory", FieldSelector("table.product-properties tr:nth-child(13) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Hard Disk", FieldSelector("table.product-properties tr:nth-child(14) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Optical Drive", FieldSelector("table.product-properties tr:nth-child(15) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Bluetooth", FieldSelector("table.product-properties tr:nth-child(16) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Fingerprint", FieldSelector("table.product-properties tr:nth-child(17) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Wireless", FieldSelector("table.product-properties tr:nth-child(18) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Camera", FieldSelector("table.product-properties tr:nth-child(19) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("OS", FieldSelector("table.product-properties tr:nth-child(20) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Battery", FieldSelector("table.product-properties tr:nth-child(21) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Weight", FieldSelector("table.product-properties tr:nth-child(22) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Carrying Case", FieldSelector("table.product-properties tr:nth-child(23) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Additional Features", FieldSelector("table.product-properties tr:nth-child(24) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Warranty", FieldSelector("table.product-properties tr:nth-child(25) td.property-value::text", FieldSelector.CSS)),
  KeyValueSelector("Screenshot", ImageSelector("//div[contains(@class,'pr_page_desc')]/img/@src", FieldSelector.XPATH))])

nefsak_main_page = MainPage(UrlSelector(r"//div[@class='pr_list_title']//a/@href",FieldSelector.XPATH),
                         nefsak_laptop_info,
                         UrlSelector("nefsak\.com/15-17-Screen/\?page=\d+", FieldSelector.REGEX),
                         FieldSelector('//div[contains(@class,"navigation_holder")]', FieldSelector.XPATH))

egyprices_url = URL("http://www.egprices.com/en/category/computers/laptops")
egyprices_laptop_selector = ItemSelector([
                                KeyValueSelector("Laptop Name", FieldSelector("h3.blueFontL::text", FieldSelector.CSS)),
                                KeyValueSelector("PriceValue", FieldSelector("div#pricebox > div:nth-child(2) div span:nth-child(1)::text", FieldSelector.CSS)),
                                KeyValueSelector("PriceCoin", FieldSelector("div#pricebox > div:nth-child(2) div span:nth-child(2)::text", FieldSelector.CSS)),
                                KeyValueSelector("Description", FieldSelector("div#tab2 p:nth-child(1)::text", FieldSelector.CSS)),
                                KeyValueSelector("Stock", FieldSelector("div#pricebox > div:nth-child(2) div div::text", FieldSelector.CSS)),
                                KeyValueSelector("Screenshots", ImageSelector("//a[@class='zoom']/img/@src", FieldSelector.XPATH))
                                ], PostProcessing([Merge(["PriceValue", "PriceCoin"], "Price", '')]))

egyprices_main_page = MainPage(itemPageSelector=UrlSelector("a.divItem", FieldSelector.CSS),
                               itemSelector=egyprices_laptop_selector,
                               similarPagesSelector=UrlSelector("a.paginationLink", FieldSelector.CSS))


class Test(unittest.TestCase):
  
  def _test_run(self):
    path = SpiderPath()
    main_page = MainPage(UrlSelector(r"//div[@class='pr_list_title']//a/@href",FieldSelector.XPATH),
                         nefsak_laptop_info,
                         UrlSelector("nefsak\.com/15-17-Screen/\?page=\d+", FieldSelector.REGEX),
                         FieldSelector('//div[contains(@class,"navigation_holder")]', FieldSelector.XPATH))
    path.add_step(URL("http://www.nefsak.com/15-17-Screen/")).add_step(main_page)
    #_path.add_step(URL("http://xyasdmldfkhujdfs")).add_step(main_page)
    engine = CrawlEngine()
    handler = Handler()
    engine.add_spider("NefsakLaptopSpider").set_path(path).register_handler(handler).start()
    
  def _test_gui_thread(self):
    # doesn't work. The GUI also loves the main thread
    self._gui_thread = Thread(target=self._test_ui)
    self._gui_thread.start()
    
  def test_ui(self):
    app = QApplication(sys.argv)
    main = VisualScrapeWindow()
    nefsak_handler = main.addSpider("NefsakLaptopSpider")
    egyprices_handler = main.addSpider("EgypricesLaptopSpider")
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
    
if __name__ == "__main__":
  unittest.main()