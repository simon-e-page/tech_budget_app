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
      name = cell.get_data()['name']
      if name.contains('Percent'):
        perc = int(val * 1000) / 10
        new_val = f"{perc:.1f}"
      elif name.contains('Delta') or name.contains('Q'):
        new_val = f"{val:.2f}"
      else:
        new_val = val
      return new_val        

    column_labels = list(self.data[0].keys())
    columns = []
    for c in column_labels:
      columns.append({
        'title': c,
        'name': c,
        'formatter': cell_format
      })

    self.q_table.columns = columns
    self.q_table.data = self.data

  def prepare_data(self, d):
    self.data = d
    self.build_table()