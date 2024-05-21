from ._anvil_designer import AccountSearchRowTemplate
from anvil import *
import anvil.server
#import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class AccountSearchRow(AccountSearchRowTemplate):
  """This Form is the ItemTemplate of the RepeatingPanel on the 'Customer' Form.
  
  Keyword Arguments:
    item: a row from the 'Customers' data table
  """
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def link_search_result_click(self, **event_args):
    # Raise an event on the parent container when the link is clicked
    # Set the text of the result box when the link is clicked
    self.parent.raise_event('x-result-selected', result=self.item)