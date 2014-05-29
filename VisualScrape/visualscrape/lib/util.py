'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''

def Singleton(cls):
  inst = None
  def init(*args, **kwargs):
    if not inst:
      inst = cls(*args, **kwargs)
    return inst
  return init
      
