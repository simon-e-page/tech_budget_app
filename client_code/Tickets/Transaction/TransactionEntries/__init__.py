from ._anvil_designer import TransactionEntriesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class TransactionEntries(TransactionEntriesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.entries = {
      2025: { 'Budget': [ 10 ] * 12 }
    }
    self.table_data = { 
      'Jul': [10, 12, 14 ],
      'Aug': [10, 12, 14 ],
      'Sep': [10, 12, 14 ],
      'Oct': [10, 12, 14 ],
      'Nov': [10, 12, 14 ],
      'Dec': [10, 12, 14 ],
      'Jan': [10, 12, 14 ],
      'Feb': [10, 12, 14 ],
      'Mar': [10, 12, 14 ],
      'Apr': [10, 12, 14 ],
      'May': [10, 12, 14 ],
      'Jun': [10, 12, 14 ],
                      }
    
    self.labels = { 'Jul', 'Aug', 'Sep', 'Oct', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun' }
    self.col_names = [ '2023', '2024', '2025']
    self.init_components(**properties)
    # Any code you write here will run before the form opens.

    self.build_table()

  def build_table(self):
    t = self.entry_table
    d = self.table_data
    t.columns = [ {"title":x, "field":x, "width":150 } for x in self.col_names ]
    d['Total'] = [ 
                    sum([ x[i] for x in d.keys() ]) 
                      for i in range(0, len(self.col_names))  
                  ]
    t.data = d
