'''
Created on Nov 20, 2014
@author: Mohammed Hamdy
'''

class IURLGenerator(object):
  """
  This is the interface that URL generators should implement. 
  URL generators guide spiders to their destinations, and isolates them from
  URL extraction details
  """
  
  def parse_pagination_from_response(self, response):
    """
    parses the response (one of Scrapy's response classes) and gets any
    new pagination links.
    """
    pass
  
  def parse_item_links_from_response(self, response):
    """
    Should be called whenever a response is expected to contain item links
    """
    pass

class ProductCrawlerBaseURLGenerator(IURLGenerator):
  
  def __init__(self, itemPagesSelector, paginationSelector, itemRestrict=None,
               paginationRestrict=None):
    super(ProductCrawlerBaseURLGenerator, self).__init__()
    self.item_pages_selector = itemPagesSelector
    self.pagination_selector = paginationSelector
    self.item_restrict = itemRestrict
    self.pagination_restrict = paginationRestrict
    self.pagination_links = [] # this is a list of link urls, as returned by _links_from_selector
    self.pagination_index = 0
    self.item_links = []
    self.item_link_index = 0
  
class ItemFilterMixin(object):
  """
  Adds page invalidation capability to item extractors. i.e, when a page doesn't
  contain a valid item, it informs the item extractor to reject the item
  """
  
  def __init__(self, predicate):
    """
    The predicate can be a selector or a boolean function.
    For now, it's just a boolean function. It'll be given the page
    source as an argument
    """
    self.predicate = predicate
    
  def page_has_item(self, response):
    return self.predicate(response.body)

class NoMoreLinksException(Exception):
  pass