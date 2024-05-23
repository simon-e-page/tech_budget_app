from ._anvil_designer import TransactionTemplate
from anvil import *
#import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server
from datetime import datetime
from ... import Data
from ... import Validation
from ...Settings.Settings.SettingsDetails import SettingsDetails

class Transaction(TransactionTemplate):
  """This Form displays transaction and account information for a single transaction. It also allows you to edit the transaction being displayed.
  
  Keyword Arguments:
    item - a row from the 'Transaction' Data Table
    back - a dictionary containg the form to open and the filters to apply when back is clicked 
    
  A copy of this row from the 'Transaction' table is initialised as self.transaction_copy in form_refreshing_data_bindings()
  """
  
  def __init__(self, item, back=None, **properties):
    self.vendors = ['vendor example']
    self.account_codes = ['code example']
    self.cost_centres = ['cost centre example']
    self.lifecycles = ['lifecycle example']
    self.categories = ['category example']
    self.owners = ['SimonPage']
    
    #self.accounts = Data.ACCOUNTS_D.get_dropdown()
    #self.accounts_d = Data.ACCOUNTS_D
    #self.organisations = Data.ORGANISATIONS
    self.back=back
    properties['item'] = item
    print(type(item))
    #self.item = item
    #print(item)
    self.transaction_copy = {}
    
    self.initialised = False
    #self.account_changed = None
    #self.organisation_changed = False
    
    # Set Form properties and Data Bindings.
    #self.form_refreshing_data_bindings()
    print("In Transaction.__init__")
    self.init_components(**properties)
    print("In Transaction.__init__")
    # Any code you write here will run when the form opens.
    self.reset_controls()
    #self.set_rule()
    self.transaction_entries_1.build_table(self.item)
    print("Complete Transaction.__init__")
    
    
  def form_refreshing_data_bindings(self, **event_args):
    print("In: form_refreshing_data_bindings()")
    # If self.item exists and ticket_copy not yet initialised, initialise it. 
    if (not self.initialised and self.item is not None) or (self.transaction_copy == {}):
      self.initialised = True
      self.transaction_copy = self.item.copy()
      print("made item copy")

  
  # Change transaction details
  def update_transaction(self, **event_args):
    trans_validation_errors = Validation.get_transaction_settings_errors(self.transaction_copy)
    if trans_validation_errors:
      alert("The following fields are missing for your transaction: \n{}".format(
        ' \n'.join(word for word in trans_validation_errors)
      ))
    else:
      self.transaction_copy['updated_by'] = anvil.users.get_user()['email']
      self.transaction_copy['updated'] = datetime.now()
      updates = self.transaction_copy.to_dict()
      updates.pop('transaction_id', None)
      self.item.update(updates)
      #anvil.server.call('update_transaction', self.item, self.transaction_copy)
      self.refresh_data_bindings()

  def revert_button_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.transaction_copy = self.item.copy()
    self.reset_controls()
    #self.form_refreshing_data_bindings()

  def save_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    
    self.update_transaction()
    Notification('Transaction details updated successfully').show()
    #alert("Updates saved!")
    self.reset_controls()
    self.refresh_data_bindings()
      
    
      

  def back_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    back = self.back
    if back is not None:
      open_func = back.pop('open_func')
      print(back)
      open_func(**back)
    else:
      homepage = get_open_form()
      homepage.open_transactions()

    

  def reset_controls(self):
    print("In reset_controls")
    #self.credit_account_dropdown.enabled = True
    self.revert_button.enabled = False

      
    
  def notes_area_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    self.save_button.enabled = True
    self.revert_button.enabled = True


  def delete_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    return
    if confirm("Are you sure you want to delete this transaction?", large=True):
      Data.TRANSACTIONS.delete([self.item.transaction_id])
      #count = anvil.server.call("delete_transactions", [self.item])
      self.back_button_click()

  