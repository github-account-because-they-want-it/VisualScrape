'''
Created on Nov 26, 2014
@author: Mohammed Hamdy
'''

import random, time
from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware
from scrapy import log
from visualscrape import settings
from visualscrape.tor import TorManager

class RandomUserAgentMiddleware(object):
  
  def process_request(self, request, spider):
    ua  = random.choice(settings.get('USER_AGENT_LIST'))
    if ua:
      request.headers.setdefault('User-Agent', ua)

class ProxyMiddleware(object):
  
  def process_request(self, request, spider):
    request.meta['proxy'] = settings.get('HTTP_PROXY')

class RetryChangeProxyMiddleware(RetryMiddleware):
  def _retry(self, request, reason, spider):
    log.msg('Changing proxy')
    TorManager.get_instance().refresh_circuit()
    time.sleep(3)
    log.msg('Proxy changed')
    return RetryMiddleware._retry(self, request, reason, spider)
  