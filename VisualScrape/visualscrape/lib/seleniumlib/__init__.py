from .selenium_crawl import SeleniumCrawler
import logging
# setup selenium logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt="%(asctime)s [Selenium] %(levelname)s : %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log.addHandler(handler)