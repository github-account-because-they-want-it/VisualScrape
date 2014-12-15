'''
Created on Jun 17, 2014
@author: Mohammed Hamdy
'''
import logging

# setup custom scrapy logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt="%(asctime)s [Scrapy] %(levelname)s : %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log.addHandler(handler)