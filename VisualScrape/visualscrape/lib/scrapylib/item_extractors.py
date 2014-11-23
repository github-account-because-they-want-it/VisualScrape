'''
Created on Nov 21, 2014
@author: Mohammed Hamdy
'''

import re, urlparse
from scrapy.selector import Selector
from visualscrape.lib.selector import (KeyValueSelector, FieldSelector, ContentSelector,
  TableSelector, ImageSelector)
from visualscrape.lib.item import InterestItem, FaviconItem
from visualscrape.lib.commonspider.url_generator import ItemFilterMixin

class ItemExtractor(object):
  """
  Takes ItemSelector object and extracts an item. Taking multiple
  different ItemSelectors can also be considered in the future
  """
  
  def __init__(self, itemSelector, itemLoaderClass, spiderType, spiderName, 
               spiderID, **kwargs):
    self.item_selector = itemSelector
    # item loaders can be customized per spider and have custom i/o processing
    self.item_loader_class = itemLoaderClass
    self.spider_type = spiderType
    self.spider_name = spiderName
    self.spider_id = spiderID
    
  def extract_item(self, response):
      # create an item
      item_info = self._get_item_info(response)
      item = InterestItem(item_info["keys"])
      item_loader = self.item_loader_class(item, response, response_ctx=response)
      return self._fill_item_loader(item_loader, item_info, response, 
                                   self.item_selector.post_process_info)
      
  def extract_favicon_item(self, siteURL):
    url_components = urlparse.urlparse(siteURL)
    favicon_url = urlparse.urljoin(url_components.scheme + "://" + url_components.netloc, "favicon.ico")
    favicon_item = FaviconItem()
    favicon_item["image_urls"] =  [favicon_url]
    favicon_item["_id"] =  self.spider_id
    return favicon_item
  
  def _get_item_info(self, response):
    """Do field key preprocessing if required and return key-selector map"""
    item_info = {"keys":[], "values":[]}
    for selector_action in self.item_selector.selectors_actions:
      if isinstance(selector_action, KeyValueSelector):
        # keys can be either strings or selectors. For the latter, obtain the key from the page
        key_selector = selector_action.key_selector
        if isinstance(key_selector, FieldSelector): #key_selector is a FieldSelector, use it to get the key from the response
          sel = Selector(response)
          if key_selector.type == FieldSelector.XPATH:
            key = sel.xpath(key_selector).extract()
          elif key_selector.type == FieldSelector.CSS:
            key = sel.css(key_selector).extract()
          if key: key = key[0]
          else: key = "Invalid_Key_Selector" #this may pack in all values with invalid keys with this key.
        else: 
          key = key_selector
        value_selector = selector_action.value_selector
      item_info["keys"].append(key)
      item_info["values"].append(value_selector)
    return item_info
  
  def _fill_item_loader(self, itemLoader, itemInfo, response, ppInfo):
    """Fill an item loader with data from itemInfo and response"""
    table_selectors = [] # pack them because their processing differs from the rest
    for (key, value_selector) in zip(itemInfo["keys"], itemInfo["values"]):
      if isinstance(value_selector, ContentSelector):
        restricted = self._selectFrom(value_selector.restrict_selector, value_selector.restrict_selector.type, response)
        if restricted: restrict_selector = restricted[0] # get the first tag that matches the restrict selector
        else: 
          from visualscrape.lib.scrapylib.log import log
          log.warn("Content restrict selector returned empty: %s" % value_selector.restrict_selector)
          continue
        # select all subelements of restricted and check them against the regex
        subs = restrict_selector.xpath("//*")
        if value_selector.selector.type == FieldSelector.WORDLIST:
          words = value_selector.selector.split(", ")
          regexp = re.compile('|'.join(words), re.IGNORECASE)
        elif value_selector.selector.type == FieldSelector.REGEX:
          regexp = re.compile(value_selector.selector, re.IGNORECASE)
        for sub_element in subs:
          subtext = sub_element.css("::text").extract()
          if subtext: subtext = subtext[0] # the text of the parent not the children
          else: continue
          match = regexp.match(subtext)
          if match:
            value = subtext
            break
        else: value = '' # no value found for the selector. empty text
        itemLoader.add_value(key, value)
      elif isinstance(value_selector, TableSelector):
        table_selectors.append(value_selector)
      elif isinstance(value_selector, FieldSelector):
        if value_selector.type == FieldSelector.CSS:
          if isinstance(value_selector, ImageSelector):
            itemLoader.add_css("image_urls", value_selector)
          else:
            itemLoader.add_css(key, value_selector)
        elif value_selector.type == FieldSelector.XPATH:
          if isinstance(value_selector, ImageSelector):
            itemLoader.add_xpath("image_urls", value_selector)
          else:
            itemLoader.add_xpath(key, value_selector)
    for table_selector in table_selectors:
      if table_selector.table_type == TableSelector.TABLE_HHEADERS:
        self._populateItemLoaderFromHTable(itemLoader, response, table_selector)
      elif table_selector.table_type == TableSelector.TABLE_VHEADERS:
        self._populateItemLoaderFromVTable(itemLoader, response, table_selector)
    itemLoader.add_value("_id", self.spider_id)
    # add the post processing information
    itemLoader.add_value("_postinfo", ppInfo)
    itemLoader.add_value("_spidertype", self.spider_type)
    itemLoader.add_value("_spidername", self.spider_name)
    # the response url. intentional because for selenium there's no requests on responses. 
    # This means if there was a redirection on the item url, the redirected-to url is the one saved
    itemLoader.add_value("_scrapedurl", response.url) 
    item = itemLoader.load_item()
    return item
  
  def _selectFrom(self, selector, selectorType, response):
    """Apply the selector to response by selectorType without extraction"""
    sel = Selector(response)
    if selectorType == FieldSelector.CSS:
      elems = sel.css(selector)
    elif selectorType == FieldSelector.XPATH:
      elems = sel.xpath(selector)
    return elems
  
  def _populateItemLoaderFromHTable(self, itemLoader, response, tableSelector):
    table = self._selectFrom(tableSelector, tableSelector.type, response)
    # scrape the the largest even numbers of keys/values
    rows = table.css("tr")
    for row in rows:
      tds = row.css("td")
      if len(tds) == 1: continue # this can be a title data
      for tdi in range(0, len(tds), 2): # this shouldn't execute for td-less rows
        key = self._findTextWithinElement(tds[tdi]) # note that text nodes may not be directly inside td. think <td><bold>...
        key = self._filterKey(key) # only HTables are considered to be liable to have extra characters for me
        if not key:
          continue # skip non-valid keys
        try:
          value = self._findTextWithinElement(tds[tdi + 1])
        except IndexError:
          value = ''
        itemLoader.item.fields[key] = {} # hack the item loader to allow a field not in the original item
        itemLoader.add_value(key, value)
  
  def _populateItemLoaderFromVTable(self, itemLoader, response, tableSelector):
    table = self._selectFrom(tableSelector, tableSelector.type, response)
    # find a row with some th elements and take it as your keys
    # TODO: this needs debugging. There is a problem when there's more that 1 active row span 
    keys = []
    rows = table.css("tr")
    # first get the keys
    for (i, row) in enumerate(rows):
      headers = row.css("th")
      if headers:
        keys = [self._findTextWithinElement(header) for header in headers]
        break
    # search for values after where you found the keys
    data_rows = rows[i+1:]
    active_row_spans = [] # a list of 4-tuples of (rowspan, span_column, span_data, processed_rows)
    values = [] # an array of arrays (rows)
    for (row_i, data_row) in enumerate(data_rows):
      values.append([])
      tds = data_row.css("td")
      for (coli, td) in enumerate(tds):
        row_span = td.xpath("./@rowspan")
        if row_span:
          row_span = int(row_span.extract()[0])
          active_row_spans.append((row_span, coli, self._findTextWithinElement(td), 0))
        # row spans in place. Now check if (any) current td is inside a span
        for (spi, (row_span, span_column, span_data, processed_rows)) in enumerate(active_row_spans):
          if coli == span_column: # i.e, inside an active span
            values[row_i].append(span_data)
            if processed_rows != 0: # do not add the row span twice in the row you found it
              values[row_i].append(self._findTextWithinElement(td))
            processed_rows += 1
            if processed_rows == row_span:
              active_row_spans.pop(spi)
            else:
              active_row_spans[spi] = (row_span, span_column, span_data, processed_rows)
            break
        else: # td not currently in a row span
          values[row_i].append(self._findTextWithinElement(td))
    for (key, value) in zip(keys, values):
      itemLoader.item.fields[key] = {}
      itemLoader.add_value(key, value)
  
  def _findTextWithinElement(self, selector):
    """
    Joins all the texts found within element with the space character
    selector -- scrapy selector object
    """
    parent_text = self._getStrippedText(selector) # everybody has got text I think. so this shouldn't raise IndexError
    if parent_text: return parent_text
    subelements = selector.css('*')
    texts_found = []
    for element in subelements:
      elem_text = self._getStrippedText(element)
      if "CDATA" in elem_text: continue # that's a part of the document not intended to be visible
      texts_found.append(elem_text)
    return ' '.join(texts_found)
  
  def _getStrippedText(self, selector):
    text = selector.css("::text").extract()
    if text:
      text = text[0].strip()
      if text:
        return text
      else:
        return ''
    else:
      return ''
    
  def _filterKey(self, keyText):
    # removes non-character text from the end of key, like (:)
    return re.sub("[^\w]$", '', keyText, flags=re.UNICODE)
  
class FilteringItemExtractor(ItemExtractor, ItemFilterMixin):
  
  def __init__(self, *args, **kwargs):
    super(FilteringItemExtractor, self).__init__(*args, **kwargs)
    self.predicate = kwargs.get("filterPredicate")
    
  def extract_item(self, response):
    if self.predicate is None:
      return ItemExtractor.extract_item(self, response)
    if self.page_has_item(response):
      return ItemExtractor.extract_item(self, response)
    return None