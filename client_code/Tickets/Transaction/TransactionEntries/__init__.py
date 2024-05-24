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
    
    self.entries = {
      2025: { 'Budget': [ 10 ] * 12 }
    }
    self.columns = [ 'Month', '2025', '2024', '2023']
    self.totals = { 'Month': 'Total', '2025': 120, '2024': 144, '2023': 14*12 }
    self.table_data = [ 
      {'Month': 'Jul', '2025': 10000, '2024': 120000, '2023': 1400 },
      {'Month': 'Aug', '2025': 10, '2024': 12, '2023': 14 },
      {'Month': 'Sep', '2025': 10, '2024': 12, '2023': 14 },
      {'Month': 'Oct', '2025': 10, '2024': 12, '2023': 14 },
      {'Month': 'Nov', '2025': 10, '2024': 12, '2023': 14 },
      {'Month': 'Dec', '2025': 10, '2024': 12, '2023': 14 },
      {'Month': 'Jan', '2025': 10, '2024': 12, '2023': 14 },
      {'Month': 'Feb', '2025': 10, '2024': 12, '2023': 14 },
      {'Month': 'Mar', '2025': 10, '2024': 12, '2023': 14 },
      {'Month': 'Apr', '2025': 10, '2024': 12, '2023': 14 },
      {'Month': 'May', '2025': 10, '2024': 12, '2023': 14 },
      {'Month': 'Jun', '2025': 10, '2024': 12, '2023': 14 },
    ]
    
    self.labels = { 'Jul', 'Aug', 'Sep', 'Oct', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun' }
    self.init_components(**properties)
    # Any code you write here will run before the form opens.


  def build_table(self, item):
    self.t_data = item.get_all_entries(transaction_type='Budget')

    t = self.entry_table
    t.options.update(
      selectable="highlight",
      pagination=False,
      css_class=["table-striped", "table-bordered", "table-condensed"]
    )

    def format_row(cell, **kwargs):
      val = cell.getValue()
      if str(val).isnumeric():
        return "{:,.0f}".format(val)
      else:
        return "<b>{0}</b>".format(val)
    
    def format_total(cell, **kwargs):
      return "<b>{0}</b>".format(cell.getValue())

    t.data = self.t_data['data']
    t.data.append(self.t_data['totals'])
    
    t.columns = [ {"title":x, "field":x, "width":100, "formatter": format_row } 
                  for x in self.t_data['columns'] ]

  def update_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def entry_table_cell_click(self, cell, **event_args):
    """This method is called when a cell is clicked"""
    pass

  def entry_table_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    pass
