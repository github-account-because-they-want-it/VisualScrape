'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''

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