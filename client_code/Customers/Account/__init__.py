from ._anvil_designer import AccountTemplate
from anvil import *
#import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server
from ... import Validation
from ... import Data


class Account(AccountTemplate):
  """This Form is responsible for editing account information. 
  
  It is added to the 'Overlay' slot on the 'Homepage' Form, 
  which overlays it on top of the Form in the 'default' slot on the Homepage.
  It has a click handler on the 'grey' section of the overlay, which removes the overlay to reveal the content underneath. 
  This is trigged by JavaScript on the 'three_slot_overlay.html' asset, which calls the 'clear_overlay' method on this Form, from JavaScript.
  
  Keyword arguments:
    item - accepts a row from the acocunts data table
           Initialises this in the 'refresh_data' method.
  """
  
  def __init__(self, **properties):
    # This is replaced by the copy of the item property created in self.account_details
    self.account_copy = {}
      
    self.types = Data.TYPES
    self.importers = Data.IMPORTERS
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.account_copy = self.account_details.account_copy
    self.refresh_data_bindings()
    
  def clear_overlay(self):
    """This is called from the JavaScript on the `three_slot_overlay.html` asset"""
    homepage = get_open_form()
    homepage.close_overlay()

  def icon_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    ACCEPTABLE = ['image/png', 'image/jpg', '']
    #alert("".format(file.content_type))
    
    if file.content_type in ACCEPTABLE:
      try:
        self.account_copy['avatar'] = file
        self.refresh_data_bindings()
        #self.edit_image.source = file
      except Exception as e:
        alert('Not an acceptable image file. Please try again!')
        print(e)
    else:
      alert('Not an acceptable image file. Please try again!')

  def form_refreshing_data_bindings(self, **event_args):
    # Do we need to be explicit with these fields?
    #print("Entering: form_refreshing_data_bindings")
    self.notes_textarea.text = self.account_copy.get('notes', '')
    self.default_budget_text.text = self.account_copy.get('default_budget', 0)
    self.duplicates_areabox.text = self.account_copy.get('duplicates_box', '')
    self.import_pattern_box.text = self.account_copy.get('import_pattern', '')
    self.importer_dropdown.selected_value = self.account_copy.get('importer', None)
    self.order_dropdown.selected_value = self.account_copy.get('order_string', '0')

    

      
      
      
      
      
      
      
      
      
      
      
