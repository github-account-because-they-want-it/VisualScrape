'''
Created on Jul 5, 2014
@author: Mohammed Hamdy
'''
from visualscrape.lib.path import URL, Form, SpiderPath, FormElemInfo, MainPage
from visualscrape.lib.selector import (KeyValueSelector, ItemSelector, ImageSelector, UrlSelector, FieldSelector,
  ItemPageClickAction, ItemPageScrollUntilAction)
import re
from django.conf import urls


class BrowserWatcher(object):
  """
  Watches a QWebView signals and creates required information from them.
  """
  def __init__(self, browser):
    self._browser = browser
    self._browser.url_changed.connect(self.addUrl)
    self._browser.form_detected.connect(self.addForm)
    self._browser.item_page_visited.connect(self.stopNavTracking)
    self._browser.image_download_changed.connect(self.addImageUrl)
    self._browser.element_scrape_changed.connect(self.addField)
    self._browser.attribute_scrape_changed.connect(self.addAttribute)
    self._browser.item_page_selected.connect(self.addItemPages)
    self._browser.similars_selected.connect(self.addPagnation)
    self._browser.link_clicked.connect(self.addClickAction)
    self._browser.scroll_performed.connect(self.addScrollAction)
    self._spider_path = SpiderPath()
    self._selectors_actions = []
    self._item_pages_selector = None
    self._pagination_selector = None
    self._track_nav = True
    
  def addUrl(self, url):
    if self._track_nav:
      url = url.toString()
      self._spider_path.add_step(URL(url))
    
  def addForm(self, formDict):
    """This form belongs to the previous URL. So the URL should be taken from
       there and used with the form instead. Hopefully, the start url is also emitted."""
    if self._track_nav:
      last_url = self._spider_path.pop_step()
      form_data = []
      for elem_name in formDict:
        elem_value = formDict["value"]
        elem_type = formDict["type"]
        elem_type = elem_type.lower()
        if elem_type == "select":
          elem_type = FormElemInfo.INPUT_SELECT
        elif elem_type == "text":
          elem_type = FormElemInfo.INPUT_TEXT
        form_data.append(FormElemInfo(elem_name, elem_value, elem_type))
      form = Form(last_url, form_data)
      self._spider_path.add_step(form)
  
  def addImageUrl(self, add, selector):
    if add:
      # check if there's already an image selector. Note: all the images are added to the same field. May differ in practice
      for (i, kv_selector) in enumerate(self._selectors_actions):
        if isinstance(kv_selector.value_selector, ImageSelector):
          css_selector = kv_selector.value_selector
          css_selector = self._unionCSS(css_selector, selector) # union the selectors together
          self._selectors_actions.pop(i)
          break
      else:
        css_selector = selector
      self._selectors_actions.append(KeyValueSelector("Images", ImageSelector(selector + "::src", FieldSelector.CSS)))
    else:
      # remove that specific selector from all unioned selectors
      image_kv_selector = self._findSelectorByField("Images", remove=True)
      union = image_kv_selector.value_selector
      css_selector = self._removeSelectorFromUnion(selector, union)
      self._selectors_actions.append(KeyValueSelector("Images", ImageSelector(css_selector, FieldSelector.CSS)))
      
  def addField(self, add, fieldName, selector):
    selector = selector + "::text"
    kv_sel = self._findSelectorByField(fieldName, remove=True)
    if add:
      if kv_sel:
        value_sel = kv_sel.value_selector # assuming it's a regular FieldSelector
        css = self._unionCSS(selector, value_sel)
      else:
        css = selector
      self._selectors_actions.append(KeyValueSelector(fieldName, FieldSelector(css, FieldSelector.CSS)))
    else:
      pass # already removed
    
  def addAttribute(self, add, fieldName, selector, attrName):
    # assuming one-to-one relationship between attributes and fields
    self._findSelectorByField(fieldName, remove=True) # remove the field if it already exists
    if add:
      selector = ''.join([selector, "::", attrName])
      self._selectors_actions.append(KeyValueSelector(fieldName, FieldSelector(selector, FieldSelector.CSS)))
    else: pass # already done
  
  def addItemPages(self, selector):
    selector = selector + "::href"
    self._item_pages_selector = UrlSelector(selector, FieldSelector.CSS, action=UrlSelector.ACTION_VISIT)
    
  def addPagination(self, selector):
    selector = selector + "::href"
    self._pagination_selector = UrlSelector(selector, FieldSelector.CSS, action=UrlSelector.ACTION_VISIT)
    
  def addClickAction(self, selector):
    self._selectors_actions.append(ItemPageClickAction(selector, FieldSelector.CSS))
    
  def addScrollAction(self):
    self._selectors_actions.append(ItemPageScrollUntilAction())
    
  def stopNavTracking(self):
    self._track_nav = False
  
  def _unionCSS(self, selector1, selector2):
    return ', '.join([selector1, selector2]) # union the selectors together
  
  def _removeSelectorFromUnion(self, selector, union, attribute="::text"):
    selector = selector.strip()
    union = union.strip()
    css = re.sub(selector + "(, )?", '', union, re.IGNORECASE)
    return css
  
  def _findSelectorByClass(self, cls, remove=False):
    # cls like ImageSelector, UrlSelector...
    for (i, kv_sel) in enumerate(self._selectors_actions):
      value_selector = kv_sel.value_selector
      if isinstance(value_selector, cls):
        if remove:
          self._selectors_actions.pop(i)
        return kv_sel
  
  def _findSelectorByField(self, fieldName, remove=False):
    for (i, k_v_sel) in enumerate(self._selectors_actions):
      if k_v_sel.key_selector == fieldName:
        if remove:
          self._selectors_actions.pop(i)
        return k_v_sel
      
  def getPath(self):
    main_page = MainPage(self._item_pages_selector, self._selectors_actions, self._pagination_selector)
    self._spider_path.add_step(main_page)
    return self._spider_path