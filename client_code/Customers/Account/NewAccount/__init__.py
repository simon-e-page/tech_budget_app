from ._anvil_designer import NewAccountTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
#import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
from .... import Data
from .... import Validation

#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
from datetime import datetime, timedelta

class NewAccount(NewAccountTemplate):
  def __init__(self, **properties):
    self.name_unique = False
    self.prior_year_tags_raw = ''
    self.finance_tags_raw = ''
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
 
  def back_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    homepage = get_open_form()
    homepage.open_accounts()

  def get_icon(self, icon_id):
    return
    #return Data.get_icon(icon_id)

  def save_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Remap altered attributes back after possible editing
    name = self.item['name']
      
    l = self.finance_tags_raw.split('\n')
    self.item['finance_tags'] = l

    l = self.prior_year_tags_raw.split('\n')
    self.item['prior_year_tags'] = l
    
    self.item = Data.VENDORS.new(self.item)
    #account_validation_errors = Validation.get_account_errors(new_account)          
    self.back_button_click()

  
  def icon_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    title = "{0}_icon_{1}.{2}".format(self.item['name'], timestamp)
    try:
      icon = Data.Icon(name=title, content=file, icon_id=None)
      Data.ICONS.add(icon.icon_id, icon)
      self.item['icon_id'] = icon.icon_id
      self.refresh_data_bindings()
    except Exception as e:    
      alert("Error uploading new icon!")
      icon = None
      self.item['icon_id'] = ''







