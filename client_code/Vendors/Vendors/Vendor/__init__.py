from ._anvil_designer import VendorTemplate
from anvil import *

import datetime as dt

from .... import Data
from ....Data import IconsModel, VendorsModel, ACCEPTABLE_IMAGES
from ....Tickets.Transaction.VendorDetailTable import VendorDetailTable

from tabulator.Tabulator import row_selection_column

class Vendor(VendorTemplate):
  def __init__(self, **properties):
    #self.name_unique = False
    self.show_save = properties.get('show_save', True)
    self.icons = IconsModel.ICONS
    self.year = Data.get_year()
    self.vendors = VendorsModel.VENDORS
    self.vendor_list = self.vendors.get_dropdown()
    vendor_name = properties['item'].get('vendor_name', None)
    if vendor_name:
      vendor_name = [vendor_name]
    else:
      vendor_name = None
    self.finance_vendor_list = self.vendors.get_dropdown(finance_field=True, exclude=vendor_name)

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
  
  #@property
  #def finance_vendor_name(self):
  #  if self.item['finance_vendor']:
  #    self.item['finance_vendor'].vendor_name
  #  else:
  #    return None

  #@finance_vendor_name.setter
  #def finance_vendor_name(self, vendor_id):
  #  self.item['finance_vendor'] = self.vendors.get(vendor_id)
    
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
    print(f'getting tags for {key}')
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
        ret = self.vendors.save_as_new(self.item)
        if ret is not None:
          self.item = ret
        else:
          alert("There is already an existing Vendor with that name!")
      self.parent.raise_event('x-refresh-tables')
    except Exception as e:
      alert("Error adding/updating vendor! Check logs!")
      raise

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

  def actuals_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    #homepage = get_open_form()
    #homepage.open_actuals(initial_filters={ 'vendor_name': self.item.vendor_name })
    vendor = self.item
    vendor_form = VendorDetailTable(mode='Actual', vendor=vendor, year=self.year)
    ret = alert(vendor_form, large=True, title=f"Entries for {vendor.vendor_name}", buttons=[ ('Save Changes', True), ('Cancel', False) ])
    if ret:
      entries = vendor_form.get_updated_entries()
      vendor_form.save_updated_entries(entries)
  
  def finance_tag_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.finance_tag_dropdown.selected_value is not None:
      finance_vendor = self.vendors.get(self.finance_tag_dropdown.selected_value)
    else:
      finance_vendor = None
    self.item['finance_vendor'] = finance_vendor
    


  def save(self, new=False):
    if new:
      try:
        self.item.save_as_new()
        self.vendors.add(self.item.vendor_id, self.item)
      except Exception as e:
        print(f"Error saving vendor! {e}")
        alert(f"Error saving vendor! {e}")
        
    else:
      try:
        self.item.save()
      except Exception as e:
        print(f"Error saving vendor! {e}")
        alert(f"Error saving vendor! {e}")
       
      






