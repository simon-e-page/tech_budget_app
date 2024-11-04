from ._anvil_designer import TransactionReviewTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..... import Data
from .....Data import VendorsModel

class TransactionReview(TransactionReviewTemplate):
  def __init__(self, **properties):
    self.vendors = VendorsModel.VENDORS
    self.final_import_data = None

    self.lifecycles = Data.LIFECYCLES_DD
    self.account_codes = Data.ACCOUNT_CODES_DD
    self.service_changes = Data.SERVICE_CHANGES_DD
    self.billing_types = Data.BILLING_TYPES_DD
    self.categories = Data.CATEGORIES_DD
    
    
    self.entry_table.options = {
      'selectable': "highlight",
      'pagination': True,
      'pagination_size': 10,
      'css_class': ["table-striped", "table-bordered", "table-condensed"]
    }
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  @property
  def import_data(self):
    return self._import_data

  @import_data.setter
  def import_data(self, import_data):
    self._import_data = import_data
    
    # Any code you write here will run before the form opens.
  def build_entry_table(self, vendor_map):
    """ vendor_map should be a dictionary of replacement vendor_name for any vendors that are replaced on import (deprecated) """

    def dropdown_formatter(cell, items, placeholder, **params):
      def dd_changed(sender, **event_args):
        cell = sender.tag
        field = cell.getField()
        desc = cell.get_data()['description']
        old_value = cell.get_value()
        new_value = sender.selected_value
        print(f"Got change in {field} for {desc}. From {old_value} to {new_value}")
        
      val = cell.get_value()
      dd = DropDown(items=items, placeholder=placeholder, tag=cell, selected_value=val)
      dd.add_event_handler('change', dd_changed)
      return dd
      
    def total_formatter(cell, **params):
      val = cell.get_value()
      return f"{val:,.0f}"
      
    columns = [
      {
        'title': 'Description',
        'field': 'description',
        'width': 220,
      },
      {
        'title': 'Vendor',
        'field': 'vendor_name',
        'width': 200,
      },
      {
        'title': 'Cost Centre',
        'field': 'cost_centre',
        'width': 100,
      },
      {
        'title': 'Lifecycle',
        'field': 'lifecycle',
        'width': 150,
        'formatter': dropdown_formatter,
        'formatterParams': { 'items': self.lifecycles, 'placeholder': "Select Lifecycle" }
      },
      {
        'title': 'Account',
        'field': 'account_code',
        'width': 150,
        'formatter': dropdown_formatter,
        'formatterParams': { 'items': self.account_codes, 'placeholder': "Select Account Code" }
      },
      {
        'title': 'Category',
        'field': 'category',
        'width': 150,
        'formatter': dropdown_formatter,
        'formatterParams': { 'items': self.categories, 'placeholder': "Select Category" }
      },
      {
        'title': 'Service Change',
        'field': 'service_change',
        'width': 150,
        'formatter': dropdown_formatter,
        'formatterParams': { 'items': self.service_changes, 'placeholder': "Select Service Change" }
      },
      {
        'title': 'Billing',
        'field': 'billing_type',
        'width': 150,
        'formatter': dropdown_formatter,
        'formatterParams': { 'items': self.billing_types, 'placeholder': "Select Billing Type" }
      },
      
      {
        'title': 'Total',
        'field': 'total',
        'width': 100,
        'formatter': total_formatter
        
      },
    ]

    total = sum( x['total'] for x in self.import_data)
    num_lines = len(self.import_data)

    self.entry_table.columns = columns
    
    def sub(row):
      """ Replaced the vendor_name in an import row with either the automated or manual mapping replacements """
      import_vendor_name = row['vendor_name']
      import_vendor_id = row['vendor_id']
      new_row = row.copy()
      if (import_vendor_id is not None) and (import_vendor_id != 0):
        new_row['vendor_name'] = self.vendors.get(import_vendor_id)['vendor_name']
      elif vendor_map is not None:
        # TODO: remove!
        print(f"WARNING: Called vendor_map with {import_vendor_name}!")
        new_row['vendor_name'] = vendor_map.get(import_vendor_name, import_vendor_name)
      else:
        new_row['vendor_name'] = import_vendor_name 
      return new_row
      
    self.final_import_data = [ sub(x) for x in self.import_data ]
    self.entry_table.data = self.final_import_data
    self.entry_table.set_sort('vendor_name', 'asc')
    return total, num_lines

  
  def get_final_import_data(self):
    return self.final_import_data