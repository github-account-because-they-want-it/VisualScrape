'''
Created on Jun 16, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QWidget, QGridLayout
from visualscrape.ui.table import ScrapeDataTable
from visualscrape.ui.support import ScrapeSearchLineEdit

class SearchWindow(QWidget):
  """A window with a data table and a search box"""
  def __init__(self, parent=None):
    super(SearchWindow, self).__init__(parent)
    layout = QGridLayout()
    self._scrape_table = ScrapeDataTable()
    lineedit_search = ScrapeSearchLineEdit()
    self._scrape_table.configure_lineedit(lineedit_search)
    row = 0; col = 0;
    row += 1; col += 2;
    layout.addWidget(lineedit_search, row, col, 1, 2)
    row += 2; col = 0;
    layout.addWidget(self._scrape_table, row, col, 1, 4)
    self.setLayout(layout)

"""
I need a plan. The main UI will contain as much tabs as there are spiders.
I don't think it does have to know how many spiders it'll run in advance.
That can be done at runtime. Though not as elegant. If the internet is slow,
it'll cause a delay to construct the full UI, which can confuse a user
What is the current event handler doing?. It takes callables as queue receivers.
And it'll only have 2 queues, even for a million spider!. So the spiders
have to filter out for themselves. I think this can be made less messy and more
perfect at the event handler.
If the event handler can act as a router for the data packets. It doesn't need to
associate any data with a specific pipe. It only has to remember to send 
all items with the same id to the same pipe.
Or probably better and simpler, the engine should create an event handler for each
spider!. and skip all the routing bullshit
It seems the engine needs to be modified too. But how?.
Since the engine have access to the spider class, it could use it to create an event handler
for the spider, and then we skip the fishy set_spider call.
It's freaking shit. the pipeline now needs the spider instance, to pass
it to the pipelines.
"""