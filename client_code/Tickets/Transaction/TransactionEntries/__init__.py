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

class TransactionEntries(TransactionEntriesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.current_year = Data.CURRENT_YEAR
    self.budget_year = Data.BUDGET_YEAR

    self.month_map = {'Jul': 0,'Aug': 1,'Sep': 2,'Oct': 3,'Nov': 4,'Dec': 5,'Jan': 6,'Feb': 7,'Mar': 8,'Apr': 9,'May': 10,'Jun': 11 }
    self.updated_entries = []
    
    self.init_components(**properties)
    # Any code you write here will run before the form opens.

  def calc_totals(self, data):
    totals = {'Month': 'Total'}
    for r in data:
      for i,v in r.items():
        if i != 'Month':
            totals[i] = v if i not in totals else totals[i] + v

  def build_table(self, item):
    self.t_data = item.get_all_entries()
    self.t_data_copy = deepcopy(self.t_data)
    self.transaction = item
    if self.entry_table.initialized:
      self.entry_table.clear()
      self.render_table()

  def render_table(self):
    t = self.entry_table
    t.options.update(
      selectable="highlight",
      pagination=False,
      css_class=["table-striped", "table-bordered", "table-condensed"]
    )

    def format_column(cell, **params):
      val = cell.getValue()
      if params.get('backgroundColor', None):
        cell.getElement().style.backgroundColor = params['backgroundColor']
      if params.get('color', None):
        cell.getElement().style.color = params['color']
      if str(val).isnumeric():
        return "{:,.0f}".format(val)
    
    def format_month(cell, **kwargs):
      return "<b>{0}</b>".format(cell.getValue())


      return totals
           
    totals = self.calc_totals(self.t_data['data'])
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
      if self.transaction['transaction_type'] == 'Actual' and int(x) == Data.CURRENT_YEAR:
        suffix = 'A'
        params = {'backgroundColor': '##ccffff'}
        editor = 'number'
      elif int(x) == Data.CURRENT_YEAR:
        suffix = 'F'
        params = {'backgroundColor': '#ccffcc'}
        editor = 'number'        
      elif int(x) == Data.BUDGET_YEAR:
        suffix = 'B'
        params = {'backgroundColor': '#ffffcc'}
        editor = 'number'
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
        "editor": editor
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


  def entry_table_cell_edited(self, cell, **event_args):
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
    self.t_data[month_index][str(fin_year)] = value
    totals = self.calc_totals(self.t_data['data'])
    self.entry_table.delete_row(len(self.t_data['data'])-1)
    self.entry_table.add_data(totals)
  

  def revert_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.updated_entries = []
    self.t_data = deepcopy(self.t_data_copy)
    self.render_table()

  def entry_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    self.render_table()


    
