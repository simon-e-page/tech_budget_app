from ._anvil_designer import TransactionEntriesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime as dt
from copy import deepcopy
from .... import Data

from tabulator.Tabulator import Tabulator
#Tabulator.modules.add('ColumnCalcsModule')
#Tabulator.modules.add('calculations')
#Tabulator.modules.add('columnCalcs')


class TransactionEntries(TransactionEntriesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.current_year = Data.CURRENT_YEAR
    self.budget_year = Data.BUDGET_YEAR
    self.month_map = {'Jul': 0,'Aug': 1,'Sep': 2,'Oct': 3,'Nov': 4,'Dec': 5,'Jan': 6,'Feb': 7,'Mar': 8,'Apr': 9,'May': 10,'Jun': 11 }
    self.updated_entries = []
    self.entry_label = "Budget / Forecast Entries"
    self.transaction = {}
    
    self.init_components(**properties)
    # Any code you write here will run before the form opens.


  def build_table(self, item):
    print(item.transaction_id)
    if item.transaction_id:
      self.t_data = item.get_all_entries()
    else:
      self.t_data = None
      
    self.t_data_copy = deepcopy(self.t_data)
    self.transaction = item
    self.entry_label = 'Budget / Forecast Entries' if item.transaction_type == 'Budget' else 'Actual Entries'
    self.refresh_data_bindings()
    #if self.entry_table.initialized:
    if self.entries.initialized:
      #self.entry_table.clear()
      self.entries.clear()
      self.render_table()

  def render_table(self):
    if not self.t_data:
      return
    #t = self.entry_table
    t = self.entries
    t.options.update(
      selectable="highlight",
      pagination=False,
      pagination_size=15,
      css_class=["table-striped", "table-bordered", "table-condensed"]
    )
    
    def calc_totals(data):
      totals = { k: sum([ r[k] for r in data if r[k] != 'NA']) for k in data[0].keys() if k != 'Month' }
      totals['Month'] = 'Total'
      return totals

    def format_column(cell, **params):
      val = cell.getValue()
      if params.get('backgroundColor', None):
        cell.getElement().style.backgroundColor = params['backgroundColor']
      if params.get('color', None):
        cell.getElement().style.color = params['color']
      if str(val).isnumeric():
        val = "{:,.0f}".format(val)
      if cell.getData()['Month'] == 'Total':
        val = "<b>{0}</b>".format(val)
      return val
      
    
    def format_month(cell, **kwargs):
      return "<b>{0}</b>".format(cell.getValue())
           
    totals = calc_totals(self.t_data['data'])
    t.data = self.t_data['data']
    month_col = [ {
                  "title":x, 
                  "field":x,
                  "width":100,
                  "formatter": format_month,
                  'headerSort': False,  } 
                  for x in self.t_data['columns'][0:1] ]

    fy_columns = []
    for x in self.t_data['columns'][1:]:
      if 'Actual' in x:
        params = {'backgroundColor': '##ccffff'}
        editor = 'number' if self.transaction.transaction_id is not None else None
      elif 'Forecast' in x and int(x) == Data.CURRENT_YEAR:
        suffix = '\nForecast'
        params = {'backgroundColor': '#ccffcc'}
        editor = 'number' if self.transaction.transaction_id is not None else None        
      elif self.transaction.transaction_type == 'Budget' and int(x) == Data.BUDGET_YEAR:
        suffix = '\nBudget'
        params = {'backgroundColor': '#ffffcc'}
        editor = 'number' if self.transaction.transaction_id is not None else None
      elif self.transaction.transaction_type.startswith('Snapshot') and int(x) == Data.BUDGET_YEAR:
        suffix = f'\n{self.transaction.transaction_type}'
        params = {'backgroundColor': '#ffff99'}
        editor = 'number' if self.transaction.transaction_id is not None else None
      else:
        suffix = ''
        params = {'color': 'grey'}
        editor = None
        
      fy_column = {
        "title":x + suffix, 
        "field":x, 
        "width":100, 
        "formatter": format_column,
        "formatterParams": params,
        'headerSort': False,  
        "editor": editor,
        "hozAlign": 'right',
        #"bottomCalc": 'sum'
      }
      
      fy_columns.append(fy_column)
    
    t.columns = month_col + fy_columns
    t.add_data(totals)


  def update_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    print(self.updated_entries)
    self.transaction.add_entries(self.updated_entries)
    self.updated_entries = []
    self.build_table(self.transaction)


  def entries_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    fin_year = int(cell.getField())
    if self.transaction['transaction_type'] == 'Actual':
      transaction_type = 'Actual'
    elif fin_year == self.current_year:
      transaction_type = 'Forecast'
    else:
      transaction_type = 'Budget'
      
    month_label = cell.getData()['Month']
    month_index = self.month_map[month_label]

    month_num = (month_index + 7) % 12
    timestamp = dt.date(fin_year - int(month_num>6), month_num, 1)
    year_month = (fin_year - int(month_num>6)) * 100 + month_num
    value = float(cell.getValue())

    # Keep an log of changes
    self.updated_entries.append({
      'timestamp': timestamp,
      'transaction_type': transaction_type,
      'fin_year': fin_year,
      'year_month': year_month,
      'amount': value
    })
    
    #Update internal data table
    self.t_data['data'][month_index][str(fin_year)] = value
    self.render_table()
  

  def revert_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.updated_entries = []
    self.t_data = deepcopy(self.t_data_copy)
    self.render_table()

  def entries_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    self.render_table()




    
