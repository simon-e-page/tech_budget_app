from ._anvil_designer import VendorTemplate
from anvil import *

import datetime as dt

from .... import Data

class Vendor(VendorTemplate):
  def __init__(self, **properties):
    self.name_unique = False
    self.prior_year_tags_raw = ''
    self.finance_tags_raw = ''
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.

  def populate_textareas(self):
    self.finance_tags_areabox.text = '\n'.join(self.item.finance_tags)
    self.prior_year_areabox.text = '\n'.join(self.item.prior_year_tags)
 
  def set_item(self, item):
    self.item = item
    self.populate_textareas()
    self.refresh_data_bindings()
  
  def get_icon(self, icon_id):
    return
    #return Data.get_icon(icon_id)

  def save_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Remap altered attributes back after possible editing      
    l = self.finance_tags_raw.split('\n')
    self.item['finance_tags'] = l

    l = self.prior_year_tags_raw.split('\n')
    self.item['prior_year_tags'] = l
    
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
      alert("Error adding new vendor! Check logs!")

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

  def delete_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass







