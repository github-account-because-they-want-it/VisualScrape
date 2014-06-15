'''
This modules defines abstract classes that some UI components should
conform to. They are for documentation only, and not used because
PySide seems to already use metaclasses
Created on Jun 15, 2014
@author: Mohammed Hamdy
'''
import abc

class SearchableTable(object):
  __metaclass__ = abc.ABCMeta
  
  @abc.abstractmethod
  def configure_lineedit(self, lineEdit):
    raise NotImplemented

        
class SearchLineEdit(object):
  """The implementation must specify a single property, which is the search column name
     to query splitter."""
  __metaclass__ = abc.ABCMeta
  
  @abc.abstractproperty
  def column_query_splitter(self):
    raise NotImplemented