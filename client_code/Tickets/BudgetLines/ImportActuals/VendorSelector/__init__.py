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
    self.vendor_list = self.vendors.get_dropdown(import_ignore=False)
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  
  def build_vendor_table(self, data):
    vendor_list = self.vendor_list

    def match_selected(sender, **event_args):
      cell = sender.tag
      d = cell.get_data()
      vendor_name = d['vendor_name']
      existing_vendor_id = sender.selected_value
      manual_suggested_name = self.vendors.get(existing_vendor_id)['vendor_name']
      d['suggested'] = manual_suggested_name
      if cell.getRow().isSelected():
        d['create_new'] = False
        create_cell = cell.getRow().getCell('create_new')
        obj = CheckBox(checked=False, tag=create_cell)
        obj.add_event_handler('change', select_row)
        create_cell.set_value(False)
        create_cell.set_value(obj)
        cell.getRow().deselect()
      print(f"Manual match: {vendor_name} -> {manual_suggested_name}")
      
    def format_suggested(cell, **params):
      suggested_value = cell.get_value()
      suggested_id = None      
      if suggested_value:
        suggested_vendor_obj = self.vendors.get_by_name(suggested_value)
        if suggested_vendor_obj is not None:
          suggested_id = suggested_vendor_obj['vendor_id']
        else:
          print(f"Issue looking up {suggested_value}!")
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
    self.vendor_table.set_sort('vendor_name', 'asc')

  def get_data(self):
    return self.vendor_table.data

  def check_vendor_table(self):
    vendor_map = self.vendor_table.data
    new_vendor_names = []
    reverse_map = {}
    vendor_aliases = []
    ready = { x['vendor_name']: (x['suggested'] is not None) or x['create_new'] for x in vendor_map }
    if not all(ready.values()):
      not_ready = [ k for k,v in ready.items() if not v ]
      alert(f"Cannot continue until these vendors have a valid option: {not_ready}!")
      # TODO: highlight rows with errors?
      ret = False
    else:
      new_vendor_names = [ x['vendor_name'] for x in vendor_map if x['create_new'] ]
      
      alias_map = {}
      reverse_map = {}
      for row in [ x for x in vendor_map if not x['create_new'] ]:
        suggested_vendor = self.vendors.get_by_name(row['suggested'])
        if suggested_vendor is None:
          print(f"ERROR: Cannot find vendor entry for: {row['suggested']}")
        else:
          alias_list = alias_map.get(suggested_vendor.vendor_id, [])
          alias_list.append(row['vendor_name'])
          alias_map[suggested_vendor.vendor_id] = alias_list
          reverse_map[row['vendor_name']] = suggested_vendor.vendor_name
        
      # Turn dict into records
      vendor_aliases = [ { 'vendor_id': vendor_id, 'synonyms': alias_list } for vendor_id, alias_list in alias_map.items() ]
      #print(f"Aliases: {self.vendor_aliases}")
      ret = True
    return (ret, new_vendor_names, reverse_map, vendor_aliases)
