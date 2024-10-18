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
from .VendorDetailTable import VendorDetailTable

class Transaction(TransactionTemplate):
  """This Form displays transaction and account information for a single transaction. It also allows you to edit the transaction being displayed.
  
  Keyword Arguments:
    item - a row from the 'Transaction' Data Table
    back - a dictionary containg the form to open and the filters to apply when back is clicked 
    
  A copy of this row from the 'Transaction' table is initialised as self.transaction_copy in form_refreshing_data_bindings()
  """
  
  def __init__(self, item=None, back=None, **properties):
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
    self.year = Data.CURRENT_YEAR
    self.initialised = False
    self.entry_data = None
    self.updated_entries = []
    self.budget_labels = { True: "Budget Line Detail", False: "Actual Line Detail" }
    self.actual_button_labels = { True: 'Enter Actual', False: 'Enter Budget'}

    if item is not None:
      self.transaction_copy = self.item.copy()
    else:
      self.transaction_copy = {}

    self.back=back
    properties['item'] = item
    
    self.item = item
        
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.
    self.reset_controls()
    #self.transaction_entries_1.build_table(self.item)

  
  
  def show(self, title="", new=False):
    save_button = "Add New" if new else "Save Changes"
    ret = alert(self, title=title, large=True, buttons=((save_button, True), ("Cancel", False)))
    if ret:
      if new:
        try:
          self.transactions.new(transaction=self.item)
          print(f"New Transaction ID = {self.item.transaction_id}")
          self.update_entries()
        except Exception as e:
          alert("Error creating new transaction!")
          print(e)
          ret = False
          
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
    #print("In: form_refreshing_data_bindings()")
    # If self.item exists and ticket_copy not yet initialised, initialise it. 
    #if (not self.initialised and self.item is not None) or (self.transaction_copy == {}):
    #  self.initialised = True
    #  self.transaction_copy = self.item.copy()
    pass
  
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


  

  def edit_entries_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    entry_form = TransactionEntries(t_data=self.entry_data, updated_entries=self.updated_entries)
    self.entry_data, new_updated_entries = entry_form.show(self.item, self.item.transaction_type)
    self.updated_entries += new_updated_entries


  
  def update_entries(self):
    if len(self.updated_entries) > 0:
      count = self.item.add_entries(self.updated_entries, overwrite=True)
      if not count:
        alert("Error updating entries! Check logs")
      else:
        Notification(f"{count} entries updated successfully").show()
        self.updated_entries = []

  def current_entries_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    vendor = self.item['vendor']
    mode = self.item['transaction_type']
    vendor_form = VendorDetailTable(mode=mode, vendor=vendor, year=self.year, transaction_ids=[self.item['transaction_id']])
    ret = alert(vendor_form, large=True, title=f"{mode} Entries for {self.year}", buttons=[ ('Save Changes', True), ('Cancel', False) ])
    if ret:
      entries = vendor_form.get_updated_entries()
      print(entries)
      if len(entries)>0:
        count = 0
        for transaction_id, trans_entries in entries.items():
          self.item.add_entries(trans_entries, overwrite=True)
          count += len(trans_entries)
        Notification(f"{count} entries added or updated").show()
  