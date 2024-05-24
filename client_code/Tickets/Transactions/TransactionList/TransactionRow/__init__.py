from ._anvil_designer import TransactionRowTemplate
from anvil import *
#import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server
from datetime import datetime, date
from ..... import Data
from ... import Transactions

class TransactionRow(TransactionRowTemplate):
  """This Form is the ItemTemplate of the 'TransactionList' Form."""
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    #self.accounts = Data.ACCOUNTS_D
    self.init_components(**properties)
    # Any code you write here will run when the form opens.
    
  def transaction_description_link_click(self, **event_args):
    # Navigate to the 'Transactions' Form if the transactions description is clicked
    self.parent.raise_event('x-transaction-detail', transaction_id=self.item['transaction_id'])
    
  def check_box_1_change(self, **event_args):
    if self.check_box_1.checked:
      # Raise event on the parent repeating panel if the transaction is selected
      self.parent.raise_event('x-select-ticket', transaction=self.item)
      self.role = "tickets-repeating-panel-selected"
    else:
      # Raise event on the parent repeating panel if the transaction is de-selected
      self.parent.raise_event('x-deselect-ticket', transaction=self.item)
      self.role = "tickets-repeating-panel"

  def vendor_id_link_click(self, **event_args):
    return
    # Navigate to the 'Customers.Accounts' Form is the name is clicked
    homepage = get_open_form()
    homepage.open_account_transactions(account)

  
  def get_icon(self, icon_id):
    return Data.get_icon(icon_id)  



  


    



