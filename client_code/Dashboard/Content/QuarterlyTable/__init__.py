from ._anvil_designer import QuarterlyTableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class QuarterlyTable(QuarterlyTableTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.q_table.options = {
      "index": "account_code",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': False,
      'paginationSize': 10,
      'frozenRows': 0,
      #'height': '50vh',
      #'autoResize': False,
      #"pagination_size": 10,
    }

    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def build_table(self):

    def cell_format(cell, **params):
      val = cell.get_value()
      name = cell.get_field()
      if '%' in name:
        perc = int(val * 1000) / 10
        new_val = f"{perc:.1f}%"
      elif 'Delta' in name or 'Q' in name:
        val = val / 1000000
        new_val = f"{val:,.2f}"
      else:
        new_val = val

      bold = 'TOTAL' in cell.get_data()['account_code']  
      new_val = Label(text=new_val, bold=bold)
      return new_val        

    column_labels = set(list(self.data[0].keys())) - set(['account_code'])
    
    def extract(label):
      key1 = label[1]
      key2 = 1 if "FY" in label else 2
      key3 = label[5:] if "FY" in label else label[2:]
      if '%' in label:
        width = 50
      elif 'Delta' in label:
        width = 70
      else:
        width = 80
      return (key1, key2, key3, width, label)
      
    decorated = [ extract(c) for c in list(column_labels) ]
    s = sorted(decorated, key = lambda x: x[2] )
    s = sorted(s, key = lambda x : x[1] )
    s = sorted(s, key = lambda x : x[0] )
    
    columns = [{
      'title': '',
      'field': 'account_code',
      'width': 150,
      'headerSort': False
    }]
    
    for k1,k2,k3,width,c in s:
      
      columns.append({
        'title': c,
        'field': c,
        'formatter': cell_format,
        'hoz_align': 'right',
        'width': width,
        'headerSort': False
      })

    self.q_table.columns = columns
    row_index = { 
      'Software Maintenance': 0, 
      'Hardware Maintenance': 1,
      'Consulting': 2,
      'Communications': 3,
      'Salary': 4
      }
        
    self.data = sorted(self.data, key = lambda x: row_index.get(x['account_code'], 5))
    self.q_table.data = self.data

  def prepare_data(self, d):
    self.data = d
    self.build_table()