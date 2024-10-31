from ._anvil_designer import VendorSelectorTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..... import Data
from .....Data import VendorsModel

class VendorSelector(VendorSelectorTemplate):
  def __init__(self, **properties):
    self.vendors = VendorsModel.VENDORS
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  
  def build_vendor_table(self, data):
    vendor_list = self.vendors.get_dropdown()

    def match_selected(sender, **event_args):
      cell = sender.tag
      d = cell.get_data()
      vendor_name = d['vendor_name']
      existing_vendor_id = sender.selected_value
      manual_suggested_name = self.vendors.get(existing_vendor_id)['vendor_name']
      d['suggested'] = manual_suggested_name
      if cell.getRow().isSelected():
        d['create_new'] = False
        cell.getRow().deselect()
        create_cell = cell.getRow().getCell('create_new')
        create_cell.set_value(False)
      print(f"Manual match: {vendor_name} -> {manual_suggested_name}")
      
    def format_suggested(cell, **params):
      suggested_value = cell.get_value()
      suggested_id = None      
      if suggested_value:
        suggested_id = self.vendors.get_by_name(suggested_value)['vendor_id']
        print(f"{suggested_value} => ID: {suggested_id}")
      obj = DropDown(items=vendor_list, include_placeholder=True, placeholder="Select Existing Vendor", tag=cell, selected_value=suggested_id)
      obj.add_event_handler('change', match_selected)
      return obj

    def select_row(sender, **event_args):
      cell = sender.tag
      d = cell.get_data()
      #vendor_name = d['vendor_name']
      create_new = d['create_new']
      d['create_new'] = not create_new
      cell.getRow().getCell('suggested').set_value(None)
      #print(f"Flag for {vendor_name} was {create_new}. Changed to {not create_new}")
      cell.getRow().toggleSelect()
      

    def new_flag_formatter(cell, **params):
      val = cell.get_value()
      if val:
        cell.getRow().select()
      #vendor_name = cell.get_data()['vendor_name']
      obj = CheckBox(checked=val, tag=cell)
      obj.add_event_handler('change', select_row)
      return obj
      
    columns = [
      {
        'title': 'New Vendor Name',
        'field': 'vendor_name',
        'width': 200,
        'headerSort': False
      }, 
      {
        'title': 'Suggested Match',
        'field': 'suggested',
        'headerSort': False,
        'width': 200,
        'formatter': format_suggested,
      }, 
      {
        "title": "Create New Instead?",
        "field": "create_new",
        #"formatter": "tickCross",
        "formatter": new_flag_formatter,
        #"title_formatter": "rowSelection",
        #"title_formatter_params": {"rowRange": "visible"},
        "width": 150,
        "hoz_align": "center",
        "header_hoz_align": "center",
        "header_sort": False,
        #"editor": "tickCross",
        #"cellClick": select_row,
        #"cellClick": lambda e, cell: cell.getRow().toggleSelect(),
      }            
    ]

    self.vendor_table.columns = columns
    self.vendor_table.data = data

  def get_data(self):
    return self.vendor_table.data