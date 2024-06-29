from ._anvil_designer import VendorsTemplate
from anvil import *
import anvil.users
import anvil.server

from datetime import datetime
from tabulator.Tabulator import row_selection_column

from ... import Data
from ...Data import VendorsModel


class Vendors(VendorsTemplate):
  """This Form displays transaction and account information for a single transaction. It also allows you to edit the transaction being displayed.

  Keyword Arguments:
    item - a row from the 'Transaction' Data Table
    back - a dictionary containg the form to open and the filters to apply when back is clicked

  A copy of this row from the 'Transaction' table is initialised as self.transaction_copy in form_refreshing_data_bindings()
  """

  def __init__(self, **properties):
    self.vendors = VendorsModel.VENDORS
    self.selected_vendors = []

    self.add_event_handler("x-refresh-tables", self.refresh_tables)
    self.init_components(**properties)

  def refresh_tables(self, *args, **kwargs):
    current_page = self.vendors_table.get_page()
    self.vendors_table_table_built()
    self.vendors_table.set_page(current_page)


  def vendors_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
      
    self.vendors_table.columns = [
      row_selection_column,
      {
        "title": "Name", 
        "field": "vendor_name", 
        'formatter': self.name_formatter,
        'headerFilter': "input",
        'headerFilterFunc': 'starts'
      },
      {
        "title": "Description", 
        "field": "description", 
        "editor": "textarea",
        'headerFilter': "input"
      },
      {
        "title": "Active", 
        "field": "active", 
        'formatter': 'tickCross',
        'width': 100
      },      
    ]

    self.vendors_table.options = {
      "index": "vendor_id",  # or set the index property here
      "selectable": "highlight",
      'css_class': ["table-striped", "table-bordered", "table-condensed"],
      'pagination_size': 10
    }

    self.vendors_table.data = self.vendors.to_records()

  def name_formatter(self, cell, **params):
    vendor_id = cell.getData()['vendor_id']
    
    def open_vendor(sender, **event_args):
      vendor_id = sender.tag
      print("Opening vendor: {0}".format(vendor_id))
      self.vendor_detail.set_item(self.vendors.get(vendor_id))
      return

    link = Link(text=cell.get_value(), tag=vendor_id)
    link.set_event_handler('click', open_vendor)
    return link


  
  def vendors_table_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    data = dict(cell.getData())
    vendor = self.vendors.get(data["vendor_id"])
    vendor.update(data)
    vendor.save()


  def delete_vendor_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    num_vendors = len(self.selected_vendors)
    if confirm(f"About to delete {num_vendors} users! Are you sure?"):
      for row in self.selected_vendors:
        vendor = self.vendors.get(dict(row.getData())["vendor_id"])
        try:
          vendor.delete()
        except Exception as e:
          alert(f"Could not delete - perhaps there are still existing Entries for {vendor['vendor_name']}")
      self.vendors.load()
      self.vendors_table_table_built()
      self.selected_vendors = []
      self.refresh_data_bindings()

  def vendors_table_row_selection_changed(self, rows, data, **event_args):
    """This method is called when the row selection changes"""
    self.selected_vendors = rows
    if len(rows)==1:
      pass
      # Set item in vendor details
    self.refresh_data_bindings()

