from ._anvil_designer import PositionsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ....Data import PositionsModel

class Positions(PositionsTemplate):
  def __init__(self, **properties):
    self.positions = PositionsModel.POSITIONS
    
    self.tracking_table.options = {
      "index": "position_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': False,
      'paginationSize': 250,
      'frozenRows': 0,
      'height': '50vh',
      #'autoResize': False,
      #"pagination_size": 10,
    }

    self.get_data()
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
  def get_data(self):
    self.data = self.positions.all()

  def positions_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    columns = [
      {
        'title': 'Title',
        'field': 'title',
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        'title': 'Team',
        'field': 'team',
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        'title': 'Type',
        'field': 'role_type',
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        'title': 'Reason',
        'field': 'reaosn',
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      
    ]

    self.positions_table.columns = columns
    self.positions_table.data = self.data
