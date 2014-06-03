'''
Created on May 29, 2014
@author: Mohammed Hamdy
'''

import unittest
from visualscrape.engine import CrawlEngine
from visualscrape.lib.path import SpiderPath, URL, Form, MainPage
from visualscrape.lib.selector import ItemSelector, FieldSelector

nefsak_laptop_info = ItemSelector([
  FieldSelector("Laptop", ['//h1[@class="pr_title"]/text()'], FieldSelector.XPATH),
  FieldSelector("Nefsak Price", ['//div[@class="pr_page_ofs_comment"]/text()'], FieldSelector.XPATH),
  FieldSelector("SKU", ['//td[@id="product_code"]/text()'], FieldSelector.XPATH),
  FieldSelector("Product Weight", ['//span[@id="product_weight"]/text()'], FieldSelector.XPATH),
  FieldSelector("Processor", ["table.product-properties tr:nth-child(10) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Screen Size", ["table.product-properties tr:nth-child(11) td.property-value::text"], FieldSelector.CSS) ,
  FieldSelector("Graphics Card", ["table.product-properties tr:nth-child(12) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Memory", ["table.product-properties tr:nth-child(13) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Hard Disk", ["table.product-properties tr:nth-child(14) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Optical Drive", ["table.product-properties tr:nth-child(15) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Bluetooth", ["table.product-properties tr:nth-child(16) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Fingerprint", ["table.product-properties tr:nth-child(17) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Wireless", ["table.product-properties tr:nth-child(18) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Camera", ["table.product-properties tr:nth-child(19) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("OS", ["table.product-properties tr:nth-child(20) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Battery", ["table.product-properties tr:nth-child(21) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Weight", ["table.product-properties tr:nth-child(22) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Carrying Case", ["table.product-properties tr:nth-child(23) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Additional Features", ["table.product-properties tr:nth-child(24) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Warranty", ["table.product-properties tr:nth-child(25) td.property-value::text"], FieldSelector.CSS),
  FieldSelector("Screenshot", ["//div[contains(@class,'pr_page_desc')]/img/@src"], FieldSelector.XPATH, FieldSelector.IMAGE_CONTENT)])

class Test(unittest.TestCase):
  
  def test_run(self):
    path = SpiderPath()
    main_page = MainPage(FieldSelector("Laptop Page Selector", [r"//div[@class='pr_list_title']//a/@href"],
                                        FieldSelector.XPATH), nefsak_laptop_info, r"nefsak\.com/15-17-Screen/\?page=\d+",
                         '//div[contains(@class,"navigation_holder")]')
    path.addStep(URL("https://www.nefsak.com/15-17-Screen/")).addStep(main_page)
    #_path.addStep(URL("http://xyasdmldfkhujdfs")).addStep(main_page)
    engine = CrawlEngine()
    engine.add_spider("NefsakLaptopSpider").set_path(path).start()
    """HINT: Sites that has redirects actually calls the callback"""
if __name__ == "__main__":
  unittest.main()