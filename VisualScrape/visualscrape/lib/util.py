'''
Created on May 27, 2014
@author: Mohammed Hamdy
'''

class Singleton(object):
  """How to create a singleton by a decorator?"""
  inst = None
  
  def __new__(cls, *args, **kwargs):
    pass