from ._anvil_designer import PositionsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ....Data import PositionsModel
from .... import Data
from ..Position import Position

class Positions(PositionsTemplate):
  def __init__(self, **properties):
    self.positions = PositionsModel.POSITIONS
    self.po_index = self.positions.__d__
    self.year = Data.CURRENT_YEAR
    self.year_months = [ (self.year - (x>6))* 100 + x for x in [ 7,8,9,10,11,12,1,2,3,4,5,6 ]  ]
    
    self.positions_table.options = {
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
    start = self.year_months[0]
    end = self.year_months[-1]  
    self.data = self.positions.get_salaries(start_year_month=start, end_year_month=end, include_positions=True, brand=Data.CURRENT_BRAND)

  
  def positions_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""

    def open_position(sender, **event_args):
      print(f"Got link for {sender.text}")
      cell = sender.tag
      data = cell.get_data()
      position_id = data['position_id']
      #all_ids = self.po_index.keys()
      #print(f"All IDS: {all_ids}")
      position = self.po_index[position_id]
      _form = Position(item=position)
      _form.show()
      
    def title_formatter(cell, **params):
      val = cell.get_value()
      link = Link(text=val, tag=cell)
      link.add_event_handler('click', open_position)
      return link
      
    columns = [
      {
        'title': 'Title',
        'field': 'title',
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        'width': 250,
        'formatter': title_formatter
      },
      {
        'title': 'Line Manager',
        'field': 'line_manager_title',
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        'width': 250
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

    def salary_formatter(cell, **params):
      val = cell.get_value()
      label = Label(text=f"{val:,.0f}")
      return label

    salary_cols = [ {
        'title': str(year_month),
        'field': str(year_month),
        'formatter': salary_formatter
      } for year_month in self.year_months ]
    
    columns += salary_cols
    #print(columns)
    
    self.positions_table.columns = columns
    self.positions_table.data = self.data
