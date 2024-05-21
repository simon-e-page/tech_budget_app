from ._anvil_designer import AccountRowTemplate
from anvil import *
#import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .....Account import Account
from .....AccountDetailsOverlay import AccountDetailsOverlay


class AccountRow(AccountRowTemplate):
  """This Form is the ItemTemplate of the RepeatingPanel on the 'LetterGroup' Form
  
  Keyword Arguments:
    item: row from the 'Account' data table. 
          Receieved from the LetterGroup Form
  """
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def check_box_1_change(self, **event_args):
    if self.check_box_1.checked:
      self.parent.raise_event('x-select-account', account=self.item)
      self.role = "customers-repeating-panel-selected"
    else:
      self.parent.raise_event('x-deselect-account', account=self.item)
      self.role = "customers-repeating-panel"

  def account_link_click(self, **event_args):
    homepage = get_open_form()
    homepage.open_account(item=self.item)



