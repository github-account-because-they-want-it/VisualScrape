'''
Created on May 26, 2014
@author: Mohammed Hamdy
'''
"""Warning: setting names should not begin with underscores, since these are used internally"""

from visualscrape.lib.types import SpiderTypes

BOT_NAME = 'ScrapyCrawler'

SPIDER_MODULES = ['visualscrape.lib.scrapylib.crawlers']
NEWSPIDER_MODULE = 'NefsakLaptops.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'NefsakLaptops (+http://www.yourdomain.com)'
ITEM_PIPELINES = {"visualscrape.lib.scrapylib.pipeline.ItemPostProcessor": 1,
                  'scrapy.contrib.pipeline.images.ImagesPipeline': 2,
                  "visualscrape.lib.scrapylib.pipeline.CanonicalizeImagePathPipeline": 101,
                  "visualscrape.lib.scrapylib.pipeline.FilterFieldsPipeline": 100,
                  "visualscrape.lib.scrapylib.pipeline.PushToHandlerPipeline": 1000}
                  #"visualscrape.pipeline.CorrectMotoFieldNamesPipeline":102}

IMAGES_STORE = "D:/scraped_images" #relative to the project directory?
CONFIG_PATH = "D:/scraped_images/config" # this is a path used for spider configuration, like current progress
SCRAPER_CLASSES = {"visualscrape.lib.scrapylib.ScrapyCrawler" : SpiderTypes.TYPE_SCRAPY,
                   "visualscrape.lib.seleniumlib.crawlers.SeleniumCrawler" : SpiderTypes.TYPE_SELENIUM}

ITEM_LOADER = "visualscrape.lib.scrapylib.itemloader.DefaultItemLoader"

DOWNLOAD_FAVICON = True

FEED_FORMAT = "json"
FEED_URI = "file:///C:/Users/Tickler/Desktop/example.json"

USER_AGENT = "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0"

SITE_PARAMS = {"http://www.machinerytrader.com/":{"REQUEST_DELAY":3, 
              #The cookies enabled settings applies actually per-start-url, not per-site
                                                  "COOKIES_ENABLED": True,
                                                  # currently, this setting is only supported on selenium, but it might be the default on Scrapy, which seems logical
                                                  "IMAGES_ENABLED" : False, 
                                                  "PREFERRED_SCRAPER": SpiderTypes.TYPE_SELENIUM, # Uses indexes from SCRAPER_CLASSES
                                                  "ITEM_LOADER": "visualscrape.itemloader.CarItemLoader",
                                                  },
               "http://www.cycletrader.com":{"PREFERRED_SCRAPER":SpiderTypes.TYPE_SELENIUM,
                                             "IMAGES_ENABLED" : False,
                                             "REQUEST_DELAY": 1,
                                             "ITEM_LOADER": "visualscrape.itemloader.CarItemLoader"}, # use the car item loader because it overrider takefirst on output
               
               "http://www.ebay.com/":{"PREFERRED_SCRAPER": SpiderTypes.TYPE_SELENIUM,
                                       "IMAGES_ENABLED" : False,
                                       "REQUEST_DELAY": 1,
                                       "ITEM_LOADER": "visualscrape.itemloader.CarItemLoader"},
               
               "http://www.cars.com":{"PREFERRED_SCRAPER":SpiderTypes.TYPE_SELENIUM, # runs quite well with 1
                                      "IMAGES_ENABLED" : True,
                                      "REQUEST_DELAY": 1, 
                                      "ITEM_LOADER": "visualscrape.itemloader.CarItemLoader"},
               
               "http://www.autotrader.com":{"PREFERRED_SCRAPER":SpiderTypes.TYPE_SELENIUM, # requires click pagination
                                            "IMAGES_ENABLED" : True,
                                            "REQUEST_DELAY":1,
                                            "ITEM_LOADER": "visualscrape.itemloader.CarItemLoader"}}