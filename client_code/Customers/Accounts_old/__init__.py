from ._anvil_designer import Accounts_oldTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import string


class Accounts_old(Accounts_oldTemplate):
  """This Form displays a list of Accounts from the 'customers' Data Table, grouped by letter of the alphabet.
  
  It also displays a list of the letters of the alphabet.
  It fetches a list of accounts from the server, and passes them to the 'Table' Form via Data Bindings.
  """
  
  def __init__(self, **properties):
    self.accounts = anvil.server.call('get_accounts')
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.letters_repeating_panel.set_event_handler('x-scroll-letter', self.scroll_letter)

    # Any code you write here will run when the form opens.
    letters = list(string.ascii_uppercase)
    data = []
    for let in letters:
      # Group all our accounts by letter of the alphabet
      accounts = [x for x in self.accounts if x['name'][0].upper() == let]
      if accounts:
        data.append({'letter': let, 'accounts':accounts})
    
    # Work out which letters of the alphabet should be visible
    # Don't show letters if none of our accounts' surnames begin with that letter
    visible_letters = [x['letter'] for x in data]
    letters = [{
        'letter': x,
        'visible': x in visible_letters
      } for x in string.ascii_uppercase]
    
    self.letters_repeating_panel.items = letters
    print("accounts init complete")
    
  def scroll_letter(self, letter, **event_args):
    # This event is raised on the 'Letter' Form
    # Call the `scroll_accounts_letter_group` method on the 'Table' Form
    self.accounts_table.scroll_accounts_letter_group(letter)
    
    