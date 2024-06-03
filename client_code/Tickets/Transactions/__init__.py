from ._anvil_designer import TransactionsTemplate
from anvil import *
import anvil.users
import anvil.server
from datetime import date, datetime, time, timezone

from ... import Data
from ...Data import VendorsModel
from ...Data import UsersModel

class Transactions(TransactionsTemplate):
  """This Form is responsible for passing user-defined filters to the 'TransactionList' Form.
  
  The filtering logic is collected from user inputs and sent to the 'TransactionList' Form to be processed. 
  """
  
  def __init__(self, initial_filters=None, initial_date_filter=None, initial_page=0, filter_settings=None, direction='descending', **properties):
    """Collect filters, and send them to the TransactionList Form to retrieve a list of transaction.
    
    Arguments: 
      initial_filters (optional): dict of filters on the transaction view
      initial_date_filters (optional): dict of date filters on the transaction view
    """
    self.vendors = VendorsModel.VENDORS
    self.vendor_list = self.vendors.get_dropdown()
    
    self.filter_settings = filter_settings or {}
    self.direction = direction
    self.filters = initial_filters or { 'brand': Data.CURRENT_BRAND }
    
    self.date_filter = initial_date_filter or {}
    self.initial_page = initial_page
    self.current_import_ids = []
    
    if (isinstance(self.filters, dict) and len(self.filters)>0):
      #print(self.filters)
      self.set_filter_settings()
    elif isinstance(self.filters, dict):
      pass
    else:
      #print(self.filters)
      self.set_filter_settings()

    if (isinstance(self.date_filter, dict) and len(self.date_filter)>0):
      self.set_date_filter_settings()
    elif isinstance(self.date_filter, dict) or self.date_filter is None:
      pass
    else:
      self.set_date_filter_settings()

    self.account_codes = Data.ACCOUNT_CODES_DD
    self.cost_centres = Data.COST_CENTRES_DD
    self.lifecycles = Data.LIFECYCLES_DD
    self.categories = Data.CATEGORIES_DD
    self.owners = UsersModel.OWNERS_DD
    self.service_changes = Data.SERVICE_CHANGES_DD
    self.billing_types = Data.BILLING_TYPES_DD
    self.transaction_types = ['Budget', 'Actual']

    for tag in ['vendor', 'category', 'description', 'lifecycle', 'owner', 'transaction_type']:
      if tag not in self.filters:
        self.filters[tag] = None

    self.init_components(**properties)
    self.load_transactions()
    # Any code you write here will run when the form opens.

    
  def load_transactions(self, **event_args):
    # If the filters are changed, de-select any currently selected transaction. This is done on the 'TransactionList' Form
    # Why is this set up as an event? Does it need to be?
    self.transaction_list.clear_selected_link_click()
    self.transaction_list.load_transactions(filters=self.filters, date_filter=self.date_filter, initial_page=self.initial_page, filter_settings=self.filter_settings, direction=self.direction)

  def set_filter_settings(self):
    #print(self.filter_settings)
    self.vendor = self.filter_settings.get('vendor', None)
    self.description = self.filter_settings.get('description', None)
    self.transaction_type = self.filter_settings.get('transaction_type', None)
    self.lifecycle = self.filter_settings.get('lifecycle', None)
    self.category = self.filter_settings.get('category', None)
    self.owner = self.filter_settings.get('owner', None)
        
  
  def clear_filters_link_click(self, **event_args):
    self.filters = { 'brand': Data.CURRENT_BRAND }
    for tag in ['vendor', 'category', 'description', 'lifecycle', 'owner', 'transaction_type']:
      if tag not in self.filters:
        self.filters[tag] = None
    
    self.refresh_data_bindings()
    self.load_transactions()
    
  def apply_button_click(self, **event_args):
    """This method is called when an filter is changed.
    """
    for tag in self.filters:
      if self.filters[tag] is not None:
        self.filter_settings[tag] = self.filters[tag]
      
    self.initial_page = 0
    self.load_transactions()








