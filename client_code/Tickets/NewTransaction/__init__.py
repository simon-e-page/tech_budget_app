from ._anvil_designer import NewTransactionTemplate
from anvil import *
#import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server


class NewTransaction(NewTransactionTemplate):
  """This Form loads the 'Account' and 'Details' Forms that are used to create a new transaction. 
  
  Keyword Arguments:
    initial_account (optional): a row from the 'Accounts' Data Table
  If initialised with an 'initial_account' argument, 
  it passes the account row to the 'Details' Form as self.account using Data Bindings
  """
  
  def __init__(self, initial_account=None, **properties):
    self.account = initial_account
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    
