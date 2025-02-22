from ._anvil_designer import VendorTemplate
from anvil import *

import datetime as dt

from .... import Data
from ....Data import IconsModel, VendorsModel, TransactionsModel
from ....Data.BaseModel import ACCEPTABLE_IMAGES
from ....Tickets.Transaction.VendorDetailTable import VendorDetailTable
from ....Tickets.Transaction import Transaction

from tabulator.Tabulator import row_selection_column

class Vendor(VendorTemplate):
  def __init__(self, caller, **properties):
    #self.name_unique = False
    self.show_save = True
    self.caller = caller
    self.icons = IconsModel.ICONS
    self.year = Data.get_year()
    self.vendors = VendorsModel.VENDORS
    self.transactions = TransactionsModel.get_transactions()
    
    self.vendor_list = self.vendors.get_dropdown()
    vendor_name = properties['item'].get('vendor_name', None)
    if vendor_name:
      vendor_name = [vendor_name]
    else:
      vendor_name = None

    self.synonym_columns = [
      {'title': 'Synonym', 'field': 'synonyms', 'width': 400, 'formatter': self.name_formatter },
      {'title': 'Delete', 'field': 'delete', 'formatter': self.delete_formatter, 'formatterParams': {'key': 'synonyms'} }
    ]

    self.add_event_handler('x-refresh-tables', self.refresh_tables)
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.

  
  def show(self, title=None, new=False):
    if title is None:
      title = "Vendor Details"
    self.save_button.text = "Add New" if new else "Save Changes"
    ret = alert(self, large=True, title=title, buttons=[('Close', False)])
    if ret:
      self.save(new=new)

  def refresh_tables(self, sender, **event_args):
    self.caller.raise_event('x-refresh-tables')
    
  def get_icon(self, icon_id):
    if icon_id:
      return self.icons.get_content(icon_id)

  def name_formatter(self, cell, **params):
    vendor_name = cell.get_value()
    return vendor_name
    
  def delete_formatter(self, cell, **params):
    key = params['key']
    tag = cell.getData()[key]
    
    def delete_tag(sender, **event_args):
      #sender = event_args['sender']
      print("Deleting synonym: {0} from {1}".format(sender.tag, key))
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
    self.raise_event('x-close-alert', value=True)      

  
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


  def add_synonym_tag_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    new_synonym = self.synonym_text.text
    if new_synonym is not None:
      if self.vendors.get_by_name(new_synonym) is not None:
        if not confirm(f"There is already a vendor with the name {new_synonym}. Adding this as a synonym will replace all instances and delete that vendor. Are you sure?"):
          return
      current = self.item.synonyms
      current.append(new_synonym)
      self.item.prior_year_tags = list(set(current))
      self.synonym_text.text = None
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
    def open_transaction(transaction_id):
      print(f"Got open for transaction ID: {transaction_id}")
      transaction = self.transactions.get(transaction_id)
      trans_form = Transaction(transaction)
      if transaction.vendor.vendor_id != self.item.vendor_id:
        other_vendor = self.vendors.get(transaction.vendor_id)
        print(f"Mismatching vendors! We are {self.item.vendor_name}. Transaction belongs to {other_vendor.vendor_name}")
      res = trans_form.show(f"Line Detail for {transaction.description}")

    vendor = self.item
    vendor_form = VendorDetailTable(mode='Actual', vendor=vendor, year=self.year, open_transaction=open_transaction)
    result = vendor_form.show()

  
  


  def save(self, new=False):
    if not self.item.vendor_name:
      alert("Nothing to update!")
      return

    if new:
      try:
        self.item.save_as_new()
        self.vendors.add(self.item.vendor_id, self.item)
        self.caller.raise_event('x-refresh-tables')
      except Exception as e:
        print(f"Error saving vendor! {e}")
        alert(f"Error saving vendor! {e}")
        
    else:
      try:
        self.item.save()
        self.caller.raise_event('x-refresh-tables')
      except Exception as e:
        print(f"Error saving vendor! {e}")
        alert(f"Error saving vendor! {e}")
       
      





