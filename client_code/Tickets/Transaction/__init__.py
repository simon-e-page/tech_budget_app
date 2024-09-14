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
from ...Data import VendorsModel
from ...Data import TransactionsModel, UsersModel
from ...Vendors.Vendors.Vendor import Vendor
from .TransactionEntries import TransactionEntries

class Transaction(TransactionTemplate):
  """This Form displays transaction and account information for a single transaction. It also allows you to edit the transaction being displayed.
  
  Keyword Arguments:
    item - a row from the 'Transaction' Data Table
    back - a dictionary containg the form to open and the filters to apply when back is clicked 
    
  A copy of this row from the 'Transaction' table is initialised as self.transaction_copy in form_refreshing_data_bindings()
  """
  
  def __init__(self, item, back=None, **properties):
    self.vendors = VendorsModel.VENDORS
    self.transactions = TransactionsModel.get_transactions()
    self.vendor_list = self.vendors.get_dropdown()
    self.account_codes = Data.ACCOUNT_CODES_DD
    self.cost_centres = Data.COST_CENTRES_DD
    self.lifecycles = Data.LIFECYCLES_DD
    self.categories = Data.CATEGORIES_DD
    self.service_changes = Data.SERVICE_CHANGES_DD
    self.billing_types = Data.BILLING_TYPES_DD
    self.teams = UsersModel.TEAMS_DD
    
    self.back=back
    properties['item'] = item
    
    self.transaction_copy = {}
    self.updated_entries = []
    
    self.initialised = False

    self.budget_labels = { True: "Budget Line Detail", False: "Actual Line Detail" }
    self.actual_button_labels = { True: 'Enter Actual', False: 'Enter Budget'}
    
    # Set Form properties and Data Bindings.
    print("In Transaction.__init__")
    self.init_components(**properties)
    print("In Transaction.__init__")
    # Any code you write here will run when the form opens.
    self.reset_controls()
    #self.transaction_entries_1.build_table(self.item)
    print("Complete Transaction.__init__")
    
  def show(self, title="", new=False):
    save_button = "Add New" if new else "Save Changes"
    ret = alert(self, title=title, large=True, buttons=((save_button, True), ("Cancel", False)))
    if ret:
      if new:
        pass
      else:
        try:
          self.item.update()
          self.update_entries()
        except Exception as e:
          alert("Error saving changes!")
          print(e)
          ret = False
    return ret

  @property
  def vendor_id(self):
    if self.item['vendor'] is not None:
      return self.item['vendor']['vendor_id']
    else:
      return None

  @vendor_id.setter
  def vendor_id(self, vendor_id):
    self.item['vendor'] = self.vendors.get(vendor_id, default=None)
    
  def form_refreshing_data_bindings(self, **event_args):
    print("In: form_refreshing_data_bindings()")
    # If self.item exists and ticket_copy not yet initialised, initialise it. 
    if (not self.initialised and self.item is not None) or (self.transaction_copy == {}):
      self.initialised = True
      self.transaction_copy = self.item.copy()
      print("made item copy")

  
  # Change transaction details
  def update_transaction(self, **event_args):
    self.item.update()
    self.refresh_data_bindings()


  def reset_controls(self):
    print("In reset_controls")

  
  def disable_checkbox_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    if not self.disable_checkbox.checked or confirm("This will prevent this entry being used in future budgets. Are you sure?", large=True):
        self.item['status'] == 'inactive'
        self.update_transaction()
    self.refresh_data_bindings()

  def new_vendor_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    new_vendor = self.vendors.blank()
    ret = alert(Vendor(item=new_vendor, show_save=False), large=True, title="New Vendor", buttons=[ ('OK', True), ('Cancel', False) ])
    if ret:
      try:
        new_vendor = self.vendors.add(new_vendor.vendor_id, new_vendor)
        new_vendor.save()
      except Exception as e:
        print("Failed to create new Vendor!")

  def actual_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.item.transaction_type = 'Actual' if self.item.transaction_type == 'Budget' else 'Budget'
    #self.transaction_entries_1.build_table(self.item)
    self.refresh_data_bindings()

  def edit_entries_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    entry_form = TransactionEntries()
    self.updated_entries = entry_form.show(self.item, self.item.transaction_type)

  def update_entries(self, **event_args):
    """This method is called when the button is clicked"""
    print(self.updated_entries)
    if len(self.updated_entries) > 0:
      count = self.item.add_entries(self.updated_entries)
      if not count:
        alert("Error updating entries! Check logs")
      else:
        Notification(f"{count} entries updated successfully").show()
        self.updated_entries = []
        self.build_table(self.transaction)

    
  