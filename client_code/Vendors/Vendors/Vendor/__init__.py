from ._anvil_designer import VendorTemplate
from anvil import *

import datetime as dt

from ....Data import IconsModel, VendorsModel, ACCEPTABLE_IMAGES

from tabulator.Tabulator import row_selection_column

class Vendor(VendorTemplate):
  def __init__(self, **properties):
    #self.name_unique = False
    self.show_save = properties.get('show_save', True)
    self.icons = IconsModel.ICONS
    self.vendors = VendorsModel.VENDORS
    self.vendor_list = self.vendors.get_dropdown()
    self.finance_vendor_list = self.vendors.get_dropdown(finance_field=True)

    self.finance_columns = [
      {'title': 'Synonym', 'field': 'finance_tags', 'width': 400, 'formatter': self.name_formatter  },
      {'title': 'Delete', 'field': 'delete', 'formatter': self.delete_formatter, 'formatterParams': {'key': 'finance_tags'} }
    ]

    self.prior_year_columns = [
      {'title': 'Synonym', 'field': 'prior_year_tags', 'width': 400, 'formatter': self.name_formatter },
      {'title': 'Delete', 'field': 'delete', 'formatter': self.delete_formatter, 'formatterParams': {'key': 'prior_year_tags'} }
    ]

    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.
  
  @property
  def finance_vendor_name(self):
    if self.item['finance_vendor']:
      self.item['finance_vendor'].vendor_name
    else:
      return None

  @finance_vendor_name.setter
  def finance_vendor_name(self, vendor_id):
    self.item['finance_vendor'] = self.vendors.get(vendor_id)
    
  def get_icon(self, icon_id):
    if icon_id:
      return self.icons.get_content(icon_id)

  def name_formatter(self, cell, **params):
    vendor_id = cell.get_value()
    return self.vendors.get(vendor_id)['vendor_name']
    
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
  
  def generate_tags(self, key):
    return [ { key: x} for x in self.item.get(key, []) ]
    
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
        ret = self.vendors.new(self.item)
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
    ext = ACCEPTABLE_IMAGES.get(file.content_type, None)
    if ext is None:
      alert("Unacceptable file type! Try again!")
    else:
      icon_id = "{0}_icon_{1}.{2}".format(self.item['vendor_name'], timestamp, ext)
    try:
      icon = self.icons.new(icon_id=icon_id, content=file)
      icon.save()
      self.item['icon_id'] = icon_id
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

  def vendor_url_edit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    placeholder = self.item['vendor_url'] or "Enter URL"
    new_url_textbox = TextBox(placeholder=placeholder, type='url')
    alert(content=new_url_textbox,
          title="Enter the website address for this vendor")
    new_url = new_url_textbox.text
    
    if new_url:
      self.item['vendor_url'] = new_url
      self.refresh_data_bindings()









