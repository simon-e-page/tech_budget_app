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


class TransactionEntries(TransactionEntriesTemplate):
  def __init__(self, t_data=None, updated_entries=[], **properties):
    # Set Form properties and Data Bindings.
    self.current_year = Data.CURRENT_YEAR
    self.budget_year = Data.BUDGET_YEAR
    self.month_map = {'Jul': 0,'Aug': 1,'Sep': 2,'Oct': 3,'Nov': 4,'Dec': 5,'Jan': 6,'Feb': 7,'Mar': 8,'Apr': 9,'May': 10,'Jun': 11 }
    self.t_data = t_data
    self.updated_entries = updated_entries
    
    self.entry_label = "Budget / Forecast Entries"
    self.transaction = {}

    self.entries_table.options = {
      "index": "transaction_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': True,
      'paginationSize': None,
    } 
    self.init_components(**properties)
    # Any code you write here will run before the form opens.


  def show(self, transaction, transaction_type, title="Add / edit line entries:"):
    save_button = "Save Changes"
    self.build_table(transaction, transaction_type)
    ret = alert(self, title=title, large=True, buttons=((save_button, True), ("Cancel", False)))
    if not ret:
      self.updated_entries = []
      self.t_data = deepcopy(self.t_data_copy)
    return self.t_data, self.updated_entries

  
  def build_table(self, item, transaction_type):
    if self.t_data is None:
      self.t_data = item.get_all_entries(transaction_type)
      
    self.t_data_copy = deepcopy(self.t_data)
    self.transaction = item
    self.entry_label = 'Budget / Forecast Entries' if item.transaction_type == 'Budget' else 'Actual Entries'
    self.refresh_data_bindings()
    if self.entries_table.initialized:
      self.entries_table.clear()
      self.render_table()

  def render_table(self):
    if not self.t_data:
      return
      
    t = self.entries_table
    
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
    data_columns = self.t_data['columns'][1:]
    for x in data_columns:
      if 'Actual' in x:
        params = {'backgroundColor': '##ccffff'}
        editor = 'number'
      elif 'Forecast' in x:
        params = {'backgroundColor': '#ccffcc'}
        editor = 'number'
      elif 'Budget' in x:
        params = {'backgroundColor': '#ffffcc'}
        #Can only edit a Budget if there is no Forecast column
        editor = None if any('Forecast' in c for c in data_columns) else 'number'
      elif 'Snapshot' in x:
        params = {'backgroundColor': '#ffff99'}
        editor = None
      else: # History
        params = {'color': 'grey'}
        editor = None
        
      fy_column = {
        "title":x, 
        "field":x, 
        "width":130, 
        "formatter": format_column,
        "formatterParams": params,
        'headerSort': False,  
        "editor": editor,
        "hozAlign": 'right',
      }
      
      fy_columns.append(fy_column)
    
    t.columns = month_col + fy_columns
    t.add_data(totals)




  def entries_table_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    field = cell.getField()
    fin_year, transaction_type = field.split(' ')
    fin_year = int(fin_year)      
    month_label = cell.getData()['Month']
    month_index = self.month_map[month_label]

    month_num = (month_index + 6) % 12 + 1
    
    timestamp = dt.date(fin_year - int(month_num>6), month_num, 1)
    year_month = (fin_year - int(month_num>6)) * 100 + month_num
    value = cell.get_value()
    try:
      value = float(value)
    except Exception as e:
      value = 0.0

    # Keep an log of changes
    self.updated_entries.append({
      'timestamp': timestamp,
      'transaction_type': transaction_type,
      'fin_year': fin_year,
      'year_month': year_month,
      'amount': value
    })
    
    #Update internal data table
    self.t_data['data'][month_index][field] = value
    self.render_table()
  

  def revert_data(self, **event_args):
    """This method is called when the button is clicked"""
    self.updated_entries = []
    self.t_data = deepcopy(self.t_data_copy)
    self.render_table()


  
  def entries_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    self.render_table()




    
