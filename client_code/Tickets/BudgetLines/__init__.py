from ._anvil_designer import BudgetLinesTemplate
from anvil import *
import anvil.users
import anvil.server

from datetime import datetime
from tabulator.Tabulator import row_selection_column

from ... import Data
from ...Data import VendorsModel, TransactionsModel
from ...Vendors.Vendors.Vendor import Vendor

class BudgetLines(BudgetLinesTemplate):

  def __init__(self, **properties):
    self.vendors = VendorsModel.VENDORS
    self.transactions = TransactionsModel.get_transactions()
    self.vendor_list = self.vendors.get_dropdown()
    self.account_codes = Data.ACCOUNT_CODES_DD
    self.cost_centres = Data.COST_CENTRES_DD
    self.lifecycles = Data.LIFECYCLES_DD
    self.categories = Data.CATEGORIES_DD
    self.service_changes = Data.SERVICE_CHANGES_DD
    self.billing_types = Data.BILLING_TYPES_DD
    
    self.selected_lines = []
    self.reload()
    self.add_event_handler("x-refresh-tables", self.refresh_tables)
    self.init_components(**properties)

  def reload(self):
    self.transactions.load(transaction_type='Budget')
    self.budget_data = self.transactions.to_records()

  def refresh_tables(self, *args, **kwargs):
    self.budget_lines_table_table_built()

  def budget_lines_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""

    def link_formatter(cell, **params):
      tag = dict(cell.getData())['transaction_id']
  
      def open_budgetline(sender, **event_args):
        transaction_id = sender.tag
        print("Opening transaction: {0}".format(transaction_id))
        homepage = get_open_form()
        item = self.transactions.get(transaction_id)
        homepage.open_transaction(item=item)
        return
  
      link = Link(text=cell.getValue(), tag=tag)
      link.set_event_handler("click", open_budgetline)
      return link

    def vendor_formatter(cell, **params):
      tag = cell.get_value()
  
      def open_vendor(sender, **event_args):
        vendor_id = sender.tag
        print("Opening vendor: {0}".format(vendor_id))
        vendor = self.vendors.get(sender.tag)
        ret = alert(Vendor(item=vendor, show_save=False), large=True, title="Edit Vendor", buttons=[ ('Save', True), ('Cancel', False) ])
        if ret:
          try:
            vendor.update()
          except Exception as e:
            print("Failed to update Vendor!")
        
        return
  
      link = Link(text=cell.getValue(), tag=tag)
      link.set_event_handler("click", open_vendor)
      return link
    
    
    self.budget_lines_table.columns = [
      row_selection_column,
      {
        "title": "Owner",
        "field": "owner",
        #"formatter": self.name_formatter,
        #'editor': 'list',
        #'editorParams': self.owners,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Vendor",
        "field": "vendor_id",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        'formatter': vendor_formatter
      },
      {
        "title": "Description",
        "field": "description",
        "headerFilter": "input",
        'formatter': link_formatter
      },
      {
        "title": "Lifecycle",
        "field": "lifecycle",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Category",
        "field": "category",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Account Code",
        "field": "account_code",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Cost Centre",
        "field": "cost_centre",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Service Change",
        "field": "service_change",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Business Contact",
        "field": "business_contact",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Project",
        "field": "project",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Active", 
        "field": "status", 
        "formatter": "tickCross", 
        'formatterParams': { 'allowTruthy': True }, 
        "width": 100
      },
      {
        "title": "Review?", 
        "field": "to_review", 
        "formatter": "tickCross", 
        "width": 100
      },
    ]

    self.budget_lines_table.options = {
      "index": "transaction_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      "pagination_size": 10,
    }

    self.budget_lines_table.data = self.budget_data


  def budget_lines_table_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    pass
    data = dict(cell.getData())
    vendor = self.users.get(data["transaction_id"])
    vendor.update(data)
    vendor.save()

  def delete_transaction_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    num_lines = len(self.selected_lines)
    if confirm(f"About to delete {num_lines} users! Are you sure?"):
      for row in self.selected_lines:
        transaction = self.transactions.get(dict(row.getData())["transaction_id"])
        try:
          transaction.delete()
        except Exception as e:
          alert(
            f"Could not delete - perhaps there are still existing Entries for {transaction['transaction_id']}"
          )
      self.vendors.load()
      self.budget_lines_table_table_built()
      self.selected_lines = []
      self.refresh_data_bindings()

  def budget_lines_table_row_selection_changed(self, rows, data, **event_args):
    """This method is called when the row selection changes"""
    self.selected_vendors = rows
    if len(rows) == 1:
      pass
      # Set item in vendor details
    self.refresh_data_bindings()
