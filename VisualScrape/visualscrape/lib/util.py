'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''
import httplib, urlparse, os, sys, traceback, StringIO
from scrapy import log

class SingletonMeta(type):
  """Used as a metaclass, this singleton works as it should"""
  def __new__(cls, name, bases, dic):
    #just attach the instance property to the class
    cls.__instance = None
    return super(SingletonMeta, cls).__new__(cls, name, bases, dic)
  
  def __call__(cls, *args, **kwargs):
    if not cls.__instance:
      cls.__instance = type.__call__(cls, *args, **kwargs)
    return cls.__instance

def MySingleton(initMethod):
  """This makes a functional signleton, but it fails the equality test"""
  initialized = {}
  inst = {}
  def init_replacement(self, *args, **kwargs):
    if not initialized:
      print "Initializing"
      initMethod(self, *args, **kwargs)
      inst["inst"] = self
      initialized["initialized"] = True
    else: self.__dict__ = inst["inst"].__dict__
  return init_replacement


def download_image(imageUrl, savePath, replace=False):
  """Download an image (or maybe any file) and return it's save location, on success"""
  if not os.path.exists(savePath):
    os.mkdir(savePath)
  parsed_url = urlparse.urlparse(imageUrl)
  try:
    con = httplib.HTTPConnection(parsed_url.netloc)
    con.request("GET", parsed_url.path)
    response = con.getresponse()
    image_data = response.read()
    # determine the image name from the it's url path
    image_name = imageUrl[imageUrl.rfind('/') + 1:]
    save_to = os.path.join(savePath, image_name)
    if os.path.exists(save_to) and not replace: return save_to
    out = open(save_to, "wb")
    out.write(image_data)
    out.close()
    return save_to
  except httplib.HTTPException as he:
    log.err("Error downloading image <%s>" % imageUrl)
  except OSError as oe:
    log.err("Couldn't save %s :Access denied" % save_to)
  
def get_exception_str():
  exc_str = StringIO.StringIO()
  tb = sys.exc_info()[2]
  for (filename, lineno, f, code) in traceback.extract_tb(tb):
      exc_str.write("\tLine:%d in %s.%s < %s >\n" % (lineno, filename, f, code))
  return exc_str.getvalue()

if __name__ == "__main__":
  class T:
    __metaclass__ = SingletonMeta
    
    def __init__(self, name, age=25):
      self.name = name
      self.age = age
      
    def do_stuff(self):
      print "Doing Stuff with %s" % self.name
      
  o = T("Mohammed", 25)
  o2 = T("Ebrahim", 18)
  o.do_stuff()
  o2.do_stuff()
  print o == o2
  print o is o2