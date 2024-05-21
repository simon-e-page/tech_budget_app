from ._anvil_designer import AccountTransactionRowTemplate
from anvil import *
import anvil.server
#import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables

class AccountTransactionRow(AccountTransactionRowTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def description_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    # Navigate to the 'Transactions' Form if the transactions description is clicked
    self.parent.raise_event('x-transaction-detail', transaction_id=self.item['transaction_id'])

