'''
Created on Nov 20, 2014
@author: Mohammed Hamdy
'''

from visualscrape.lib.selector import (FieldSelector, UrlSelector)
from visualscrape.lib.scrapylib.url_generators import \
  ProductCrawlerURLGenerator as ScrapyProductURLGenerator

class ProductCrawlerUrlGenerator(ScrapyProductURLGenerator):
  
  def parse_item_links_from_response(self, response, browser=None):
    item_page_selector = self.item_pages_selector
    restrict = self.item_restrict
    action = item_page_selector.action
    if action == UrlSelector.ACTION_VISIT:
      new_links = super(ProductCrawlerUrlGenerator, self).parse_item_links_from_response(response)
    elif action == UrlSelector.ACTION_CLICK:
      new_links = self._get_browser_links(browser, item_page_selector, restrict)
    unique_attr_str = UrlSelector.attrFromUniqueConst(item_page_selector.unique_attr)
    # extract the unique attribute from links and return the links that are not in the start-up links (picked up from a resume)
    if not unique_attr_str:
      uniques = set([link.text for link in new_links])
    else:
      uniques = set([link.get_attribute(unique_attr_str) for link in new_links])
    return uniques
  
  def parse_pagination_from_response(self, response, browser=None):
    similar_pages_selector = self.pagination_selector
    action = similar_pages_selector.action
    restrict = self.pagination_restrict
    if action == UrlSelector.ACTION_VISIT:
      new_links = super(ProductCrawlerUrlGenerator, self).parse_pagination_from_response(response)
    elif action == UrlSelector.ACTION_CLICK:
      new_links = self._get_browser_links(browser, similar_pages_selector, restrict)
    new_links = self._filter_unique_and_save(similar_pages_selector, new_links)
    return new_links
  
  def _get_browser_links(self, browser, selector, restrict):
    if selector.type == FieldSelector.REGEX:
      pass # no regex links for selenium for now
    elif selector.type == FieldSelector.CSS:
      links = browser.find_elements_by_css_selector(selector)
    elif selector.type == FieldSelector.XPATH:
      links = browser.find_elements_by_xpath(selector)
    return links
  
  def _filter_unique_and_save(self, selector, links):
    """Uses the elements unique attribute together with self.pagination_links
       to get new links
       links : must be selenium WebElements"""
    if selector.unique_attr == UrlSelector.UNIQUE_HREF:
        new_links = [link for link in links if link.get_attribute("href") not in self.pagination_links]
        uniq_attrs = [link.get_attribute("href") for link in new_links]
    elif selector.unique_attr == UrlSelector.UNIQUE_TEXT:
      new_links = [link for link in links if link.text not in self.pagination_links]
      uniq_attrs = [link.text for link in new_links]
    elif selector.unique_attr == UrlSelector.UNIQUE_ONCLICK:
      new_links = [link for link in links if link.get_attribute("onCLick") not in self.pagination_links]
      uniq_attrs = [link.get_attribute("onClick") for link in new_links]
    self.pagination_links.extend(uniq_attrs)
    return new_links