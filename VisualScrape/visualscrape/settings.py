'''
Created on May 26, 2014
@author: Mohammed Hamdy
'''
"""Warning: setting names should not begin with underscores, since these are used internally"""

BOT_NAME = 'ScrapyCrawler'

SPIDER_MODULES = ['visualscrape.lib.scrapylib.scrapy_crawl']
NEWSPIDER_MODULE = 'NefsakLaptops.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'NefsakLaptops (+http://www.yourdomain.com)'
ITEM_PIPELINES = {'scrapy.contrib.pipeline.images.ImagesPipeline': 1,
                  "visualscrape.lib.scrapylib.pipeline.FilterFieldsPipeline": 100,
                  "visualscrape.lib.scrapylib.pipeline.CanonicalizeImagePathPipeline": 101,
                  "carscraper.pipeline.CorrectMotoFieldNamesPipeline":102}

IMAGES_STORE = "D:/scraped_images" #relative to the project directory?

SCRAPER_CLASSES = {"visualscrape.lib.scrapylib.ScrapyCrawler" : 1,
                   "visualscrape.lib.seleniumlib.selenium_crawl.SeleniumCrawler" : 2}

ITEM_LOADER = "visualscrape.lib.scrapylib.itemloader.DefaultItemLoader"

DOWNLOAD_FAVICON = False

FEED_FORMAT = "json"
FEED_URI = "file:///C:/Users/Tickler/Desktop/example.json"

USER_AGENT = "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0"

SITE_PARAMS = {"http://www.machinerytrader.com/":{"REQUEST_DELAY":3, 
              #The cookies enabled settings applies actually per-start-url, not per-site
                                                  "COOKIES_ENABLED": True,
                                                  "PREFERRED_SCRAPER": 2, # Uses indexes from SCRAPER_CLASSES
                                                  "ITEM_LOADER": "carscraper.itemloader.CarItemLoader",
                                                  },
               "http://www.cycletrader.com":{"PREFERRED_SCRAPER":2,
                                             "REQUEST_DELAY": 1,
                                             "ITEM_LOADER": "carscraper.itemloader.CarItemLoader"}, # use the car item loader because it overrider takefirst on output
               
               "http://www.ebay.com/":{"PREFERRED_SCRAPER": 2,
                                       "REQUEST_DELAY": 1,
                                       "ITEM_LOADER": "carscraper.itemloader.CarItemLoader"},
               
               "http://www.cars.com":{"PREFERRED_SCRAPER":1, # runs quite well with 1
                                      "REQUEST_DELAY": 1, 
                                      "ITEM_LOADER": "carscraper.itemloader.CarItemLoader"},
               
               "http://www.autotrader.com":{"PREFERRED_SCRAPER":2, # requires click pagination
                                            "REQUEST_DELAY":1,
                                            "ITEM_LOADER": "carscraper.itemloader.CarItemLoader"}}