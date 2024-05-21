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
    self.types = Data.TYPES
    self.subtypes = Data.SUBTYPES
    self.orders = [ str(x) for x in list(range(0,8)) ]
    self.importers = Data.IMPORTERS
    self.order_raw = '0'
    self.duplicates_raw = ''
    self.name_unique = False
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
 
  def back_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    homepage = get_open_form()
    homepage.open_accounts()

  def get_icon(self, icon_id):
    return Data.get_icon(icon_id)

  def save_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Remap altered attributes back after possible editing
    name = self.item['name']
      
    l = self.duplicates_raw.split('\n')
    self.item['duplicates'] = l
    self.item['order'] = int(self.order_raw)
    #for key, default in ['budget', 'reconcile', 'discretionary', 'report']:
    #  if self.item.get(key, None) is None: 
    #    self.item[key] = False

    #for key in ['order', 'default_budget']:
    #  if self.item.get(key, None) is None:
    #    self.item[key] = 0

    new_account = Data.Account(**self.item)
    account_validation_errors = Validation.get_account_errors(new_account)
    
    if not account_validation_errors:
      new_account.save()
      #anvil.server.call('add_account', self.item)
      Data.refresh()
      Notification('New account {0} created'.format(name)).show()
      
      self.back_button_click()
    else:
      alert("The following mandatory fields are missing: \n{}".format(
        ' \n'.join(account_validation_errors)
      ))


  def type_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.type_dropdown.selected_value == 'ASSET':
      self.order_dropdown.selected_value = '5'
    elif self.type_dropdown.selected_value =='LIABILITY':
      self.order_dropdown.selected_value = '6'
    elif self.type_dropdown.selected_value =='INCOME':
      self.order_dropdown.selected_value = '1'
    elif self.type_dropdown.selected_value =='EXPENSE':
      self.order_dropdown.selected_value = '2'
    self.refresh_data_bindings()

  def budget_checkbox_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    self.refresh_data_bindings()


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


  def name_textbox_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.name_unique = not (self.name_textbox.text in Data.ACCOUNTS_D)
    

  def name_textbox_lost_focus(self, **event_args):
    """This method is called when the TextBox loses focus"""
    self.refresh_data_bindings()






