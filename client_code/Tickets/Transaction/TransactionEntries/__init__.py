from ._anvil_designer import TransactionEntriesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .... import Data

class TransactionEntries(TransactionEntriesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.current_year = Data.CURRENT_YEAR
    self.budget_year = Data.BUDGET_YEAR
    
    self.init_components(**properties)
    # Any code you write here will run before the form opens.


  def build_table(self, item):
    self.t_data = item.get_all_entries()

    t = self.entry_table
    t.options.update(
      selectable="highlight",
      pagination=False,
      css_class=["table-striped", "table-bordered", "table-condensed"]
    )

    def format_column(cell, **kwargs):
      val = cell.getValue()
      if str(val).isnumeric():
        return "{:,.0f}".format(val)
      else:
        return "<b>{0}</b>".format(val)
    
    def format_total(cell, **kwargs):
      return "<b>{0}</b>".format(cell.getValue())

    t.data = self.t_data['data']
    t.data.append(self.t_data['totals'])

    month_col = [ {"title":x, "field":x, "width":100, "formatter": format_column, 'headerSort': False,  } 
                  for x in self.t_data['columns'][1:] ]
    
    fy_columns = [ {"title":x, "field":x, "width":100, "formatter": format_column, 'headerSort': False,  } 
                  for x in self.t_data['columns'][1:] ]
    
    t.columns = month_col + fy_columns

  def update_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def entry_table_cell_click(self, cell, **event_args):
    """This method is called when a cell is clicked"""
    pass

  def entry_table_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    pass
