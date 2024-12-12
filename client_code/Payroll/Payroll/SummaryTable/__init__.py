from ._anvil_designer import SummaryTableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ....Data import PositionsModel, EmployeesModel
from .... import Data


class SummaryTable(SummaryTableTemplate):
  def __init__(self, **properties):
    self.positions = PositionsModel.POSITIONS
    self.employees = EmployeesModel.EMPLOYEES
    self.year = Data.CURRENT_YEAR
    self.brand = Data.CURRENT_BRAND
    
    self.year_months = [ (self.year - (x>6))* 100 + x for x in [ 7,8,9,10,11,12,1,2,3,4,5,6 ]  ]
    
    self.positions_table.options = {
      "index": "position_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': True,
      'paginationSize': 5
    }
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def prepare_summary_table(self):
    columns = [
      {
        'title': 'Team',
        'field': 'team',
        'width': 250,
      },
      
    ]


    salary_cols = [ {
        'title': str(year_month),
        'field': str(year_month),
        'formatter': salary_formatter
      } for year_month in self.year_months ]
    
    columns += salary_cols
    #print(columns)
    
    self.summary_table.columns = columns

    # Any code you write here will run before the form opens.

    