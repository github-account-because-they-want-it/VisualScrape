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
                  "visualscrape.lib.scrapylib.pipeline.FilterFieldsPipeline": 100}

IMAGES_STORE = "D:/scraped_images" #relative to the project directory?

SCRAPER_CLASSES = {"visualscrape.lib.scrapylib.ScrapyCrawler" : 1,
                   "visualscrape.lib.crawl.SeleniumCrawler" : 2}

ITEM_LOADER = "visualscrape.lib.scrapylib.itemloader.DefaultItemLoader"

DOWNLOAD_FAVICON = True

