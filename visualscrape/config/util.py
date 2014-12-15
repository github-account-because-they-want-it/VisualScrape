'''
Created on Nov 19, 2014
@author: Mohammed Hamdy
'''

from urlparse import urlparse
from scrapy.utils.project import get_project_settings as get_scrapy_project_settings
from scrapy.utils.misc import load_object
from visualscrape.lib.util import sort_dict_by_values

def get_project_settings():
  # currently, I use scrapy's default project conf
  # module. This can change in the future
  return get_scrapy_project_settings()

settings = get_project_settings()

def get_url_params(url):
  parsed = urlparse(url)
  domain_in = parsed.netloc
  for url_v, params in settings.getdict("SITE_PARAMS").iteritems():
    parsed_v = urlparse(url_v)
    if parsed_v.netloc == domain_in:
      return params
  else: return {}
  
def get_item_loader_for(startUrl):
  """Used by spider managers to get item loaders for spiders, because it can be spider-specific"""
  site_params = get_url_params(startUrl)
  if site_params: 
    loader_cls = site_params.get("ITEM_LOADER", "visualscrape.lib.scrapylib.itemloader.DefaultItemLoader")
    if loader_cls: # specific item loader?
      return load_object(loader_cls)
    
  else: 
    return load_object(settings.get("ITEM_LOADER")) #default item loader
                           
def get_preferred_scraper_for_url(startUrl):
    """Used by the engine to get the user-defined scraper for his site"""
    crawler_params = get_url_params(startUrl)
    scraper_class_name = crawler_params.get("PREFERRED_SCRAPER", 
                                            "visualscrape.lib.scrapylib.crawlers.ScrapyProductCrawler")
    return load_object(scraper_class_name)
    
def get_sorted_pipelines():
  # http://doc.scrapy.org/en/0.24/topics/item-pipeline.html#activating-an-item-pipeline-component
  pipelines = settings.getdict("ITEM_PIPELINES")
  sorted_pipelines = sort_dict_by_values(pipelines)
  return [load_object(pipeline) for pipeline in sorted_pipelines]

def get_url_generator_for(startUrl):
  crawler_params = get_url_params(startUrl)
  return load_object(crawler_params.get("URL_GENERATOR"))

def get_filter_predicate_for(siteUrl):
  crawler_params = get_url_params(siteUrl)
  return load_object(crawler_params.get("FILTER_PREDICATE"))