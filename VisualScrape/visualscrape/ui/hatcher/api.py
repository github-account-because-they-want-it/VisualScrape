'''
Created on Jul 5, 2014
@author: Mohammed Hamdy
'''
from visualscrape.lib.path import URL, Form, SpiderPath, FormElemInfo, MainPage
from visualscrape.lib.selector import KeyValueSelector, ItemSelector, ImageSelector, UrlSelector, FieldSelector
import re

"""
item_page_selected = Signal(str)
similars_selected = Signal(str)
progress_changed = Signal(int) # emitted whenever the progress changes
url_changed = Signal(QUrl)
form_detected = Signal(dict)
image_download_changed = Signal(bool, str) # emit the image selector
element_scrape_changed = Signal(bool, str, str) # enabled, fieldname, selector
# for non-image elements. enabled, fieldname, selector, attribute name (can be empty when deleting selectors)
attribute_scrape_changed = Signal(bool, str, str, str)
"""
class BrowserWatcher(object):
  """
  Watches a QWebView signals and creates required information from them.
  """
  def __init__(self, browser):
    self._browser = browser
    self._browser.url_changed.connect(self.addUrl)
    self._browser.form_detected.connect(self.addForm)
    self._browser.image_download_changed.connect(self.addImageUrl)
    self._spider_path = SpiderPath()
    self._key_value_selectors = []
    
  def addUrl(self, url):
    url = url.toString()
    self._spider_path.add_step(URL(url))
    
  def addForm(self, formDict):
    """This form belongs to the previous URL. So the URL should be taken from
       there and used with the form instead. Hopefully, the start url is also emitted."""
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
      for (i, kv_selector) in enumerate(self._key_value_selectors):
        if isinstance(kv_selector.value_selector, ImageSelector):
          css_selector = kv_selector.value_selector
          css_selector = self._unionCSS(css_selector, selector) # union the selectors together
          self._key_value_selectors.pop(i)
          break
      else:
        css_selector = selector
      self._key_value_selectors.append(KeyValueSelector("Images", ImageSelector(selector + "::src", FieldSelector.CSS)))
    else:
      # remove that specific selector from all unioned selectors
      image_kv_selector = self._findSelectorByField("Images", remove=True)
      union = image_kv_selector.value_selector
      css_selector = self._removeSelectorFromUnion(selector, union)
      self._key_value_selectors.append(KeyValueSelector("Images", ImageSelector(css_selector, FieldSelector.CSS)))
  
  def _unionCSS(self, selector1, selector2):
    return ', '.join([selector1, selector2]) # union the selectors together
  
  def _removeSelectorFromUnion(self, selector, union):
    selector = selector.strip()
    union = union.strip()
    css = re.sub(selector + "(, )?", '', union, re.IGNORECASE)
    return css
  
  def _findSelectorByClass(self, cls, remove=False):
    # cls like ImageSelector, UrlSelector...
    for (i, kv_sel) in enumerate(self._key_value_selectors):
      value_selector = kv_sel.value_selector
      if isinstance(value_selector, cls):
        if remove:
          self._key_value_selectors.pop(i)
        return kv_sel
  
  def _findSelectorByField(self, fieldName, remove=False):
    for (i, k_v_sel) in enumerate(self._key_value_selectors):
      if k_v_sel.key_selector == fieldName:
        if remove:
          self._key_value_selectors.pop(i)
        return k_v_sel
      
  def getPath(self):
    return self._spider_path