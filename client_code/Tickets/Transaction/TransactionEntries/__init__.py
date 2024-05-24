from ._anvil_designer import TransactionEntriesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
#from anvil_extras import augment
from .... import Data

class TransactionEntries(TransactionEntriesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.current_year = Data.CURRENT_YEAR
    self.budget_year = Data.BUDGET_YEAR
    self.months = { 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12, 'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6 }
    
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
  

  
  def build_table(self, item):
    # TODO: We want Forecast value where they exist!
    self.t_data = item.get_all_entries(transaction_type='Budget')
    self.render_table()

    
  def render_table(self):
    self.updated_entries = {}
    
    t = self.entry_table
    t.options.update(
      selectable="highlight",
      pagination=False,
      css_class=["table-striped", "table-bordered", "table-condensed"]
    )

    
    def format_column(cell, foreground_color='blue', background_color=None, **kwargs):
      val = cell.getValue()
      cell.getElement().style.color = foreground_color
      if background_color:
        cell.getElement().style.backgroundColor = background_color
      if str(val).isnumeric():
        return "{:,.0f}".format(float(val))
      else:
        return "<b>{0}</b>".format(val)

    
    def format_month(cell, **kwargs):
        return "<b>{0}</b>".format(cell.getValue())

    def format_total(cell, **kwargs):
      return "<b>{0}</b>".format(cell.getValue())

    t.data = self.t_data['data']
    t.data.append(self.t_data['totals'])

    month_col = [ {"title":x, "field":x, "width":100, "formatter": format_month, 'headerSort': False,  } 
                  for x in self.t_data['columns'][0:1] ]

    fy_columns = []
    for x in self.t_data['columns'][1:]:
      foreground_color = 'black'
      background_color = None
      edit_func = None
      if int(x) == self.current_year:
        background_color = '#ffffcc'
        edit_func = 'number'
      elif int(x) == self.budget_year:
        background_color = '#ccffcc'
        edit_func = 'number'
      else:
        foreground_color = 'grey'
      params = { 'foreground_color': foreground_color, 'background_color': background_color}
      fy_columns.append({"title":x, 
                         "field":x, 
                         "width":100, 
                         "formatter": format_column, 
                         'headerSort': False, 
                         'hozAlign': 'right',
                         'formatterParams': params,
                         'editor': edit_func
                        } )
    
    t.columns = month_col + fy_columns


  def update_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    print("Updated Entries: {0}".format(self.updated_entries))



  def entry_table_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    month = self.months[cell.getData()['Month']]
    fin_year = int(cell.getField())
    year_month = (fin_year - int(month > 6)) * 100 + month
    value = float(cell.getValue())

    if fin_year == self.current_year:
      transaction_type = 'Forecast'
    else:
      transaction_type = 'Budget'
      
    new_entry = {
        'transaction_type': transaction_type,
        'fin_year': fin_year,
        'year_month': year_month,
        'amount': value
    }
    self.updated_entries[year_month] = new_entry

  def revert_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.render_table()
    
