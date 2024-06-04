from ._anvil_designer import BudgetLinesTemplate
from anvil import *
import anvil.users
import anvil.server

from datetime import datetime
from tabulator.Tabulator import row_selection_column

from ... import Data
from ...Data import VendorsModel, TransactionsModel


class BudgetLines(BudgetLinesTemplate):

  def __init__(self, **properties):
    self.vendors = VendorsModel.VENDORS
    self.transactions = TransactionsModel.TRANSACTIONS
    
    self.selected_lines = []

    self.add_event_handler("x-refresh-tables", self.refresh_tables)
    self.init_components(**properties)

  def reload(self):
    self.budget_data = self.transactions.load(transaction_type='Budget')

  def refresh_tables(self, *args, **kwargs):
    self.budget_lines_table_table_built()

  def budget_lines_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    
    self.vendors_table.columns = [
      row_selection_column,
      {
        "title": "Name",
        "field": "vendor_name",
        "formatter": self.name_formatter,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Description",
        "field": "description",
        "editor": "textarea",
        "headerFilter": "input",
      },
      {"title": "Active", "field": "active", "formatter": "tickCross", "width": 100},
    ]

    self.vendors_table.options = {
      "index": "vendor_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      "pagination_size": 10,
    }

    self.vendors_table.data = self.vendors.to_records()

  def name_formatter(self, cell, **params):
    cell_value = cell.getValue()

    def open_vendor(**event_args):
      sender = event_args["sender"]
      vendor_id = sender.text
      print("Opening vendor: {0}".format(vendor_id))
      self.vendor_detail.set_item(self.vendors.get(vendor_id))
      return

    link = Link(text=cell_value)
    link.set_event_handler("click", open_vendor)
    return link

  def budget_lines_table_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    data = dict(cell.getData())
    vendor = self.users.get(data["vendor_id"])
    vendor.update(data)
    vendor.save()

  def delete_vendor_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    num_vendors = len(self.selected_vendors)
    if confirm(f"About to delete {num_vendors} users! Are you sure?"):
      for row in self.selected_vendors:
        vendor = self.vendors.get(dict(row.getData())["email"])
        try:
          vendor.delete()
        except Exception as e:
          alert(
            f"Could not delete - perhaps there are still existing Entries for {vendor['vendor_name']}"
          )
      self.vendors.load()
      self.vendors_table_table_built()
      self.selected_vendors = []
      self.refresh_data_bindings()

  def budget_lines_table_row_selection_changed(self, rows, data, **event_args):
    """This method is called when the row selection changes"""
    self.selected_vendors = rows
    if len(rows) == 1:
      pass
      # Set item in vendor details
    self.refresh_data_bindings()
