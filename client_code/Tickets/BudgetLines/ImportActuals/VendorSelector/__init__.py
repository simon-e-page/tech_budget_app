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

    def reformat_table():
      page = self.vendor_table.get_page()
      self.build_vendor_table(self.vendor_table.data)
      self.vendor_table.set_page(page)
      
    def match_selected(sender, **event_args):
      cell = sender.tag
      d = cell.get_data()
      vendor_name = d['vendor_name']
      existing_vendor_id = sender.selected_value
      if existing_vendor_id:
        manual_suggested_name = self.vendors.get(existing_vendor_id)['vendor_name']        
        d['suggested'] = manual_suggested_name
        d['create_new'] = False
        d['combine_with'] = None
        reformat_table()
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
      obj = DropDown(items=vendor_list, include_placeholder=True, placeholder="Select Existing..", tag=cell, selected_value=suggested_id)
      obj.add_event_handler('change', match_selected)
      return obj

    def select_create_new(sender, **event_args):
      cell = sender.tag
      if sender.checked:
        d = cell.get_data()
        d['create_new'] = True
        d['suggested'] = None
        d['combine_with'] = None
        reformat_table()

    def format_create_new(cell, **params):
      val = cell.get_value()
      if val:
        cell.getRow().select()
      else:
        cell.getRow().deselect()
      obj = CheckBox(checked=val, tag=cell)
      obj.add_event_handler('change', select_create_new)
      return obj

    def get_new():
      data = self.vendor_table.data
      items = sorted([ x['vendor_name'] for x in data if x['create_new'] ])
      return items
      
    def change_combine(sender, **event_args):
      cell = sender.tag
      data = cell.get_data()
      combined = sender.selected_value
      if combined:
        data['combine_with'] = combined
        data['suggested'] = None
        data['create_new'] = False
        reformat_table()

    
    def format_combine(cell, **params):
      combine_value = cell.get_value()
      items = get_new()
      if combine_value not in items:
        combine_value = None
        cell.get_data()['combine_with'] = None
      obj = DropDown(items=items, include_placeholder=True, placeholder="Combine with..", tag=cell, selected_value=combine_value)
      obj.add_event_handler('change', change_combine)
      return obj
    
    
    columns = [
      {
        'title': 'New Vendor Name',
        'field': 'vendor_name',
        'width': 200,
        'headerSort': False
      }, 
      {
        'title': 'Suggested Existing',
        'field': 'suggested',
        'headerSort': False,
        'width': 200,
        'formatter': format_suggested,
      }, 
      {
        'title': 'Combine with New',
        'field': 'combine_with',
        'headerSort': False,
        'width': 200,
        'formatter': format_combine,
      }, 
      {
        "title": "Create New Vendor",
        "field": "create_new",
        "formatter": format_create_new,
        "width": 150,
        "hoz_align": "center",
        "header_hoz_align": "center",
        "header_sort": False,
      },

    ]

    self.vendor_table.columns = columns
    self.vendor_table.data = data
    self.vendor_table.set_sort('vendor_name', 'asc')

  def get_data(self):
    return self.vendor_table.data

  def check_vendor_table(self):
    data = self.vendor_table.data
    new_vendor_names = []
    reverse_map = {}
    vendor_aliases = []
    ready = { x['vendor_name']: (x['suggested'] is not None) or x['create_new'] for x in data }
    if not all(ready.values()):
      not_ready = [ k for k,v in ready.items() if not v ]
      alert(f"Cannot continue until these vendors have a valid option: {not_ready}!")
      # TODO: highlight rows with errors?
      ret = False
    else:
      new_vendor_names = [ x['vendor_name'] for x in data if x['create_new'] ]
      
      alias_map = {}
      reverse_map = {}
      for row in [ x for x in data if not x['create_new'] ]:
        if row['combine_with'] is not None:
          suggested_vendor_name = row['combine_with']
        else:
          suggested_vendor_name = row['suggested']
        alias_list = alias_map.get(suggested_vendor_name, [])
        alias_list.append(row['vendor_name'])
        alias_map[suggested_vendor_name] = alias_list
        reverse_map[row['vendor_name']] = suggested_vendor_name
        
      # Turn dict into records
      vendor_aliases = [ { 'vendor_name': vendor_name, 'synonyms': alias_list } for vendor_name, alias_list in alias_map.items() ]
      #print(f"Aliases: {self.vendor_aliases}")
      ret = True
    return (ret, new_vendor_names, reverse_map, vendor_aliases)
