from ._anvil_designer import RecentTransactionsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class RecentTransactions(RecentTransactionsTemplate):
  """This Form is the ItemTemplate of the RepeatingPanel on the 'Details' Form.
  
  It handles navigation when the title of a Ticket is clicked.
  """
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def transaction_link_click(self, **event_args):
    homepage = get_open_form()
    homepage.open_transaction(item=self.item)


    
