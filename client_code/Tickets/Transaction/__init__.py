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
  
  def __init__(self, back=None, **properties):
    self.vendors = Data.VENDORS.get_dropdown()
    self.account_codes = Data.ACCOUNT_CODES_DD
    self.cost_centres = Data.COST_CENTRES_DD
    self.lifecycles = Data.LIFECYCLES_DD
    self.categories = Data.CATEGORIES_DD
    self.service_changes = Data.SERVICE_CHANGES_DD
    self.billing_types = Data.BILLING_TYPES_DD
    self.titles = { 'Budget': 'Budget Line Detail', 'Actual': 'Finance Actual Detail'}
  
    self.back=back
    self.transaction_copy = {}
    
    self.initialised = False
    
    # Set Form properties and Data Bindings.
    print("In Transaction.__init__")
    self.init_components(**properties)
    print("In Transaction.__init__")
    # Any code you write here will run when the form opens.
    self.reset_controls()
    self.transaction_entries_1.build_table(self.item)
    print("Complete Transaction.__init__")
    
    
  def form_refreshing_data_bindings(self, **event_args):
    print("In: form_refreshing_data_bindings()")
    # If self.item exists and transaction_copy not yet initialised, initialise it. 
    if (not self.initialised and self.item is not None) or (self.transaction_copy == {}):
      self.initialised = True
      self.transaction_copy = self.item.copy()
      print("made item copy")

  
  # Change transaction details
  def update_transaction(self, **event_args):
    #trans_validation_errors = Validation.get_transaction_settings_errors(self.transaction_copy)
    #if trans_validation_errors:
    #  alert("The following fields are missing for your transaction: \n{}".format(
    #    ' \n'.join(word for word in trans_validation_errors)
    #  ))
    #else:
    self.item['updated_by'] = anvil.users.get_user()['email']
    self.item['updated'] = datetime.now()
    updates = self.item.to_dict()
    updates.pop('transaction_id', None)
    self.item.update()
    self.transaction_copy = self.item.copy()
    self.refresh_data_bindings()

  def revert_button_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.item = self.transaction_copy.copy()
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
    if confirm("This will remove this transaction completely! Are you sure?", large=True):
      Data.TRANSACTIONS.delete([self.item.transaction_id])
      #count = anvil.server.call("delete_transactions", [self.item])
      self.back_button_click()

  def inactive_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if confirm("This will remove this transaction from future budgets. Are you sure?", large=True):
      self.item['status']=='inactive'
      self.update_transaction()
      self.back_button_click()

  