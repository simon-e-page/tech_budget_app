from ._anvil_designer import VendorTemplate
from anvil import *

import datetime as dt

from .... import Data
from tabulator.Tabulator import row_selection_column

class Vendor(VendorTemplate):
  def __init__(self, **properties):
    #self.name_unique = False
    self.vendor_list = Data.VENDORS.get_dropdown()
    #self.finance_tags_raw = ''

    self.finance_columns = [
      row_selection_column,
      {'title': 'Synonym', 'field': 'finance_tag'},
      {'title': 'Delete', 'field': 'delete', 'formatter': self.delete_formatter, 'formatterParams': {'key': 'finance_tags'} }
    ]

    self.prior_year_columns = [
      row_selection_column,
      {'title': 'Synonym', 'field': 'prior_year_tag'},
      {'title': 'Delete', 'field': 'delete', 'formatter': self.delete_formatter, 'formatterParams': {'key': 'prior_year_tags'} }
    ]

    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.

  def delete_formatter(self, cell, **params):
    key = params['key']
    tag = cell.getData()[key]
    
    def delete_tag(**event_args):
      sender = event_args['sender']
      print("Deleting tag: {0} from {1}".format(sender.tag, key))
      self.item[key] = [ x for x in self.item[key] if x != sender.tag ]
      self.refresh_data_bindings()
      return

    link = Link(icon='fa:trash', tag=tag)
    link.set_event_handler('click', delete_tag)
    return link
   
  def set_item(self, item):
    self.item = item
    self.refresh_data_bindings()
  
  def get_icon(self, icon_id):
    return
    #return Data.get_icon(icon_id)

  def generate_finance_tags(self):
    return [ { 'finance_tag': x} for x in self.item.get('finance_tags', []) ]

  def generate_prior_year_tags(self):
    return [ { 'prior_year_tag': x} for x in self.item.get('prior_year_tags', []) ]

  def save_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Remap altered attributes back after possible editing 

    if not self.item.vendor_name:
      alert("Nothing to update!")
      return
          
    ret = None
    try:
      if self.item.vendor_id is not None:
        self.item.save()
      else:
        self.item.vendor_id = self.item.vendor_name
        ret = Data.VENDORS.new(self.item)
        if ret is not None:
          self.item = ret
        else:
          alert("There is already an existing Vendor with that name!")
    except Exception as e:
      alert("Error adding/updating vendor! Check logs!")

    self.refresh_data_bindings()
      

  
  def icon_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    timestamp = dt.datetime.now().strftime('%Y%m%d_%H%M')
    title = "{0}_icon_{1}.{2}".format(self.item['vendor_name'], timestamp, 'png')
    try:
      icon = Data.Icon(name=title, content=file, icon_id=None)
      Data.ICONS.add(icon.icon_id, icon)
      self.item['icon_id'] = icon.icon_id
      self.refresh_data_bindings()
    except Exception as e:    
      alert("Error uploading new icon!")
      icon = None
      self.item['icon_id'] = ''

  def add_finance_tag_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    new_synonym = self.finance_tag_dropdown.selected_value
    if new_synonym is not None:
      current = self.item.finance_tags
      current.append(new_synonym)
      self.item.finance_tags = list(set(current))
      self.finance_tag_dropdown.selected_value = None
      self.refresh_data_bindings()

  def add_prior_year_tag_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    new_synonym = self.prior_year_tag_dropdown.selected_value
    if new_synonym is not None:
      current = self.item.prior_year_tags
      current.append(new_synonym)
      self.item.prior_year_tags = list(set(current))
      self.prior_year_tag_dropdown.selected_value = None
      self.refresh_data_bindings()








