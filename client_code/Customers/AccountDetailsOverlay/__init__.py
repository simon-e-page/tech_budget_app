from ._anvil_designer import AccountDetailsOverlayTemplate
from anvil import *
#import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class AccountDetailsOverlay(AccountDetailsOverlayTemplate):
  """This Form contains the 'Details' Form, and displays information for a Customer. 
  
  It is added to the 'Overlay' slot on the 'Homepage' Form, 
  which overlays it on top of the Form in the 'default' slot on the Homepage.
  
  Keyword Arguments:
    item: accepts a row from the customers data table as self.item
          passes this to the 'Details' form via data bindings
  """
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    #print("Opening AccountDetailsOverlay")
    #print(self.item)
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.account_details.refresh_data()


  