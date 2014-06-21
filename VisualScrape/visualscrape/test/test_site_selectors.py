'''
Created on Jun 21, 2014
@author: Mohammed Hamdy
'''
from visualscrape.lib.path import URL, MainPage
from visualscrape.lib.selector import (ItemSelector, FieldSelector, KeyValueSelector, ImageSelector, 
                                       UrlSelector, PostProcessing, Merge)

#www.machinetrader.com
machinery_selector = ItemSelector([
                           KeyValueSelector(FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(2) td.detailstablecellalt b::text", FieldSelector.CSS), #year
                                            FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(2) td.detailstablecell::text", FieldSelector.CSS)),
                           KeyValueSelector(FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(3) td.detailstablecellalt b::text", FieldSelector.CSS), #manufacturer
                                            FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(3) td.detailstablecell::text", FieldSelector.CSS)),
                           KeyValueSelector(FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(4) td.detailstablecellalt b::text", FieldSelector.CSS), #model
                                            FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(4) td.detailstablecell::text", FieldSelector.CSS)),
                           KeyValueSelector(FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(5) td.detailstablecellalt b::text", FieldSelector.CSS), #price
                                            FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(5) td.detailstablecell span#spanSalePrice::text", FieldSelector.CSS)),
                           KeyValueSelector(FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(6) td.detailstablecellalt b::text", FieldSelector.CSS), #location
                                            FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(6) td.detailstablecell::text", FieldSelector.CSS)),
                           KeyValueSelector(FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(8) td.detailstablecellalt b::text", FieldSelector.CSS), #condition
                                            FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(8) td.detailstablecell::text", FieldSelector.CSS)),
                           KeyValueSelector(FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(9) td.detailstablecellalt b::text", FieldSelector.CSS), #Stock no.
                                            FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(9) td.detailstablecell::text", FieldSelector.CSS)),
                           KeyValueSelector(FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(11) td.detailstablecellalt b::text", FieldSelector.CSS), #Drive
                                            FieldSelector("#tblSpecs:nth-child(1) tr:nth-child(11) td.detailstablecell::text", FieldSelector.CSS)),
                           KeyValueSelector("Images", FieldSelector("//img[@id='imgDefault']/@src | //div[starts-with(@onclick,'FillFullSize')]/@onclick", FieldSelector.XPATH))])

machinery_main_page = MainPage(itemPageSelector=UrlSelector("a.feature", FieldSelector.CSS),
                           itemSelector=machinery_selector,
                           similarPagesSelector=UrlSelector("table#ctl00_ContentPlaceHolder1_ctl18_Paging1_tblPaging a", FieldSelector.CSS),
                           similarPagesXpathRestrict=None)

machinery_url = URL("http://www.machinerytrader.com/list/list.aspx?bcatid=4&DidSearch=1&EID=1&LP=MAT&ETID=1&Manu=CASE&mdlx=Contains&PT=10000000&Cond=Used&CTRY=usa&SO=2&btnSearch=Search")

#www.cycletrader.com
cycletrader_selector = ItemSelector([
                            KeyValueSelector("Name", FieldSelector("//h1[@itemprop='name']/text()", FieldSelector.XPATH)), #Model
                            KeyValueSelector("Price", FieldSelector("//span[@itemprop='price']/@text", FieldSelector.XPATH)),
                            KeyValueSelector(FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(1) li:nth-child(1) span.infoLabel::text", FieldSelector.CSS),
                                             FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(1) li:nth-child(1) span:nth-child(2)::text", FieldSelector.CSS)),
                            KeyValueSelector(FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(1) li:nth-child(2) span.infoLabel::text", FieldSelector.CSS),
                                             FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(1) li:nth-child(2) span:nth-child(2)::text", FieldSelector.CSS)),
                            KeyValueSelector(FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(1) li:nth-child(3) span.infoLabel::text", FieldSelector.CSS),
                                             FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(1) li:nth-child(3) span:nth-child(2)::text", FieldSelector.CSS)),
                            KeyValueSelector(FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(1) li:nth-child(4) span.infoLabel::text", FieldSelector.CSS),
                                             FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(1) li:nth-child(4) span:nth-child(2)::text", FieldSelector.CSS)),
                            KeyValueSelector(FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(2) li:nth-child(1) span.infoLabel::text", FieldSelector.CSS), 
                                             FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(2) li:nth-child(1) span:nth-child(2)::text", FieldSelector.CSS)),
                            KeyValueSelector(FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(2) li:nth-child(2) span.infoLabel::text", FieldSelector.CSS), 
                                             FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(2) li:nth-child(2) span:nth-child(2)::text", FieldSelector.CSS)),
                            KeyValueSelector(FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(2) li:nth-child(3) span.infoLabel::text", FieldSelector.CSS), 
                                             FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(2) li:nth-child(3) span:nth-child(2)::text", FieldSelector.CSS)),
                            KeyValueSelector(FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(2) li:nth-child(4) span.infoLabel::text", FieldSelector.CSS), 
                                             FieldSelector("div.featuresList ul.unstyled.lfloat:nth-of-type(2) li:nth-child(4) span:nth-child(2)::text", FieldSelector.CSS)),
                            KeyValueSelector("Images", FieldSelector("//li[@class='photoThumb']/a/img/@id", FieldSelector.XPATH))])

cycletrader_main_page = MainPage(itemPageSelector=UrlSelector("h3.resultTitle a", FieldSelector.CSS),
                                 itemSelector=cycletrader_selector,
                                 similarPagesSelector=UrlSelector("li.pageNumber.hidden-phone a", FieldSelector.CSS),
                                 similarPagesXpathRestrict=None)

cycletrader_url = URL("http://www.cycletrader.com/search-results?schemecode=AD&sort=featured%3Adesc&type=356953&&")

#ebay.com/motors
ebay_url = URL("http://www.ebay.com/sch/Cars-Trucks-/6001/i.html?&_trksid=p2050890.m1603")
ebay_item_selector = ItemSelector([
                         KeyValueSelector("Name", FieldSelector("//h1[@id='itemTitle']/text()", FieldSelector.XPATH)),
                         # strange things happening with firefox and the table selectors
                         KeyValueSelector("Condition", FieldSelector("table#itmSellerDesc tr:nth-child(1) td b:nth-child(1)::text", FieldSelector.CSS)),
                         KeyValueSelector("Price", FieldSelector("span#prcIsum_bidPrice::text", FieldSelector.CSS)),
                         # each 2 kvselectors denote an ebay table row
                         #"""I was trying to differntiate between the tables based on row count. This shit is working"""
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[1]/td[1]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[1]/td[2]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[1]/td[3]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[1]/td[4]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[2]/td[1]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[2]/td[2]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[2]/td[3]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[2]/td[4]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[3]/td[1]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[3]/td[2]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[3]/td[3]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[3]/td[4]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[4]/td[1]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[4]/td[2]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[4]/td[3]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[4]/td[4]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[5]/td[1]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[5]/td[2]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[5]/td[3]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[5]/td[4]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[6]/td[1]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[6]/td[2]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[6]/td[3]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[6]/td[4]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[7]/td[1]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[7]/td[2]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[7]/td[3]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[7]/td[4]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[8]/td[1]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[8]/td[2]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[8]/td[3]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[8]/td[4]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[9]/td[1]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[9]/td[2]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[9]/td[1]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[9]/td[2]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[10]/td[1]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[10]/td[2]//text()", FieldSelector.XPATH)),
                         KeyValueSelector(FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[10]/td[3]//text()", FieldSelector.XPATH),
                                          FieldSelector("//div[@class='itemAttr']//table[count(.//tr) > 2]/tbody/tr[10]/td[4]//text()", FieldSelector.XPATH)),
                         KeyValueSelector("Images", FieldSelector("//img[@id='icImg']/@src"))
                         ])
ebay_main_page = MainPage(itemPageSelector=UrlSelector("a.vip", FieldSelector.CSS),
                          itemSelector=ebay_item_selector,
                          similarPagesSelector=UrlSelector("a.pg", FieldSelector.CSS),
                          similarPagesXpathRestrict=None)

# ebay motos, same selectors different urls
ebay_moto_url = URL("http://www.ebay.com/sch/Motorcycles-/6024/i.html?&_trksid=p2050890.m1603")

#www.cars.com << 31532 zip code used. may need changing >>
cars_url = URL("http://www.cars.com/for-sale/searchresults.action?stkTyp=N&tracktype=newcc&rd=100000&zc=31532&searchSource=TRAIL_HEAD&enableSeo=1")

cars_item_selector = ItemSelector([
                         KeyValueSelector("Name", FieldSelector("span.price::text", FieldSelector.CSS)),
                         KeyValueSelector("Price", FieldSelector("span.price::text", FieldSelector.CSS)),
                         KeyValueSelector(FieldSelector("table.datalist tbody tr:nth-child(1) td strong::text", FieldSelector.CSS),
                                          FieldSelector("table.datalist tbody tr:nth-child(1) td:nth-child(2)::text", FieldSelector.CSS)),
                         KeyValueSelector(FieldSelector("table.datalist tbody tr:nth-child(2) td strong::text", FieldSelector.CSS),
                                          FieldSelector("table.datalist tbody tr:nth-child(2) td:nth-child(2)::text", FieldSelector.CSS)),
                         KeyValueSelector(FieldSelector("table.datalist tbody tr:nth-child(3) td strong::text", FieldSelector.CSS),
                                          FieldSelector("table.datalist tbody tr:nth-child(3) td:nth-child(2)::text", FieldSelector.CSS)),
                         KeyValueSelector(FieldSelector("table.datalist tbody tr:nth-child(4) td strong::text", FieldSelector.CSS),
                                          FieldSelector("table.datalist tbody tr:nth-child(4) td:nth-child(2)::text", FieldSelector.CSS)),
                         KeyValueSelector(FieldSelector("table.datalist tbody tr:nth-child(5) td strong::text", FieldSelector.CSS),
                                          FieldSelector("table.datalist tbody tr:nth-child(5) td:nth-child(2)::text", FieldSelector.CSS)),
                         KeyValueSelector(FieldSelector("table.datalist tbody tr:nth-child(6) td strong::text", FieldSelector.CSS),
                                          FieldSelector("table.datalist tbody tr:nth-child(6) td:nth-child(2)::text", FieldSelector.CSS)),
                         KeyValueSelector(FieldSelector("table.datalist tbody tr:nth-child(7) td strong::text", FieldSelector.CSS),
                                          FieldSelector("table.datalist tbody tr:nth-child(7) td:nth-child(2)::text", FieldSelector.CSS)),
                         KeyValueSelector(FieldSelector("table.datalist tbody tr:nth-child(8) td strong::text", FieldSelector.CSS),
                                          FieldSelector("table.datalist tbody tr:nth-child(8) td:nth-child(2)::text", FieldSelector.CSS)),
                         KeyValueSelector(FieldSelector("table.datalist tbody tr:nth-child(9) td strong::text", FieldSelector.CSS),
                                          FieldSelector("table.datalist tbody tr:nth-child(9) td:nth-child(2)::text", FieldSelector.CSS)),
                         KeyValueSelector("Images", FieldSelector("//div[@class='item']/img/@src | //img[@id='chosenPhotoIMG']/@src", FieldSelector.XPATH))]) # | //img[@class='js-thumbnail' and not contains(@src, 'spacer')]/@src

cars_main_page = MainPage(itemPageSelector=UrlSelector("h4.secondary a", FieldSelector.CSS, UrlSelector.ACTION_CLICK),
                          itemSelector=cars_item_selector,
                          similarPagesSelector=UrlSelector("//a[contains(@name, 'pagination')]", FieldSelector.XPATH))

# autotrader.com
autotrader_url = URL("http://www.autotrader.com/cars-for-sale/searchresults.xhtml?zip=31532&endYear=2015&showcaseOwnerId=100040430&startYear=1981&searchRadius=25&showcaseListingId=368080370&showcaseOwnerId=100040430&captureSearch=true&fromSIP=45A362CD33B5E87BA519EEC2F07E1FD0&showToolbar=true&Log=0")

autotrader_item_selector = ItemSelector([
                               KeyValueSelector("Name", FieldSelector("h1.listing-title::text", FieldSelector.CSS)),
                               KeyValueSelector("Price", FieldSelector("h4.primary-price span::text", FieldSelector.CSS)),
                               KeyValueSelector(FieldSelector("table.vehicle-stats tbody tr:nth-child(1) td.atcui-label::text", FieldSelector.CSS),
                                                FieldSelector("table.vehicle-stats tbody tr:nth-child(1) td:nth-child(2)::text", FieldSelector.CSS)),
                               KeyValueSelector(FieldSelector("table.vehicle-stats tbody tr:nth-child(2) td.atcui-label::text", FieldSelector.CSS),
                                                FieldSelector("table.vehicle-stats tbody tr:nth-child(2) td:nth-child(2)::text", FieldSelector.CSS)),
                               KeyValueSelector(FieldSelector("table.vehicle-stats tbody tr:nth-child(3) td.atcui-label::text", FieldSelector.CSS),
                                                FieldSelector("table.vehicle-stats tbody tr:nth-child(3) td:nth-child(2)::text", FieldSelector.CSS)),
                               KeyValueSelector(FieldSelector("table.vehicle-stats tbody tr:nth-child(4) td.atcui-label::text", FieldSelector.CSS),
                                                FieldSelector("table.vehicle-stats tbody tr:nth-child(4) td:nth-child(2)::text", FieldSelector.CSS)),
                               KeyValueSelector(FieldSelector("table.vehicle-stats tbody tr:nth-child(5) td.atcui-label::text", FieldSelector.CSS),
                                                FieldSelector("table.vehicle-stats tbody tr:nth-child(5) td:nth-child(2)::text", FieldSelector.CSS)),
                               KeyValueSelector(FieldSelector("table.vehicle-stats tbody tr:nth-child(6) td.atcui-label::text", FieldSelector.CSS),
                                                FieldSelector("table.vehicle-stats tbody tr:nth-child(6) td:nth-child(2)::text", FieldSelector.CSS)),
                               KeyValueSelector(FieldSelector("table.vehicle-stats tbody tr:nth-child(7) td.atcui-label::text", FieldSelector.CSS),
                                                FieldSelector("table.vehicle-stats tbody tr:nth-child(7) td:nth-child(2)::text", FieldSelector.CSS)),
                               KeyValueSelector(FieldSelector("table.vehicle-stats tbody tr:nth-child(8) td.atcui-label::text", FieldSelector.CSS),
                                                FieldSelector("table.vehicle-stats tbody tr:nth-child(8) td:nth-child(2)::text", FieldSelector.CSS)),
                               KeyValueSelector(FieldSelector("table.vehicle-stats tbody tr:nth-child(9) td.atcui-label::text", FieldSelector.CSS),
                                                FieldSelector("table.vehicle-stats tbody tr:nth-child(9) td:nth-child(2)::text", FieldSelector.CSS)),
                               KeyValueSelector(FieldSelector("table.vehicle-stats tbody tr:nth-child(10) td.atcui-label::text", FieldSelector.CSS),
                                                FieldSelector("table.vehicle-stats tbody tr:nth-child(10) td:nth-child(2)::text", FieldSelector.CSS)),
                               KeyValueSelector(FieldSelector("table.vehicle-stats tbody tr:nth-child(11) td.atcui-label::text", FieldSelector.CSS),
                                                FieldSelector("table.vehicle-stats tbody tr:nth-child(11) td:nth-child(2)::text", FieldSelector.CSS)),
                               KeyValueSelector(FieldSelector("table.vehicle-stats tbody tr:nth-child(12) td.atcui-label::text", FieldSelector.CSS),
                                                FieldSelector("table.vehicle-stats tbody tr:nth-child(12) td:nth-child(2)::text", FieldSelector.CSS)),
                               KeyValueSelector(FieldSelector("table.vehicle-stats tbody tr:nth-child(13) td.atcui-label::text", FieldSelector.CSS),
                                                FieldSelector("table.vehicle-stats tbody tr:nth-child(13) td:nth-child(2)::text", FieldSelector.CSS)),     
                               KeyValueSelector("Images", FieldSelector("//div[@class='eve-photo']/img/@src | //img[@class='thumbnailImage']/@src", FieldSelector.XPATH))])

autotrader_main_page = MainPage(itemPageSelector=UrlSelector("a.vehicle-title", FieldSelector.CSS),
                                itemSelector=autotrader_item_selector,
                                similarPagesSelector=UrlSelector("a.pagination-button", FieldSelector.CSS, UrlSelector.ACTION_CLICK))
# nefsak.com
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

# egyprices.com
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

