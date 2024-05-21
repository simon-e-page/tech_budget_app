from ._anvil_designer import TransactionTemplate
from anvil import *
#import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
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
    self.accounts = Data.ACCOUNTS_D.get_dropdown()
    self.accounts_d = Data.ACCOUNTS_D
    self.organisations = Data.ORGANISATIONS
    self.back=back
    properties['item'] = item
    #self.item = item
    #print(item)
    self.transaction_copy = {}
    
    self.initialised = False
    self.account_changed = None
    self.organisation_changed = False
    
    # Set Form properties and Data Bindings.
    #self.form_refreshing_data_bindings()
    print("In Transaction.__init__")
    self.init_components(**properties)
    print("In Transaction.__init__")
    # Any code you write here will run when the form opens.
    self.reset_controls()
    self.set_rule()
    print("Complete Transaction.__init__")
    
  def load_organisations(self):
    Data.refresh_organisations()
    self.organisations = Data.ORGANISATIONS
    
  def form_refreshing_data_bindings(self, **event_args):
    print("In: form_refreshing_data_bindings()")
    # If self.item exists and ticket_copy not yet initialised, initialise it. 
    if (not self.initialised and self.item is not None) or (self.transaction_copy == {}):
      self.initialised = True
      self.transaction_copy = self.item.copy()
      print("made item copy")

  # Change the description of the transaction
  def transaction_description_edit(self, **event_args):
    if self.description_box.text is not "":
      self.save_button.enabled = True
      self.revert_button.enabled = True
    else:
      self.description_box.text = self.item['description']
      alert("Please give your transaction a description")
  
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
    test1 = (self.account_changed == 'credit account') and (self.transaction_copy['organisation'] != '')
    test2 = self.organisation_changed and (self.transaction_copy['credit_account'] != 'Unknown')
    #print(self.account_changed)
    #print(self.transaction_copy['organisation'])
    #print(self.transaction_copy['credit_account'])

    if test1 or test2:
      if confirm("Remember new Credit Account and Organisation setting for future imports?"):
        t = TextBox(placeholder=self.transaction_copy['description'])
        alert(content=t,
              title="Confirm description pattern for this account")
        if len(t.text) > 0:
          self.transaction_copy['suggested'] = False
          org = self.transaction_copy['organisation']
          account_name = self.transaction_copy['credit_account']
          p = Data.RULES.new(pattern_description=t.text, account_name=account_name, organisation=org)
          #anvil.server.call('add_organisation_map', name=org, pattern=t.text, account_name=account_name)

    #try:
    self.update_transaction()
    Notification('Transaction details updated successfully').show()
    #alert("Updates saved!")
    self.reset_controls()
    self.refresh_data_bindings()
    #except Exception as e:
    #  alert("Error while updating. Messag: {0}".format(e))
      
    
      

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

  def debit_account_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.save_button.enabled = True
    self.revert_button.enabled = True
    self.apply_all_button.enabled = True
    self.account_changed = 'debit_account'
    self.credit_account_dropdown.enabled = False
    self.refresh_data_bindings()

  def credit_account_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""      
    self.save_button.enabled = True
    self.revert_button.enabled = True
    self.apply_all_button.enabled = True
    self.account_changed = 'credit_account'
    self.debit_account_dropdown.enabled = False
    self.refresh_data_bindings()

  def amount_box_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    if self.transaction_copy['amount'] > 0:
      self.save_button.enabled = True
      self.revert_button.enabled = True
    else:
      self.transaction_copy['amount'] = self.item['amount']

  def get_icon(self, icon_id):
    return Data.get_icon(icon_id)
    

  def duplicate_check_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    self.save_button.enabled = True
    self.revert_button.enabled = True

  def reset_controls(self):
    print("In reset_controls")
    self.debit_account_dropdown.enabled = True
    self.credit_account_dropdown.enabled = True
    self.save_button.enabled = False
    self.revert_button.enabled = False
    self.apply_all_button.enabled = False
    self.apply_all_button.visible = False

    if (self.transaction_copy['organisation'] is not None) and (len(self.transaction_copy['organisation'])>0):
      if self.transaction_copy['organisation'] in self.organisations:
        self.organisation_dropdown.selected_value = self.transaction_copy['organisation']
        self.organisation_dropdown.visible = True
      else:
        # This will happen if there is no Pattern for this Organisation
        #print("Organisation value is not in Orgnaisation list: {0}".format(self.transaction_copy['organisation']))
        self.organisation_dropdown.enabled = False
        self.organisation_box.visible = True
        self.organisation_box.text = self.transaction_copy['organisation']
        
    else:
        self.organisation_dropdown.selected_value = None
        self.organisation_dropdown.visible = True
      
    
  def notes_area_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    self.save_button.enabled = True
    self.revert_button.enabled = True

  def set_rule(self):
    self.rules_form.set_main_form(self)
    rule = Data.RULES.match(self.item)
    if rule:
      self.rules_form.set_rule(item=rule)
    else:
      self.rules_form.item['pattern_description'] = self.item['description']
      self.rules_form.item['pattern_source'] = self.item['source']
      if self.item['source'] != 'Manual Entry':
        account_name = self.item['credit_account'] if self.item['credit_account'] != self.item['source'] else self.item['debit_account']
        self.rules_form.item['account_name'] = account_name
    #self.apply_all_button.enabled = False

  def change_account(self, *args, **kwargs):
    pass
  
  def build_datagrid(self, *args, **kwargs):
    pass

  def account_select_change(self, *args, **kwargs):
    pass
    
  def apply_all_button_click_old(self, **event_args):
    """This method is called when the Apply to All button is clicked"""
    trans_validation_errors = Validation.get_transaction_settings_errors(self.transaction_copy)
    if trans_validation_errors:
      alert("The following fields are missing for your transaction: \n{}".format(
        ' \n'.join(word for word in trans_validation_errors)
      ))
    else:
      matched_trans = Data.TRANSACTIONS.match(self.item)
      #matched_trans = anvil.server.call('match_transactions', self.item)
      msg = "Found {0} matched transactions. Set {1} to {2} and copy Duplicate and Organisation settings for all of these?".format(len(matched_trans), self.account_changed, self.transaction_copy[self.account_changed])
      if confirm(msg, title="Please confirm", large=True):
        self.transaction_copy['updated_by'] = anvil.users.get_user()['email']
        self.transaction_copy['updated'] = datetime.now()
        updates = {}
        for k in ['updated', 'updated_by', self.account_changed, 'duplicate', 'organisation' ]:
          updates[k] = self.transaction_copy[k]
        ids = [ x.transaction_id for x in matched_trans ]
        count = Data.TRANSACTIONS.update(ids, updates)
        #count = anvil.server.call('update_transaction_all', matched_trans, self.transaction_copy, self.account_changed)
        
        Notification('{0} transaction details updated successfully'.format(count)).show()
        #alert("{0} transactions updated successfully".format(count), "Success")
        self.reset_controls()
        self.refresh_data_bindings()

  def delete_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if confirm("Are you sure you want to delete this transaction?", large=True):
      Data.TRANSACTIONS.delete([self.item.transaction_id])
      #count = anvil.server.call("delete_transactions", [self.item])
      self.back_button_click()

  
  def organisation_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.transaction_copy['organisation'] = self.organisation_dropdown.selected_value
    #self.pattern_textbox.text = self.transaction_copy['description']
    #self.pattern_textbox.visible = True
    #self.save_pattern_button.visible = True
    self.save_button.enabled = True
    self.revert_button.enabled = True
    self.organisation_changed = True

  def organisation_box_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    if len(self.organisation_box.text) > 0:
      #self.organisation_dropdown.selected_value = None
      self.organisation_dropdown.enabled = False
      self.transaction_copy['organisation'] = self.organisation_box.text
    else:
      self.organisation_dropdown.enabled = True
      
    self.save_button.enabled = True
    self.revert_button.enabled = True
    self.organisation_changed = True
