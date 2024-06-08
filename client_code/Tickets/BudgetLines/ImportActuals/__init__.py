from ._anvil_designer import ImportActualsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import Data
from ....Data import CURRENT_YEAR 


class ImportActuals(ImportActualsTemplate):
  def __init__(self, **properties):
    self.next_month = Data.get_actuals_updated(CURRENT_YEAR)
    if self.next_month is None or self.next_month == 0:
      self.next_month = (CURRENT_YEAR - 1) * 100 + 7
      
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def get_new_entries(self):
    return [ 'Testing!']

  def file_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    pass
