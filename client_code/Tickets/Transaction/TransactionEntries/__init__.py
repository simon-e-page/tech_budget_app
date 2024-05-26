from ._anvil_designer import TransactionEntriesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime as dt
from .... import Data

class TransactionEntries(TransactionEntriesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.current_year = Data.CURRENT_YEAR
    self.budget_year = Data.BUDGET_YEAR

    self.month_map = enumerate(['Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun'])
    self.updated_entries = []
    
    self.init_components(**properties)
    # Any code you write here will run before the form opens.


  def build_table(self, item):
    self.t_data = item.get_all_entries()
    print(self.t_data['columns'])
    
    t = self.entry_table
    t.options.update(
      selectable="highlight",
      pagination=False,
      css_class=["table-striped", "table-bordered", "table-condensed"]
    )

    def format_column(cell, **params):
      val = cell.getValue()
      if params['backgroundColor']:
        cell.getElement().style.backgroundColor = params['backgroundColor']
      if str(val).isnumeric():
        return "{:,.0f}".format(val)
    
    def format_month(cell, **kwargs):
      return "<b>{0}</b>".format(cell.getValue())

    t.data = self.t_data['data']
    t.data.append(self.t_data['totals'])
    month_col = [ {
                  "title":x, 
                  "field":x,
                  "width":100,
                  "formatter": format_month,
                  'headerSort': False,  } 
                  for x in self.t_data['columns'][0:1] ]

    fy_columns = []
    for x in self.t_data['columns'][1:]:
      if int(x) == Data.CURRENT_YEAR:
        suffix = 'F'
        params = {'backgroundColor': '#ccffcc'}
        editor = 'number'
      elif int(x) == Data.BUDGET_YEAR:
        suffix = 'B'
        params = {'backgroundColor': '#ffffcc'}
        editor = 'number'
      else:
        suffix = ''
        params = {}
        editor = None
        
      fy_column = {
        "title":x + suffix, 
        "field":x, 
        "width":100, 
        "formatter": format_column,
        "formatterParams": params,
        'headerSort': False,  
        "editor": editor
      }
      
      fy_columns.append(fy_column)
    
    t.columns = month_col + fy_columns

  def update_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    print(self.updated_entries)
    self.updated_entries = []


  def entry_table_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    fin_year = int(cell.getField())
    if fin_year == self.current_year:
      transaction_type = 'Forecast'
    else:
      transaction_type = 'Budget'
      
    month_label = cell.getData['Month']
    for i, v in self.month_map:
      if v == month_label:
        month_index = i
        break

    month_num = (month_index + 7) % 12
    timestamp = dt.date(fin_year - int(month_num>6), month_num, 1)
    year_month = fin_year * 100 + month_num
    value = float(cell.getValue())
    self.updated_entries.append({
      'timestamp': timestamp,
      'transaction_type': transaction_type,
      'fin_year': fin_year,
      'year_month': year_month,
      'amount': value
    })

    
