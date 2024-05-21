from ._anvil_designer import LetterGroupTemplate
from anvil import *
#import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class LetterGroup(LetterGroupTemplate):
  """This Form is the ItemTemplate of the RepeatingPanel on the 'Table' Form
  
  It displays a single letter from the alphabet in letter_label via data bindings
  It then sends a list of customers whose name begins with the letter in letter_label to the 'AccountRow' Form.
  
  Keyword Arguments:
    item: accepts a dict in the form {'letter': let, 'accounts':accounts}
          'let' is a list of letters and 'accounts' is a list of customer rows from the accounts data table. 
          'accounts' is a list of accounts passed through from the 'Table' Form. 
           The 'items' property of the accounts_repeating_panel is set to self.item['accounts'] using Data Bindings
  """
  
  def __init__(self, **properties):
     # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.accounts_repeating_panel.set_event_handler('x-select-account', self.select_account)
    self.accounts_repeating_panel.set_event_handler('x-deselect-account', self.deselect_account)
    
  def select_account(self, account, **event_args):
    self.parent.raise_event('x-select-account', account=account)
    
  def deselect_account(self, account, **event_args):
    self.parent.raise_event('x-deselect-account', account=account)