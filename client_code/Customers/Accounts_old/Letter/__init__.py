from ._anvil_designer import LetterTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class Letter(LetterTemplate):
  """This Form is the ItemTemplate of the RepeatingPanel on the 'Accounts' Form"""
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def letter_link_click(self, **event_args):
    selected_letter = self.item['letter']
    # Raise an event on the parent `letters_repeating_panel` 
    # the event scrolls the appropriate letter group into view when a letter is clicked
    self.parent.raise_event('x-scroll-letter', letter=selected_letter)


