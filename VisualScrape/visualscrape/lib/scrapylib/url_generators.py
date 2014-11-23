'''
Created on Nov 20, 2014
@author: Mohammed Hamdy
'''
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from visualscrape.lib.path import URL
from visualscrape.lib.selector import FieldSelector
from visualscrape.lib.commonspider.url_generator import ProductCrawlerBaseURLGenerator, NoMoreLinksException

class ProductCrawlerURLGenerator(ProductCrawlerBaseURLGenerator):
  """
  A general generator suitable for product seller sites, where there's some item 
    links on the main page and some pagination links at the bottom or some other place
  """
    
  def parse_pagination_from_response(self, response):
    new_pagination_links = self._links_from_selector(response, 
                            self.pagination_selector, self.pagination_restrict)
    self.pagination_links.extend(new_pagination_links)
    return new_pagination_links
    
  def get_pagination_link(self):
    if self.pagination_index == len(self.pagination_links):
      raise NoMoreLinksException()
    link = self.pagination_links[self.pagination_index]
    self.pagination_index += 1
    return link
  
  def parse_item_links_from_response(self, response):
    new_item_links = self._links_from_selector(response, 
                       self.item_pages_selector, self.item_restrict)
    self.item_links.extend(new_item_links)
    return new_item_links
    
  def get_item_link(self):
    if self.item_link_index == len(self.item_links):
      raise NoMoreLinksException()
    new_link = self.item_links[self.item_link_index]
    self.item_link_index += 1
    return new_link
  
  def _links_from_selector(self, response, selector, restrict=None):
    if selector.type == FieldSelector.REGEX:
      # use rules to do manual link extraction, since scrapy seems not to do it unless the rules are a class attribute
      similar_extractor = SgmlLinkExtractor(allow=(selector,),
                         restrict_xpaths=(restrict,) if restrict else ())
      links = [link.url for link in similar_extractor.extract_links(response)]
    else:
      sel = Selector(response)
      if selector.type == FieldSelector.CSS:
        if not "::href" in selector: selector = selector + "::attr(href)"
        links = sel.css(selector).extract()
      elif selector.type == FieldSelector.XPATH:
        if not "@href" in selector: selector = selector + "/@href"
        links = sel.xpath(selector).extract()
      # canonicalize ...
      links = [URL(link).canonicalize(response.url) for link in links]
    return links

