from ._anvil_designer import BudgetLinesTemplate
from anvil import *
import anvil.users
import anvil.server

from datetime import datetime
from tabulator.Tabulator import row_selection_column

from ... import Data
from ...Data import VendorsModel, TransactionsModel
from ...Vendors.Vendors.Vendor import Vendor
from .ImportActuals import ImportActuals

class BudgetLines(BudgetLinesTemplate):

  def __init__(self, mode = 'Budget', **properties):
    self.mode = mode
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
    self.transactions.load(transaction_type=self.mode)
    self.budget_data = self.transactions.to_records(with_vendor_name=True, with_vendor=True)

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
      vendor = cell.getData()['vendor']
  
      def open_vendor(sender, **event_args):
        print("Opening vendor: {0}".format(sender.tag.vendor_name))
        ret = alert(Vendor(item=sender.tag, show_save=False), large=True, title="Vendor Details", buttons=[ ('Save Changes', True), ('Cancel', False) ])
        if ret:
          try:
            vendor.update()
          except Exception as e:
            print("Failed to update Vendor!")
        return

      link = Link(text=cell.get_value(), tag=vendor)
      link.set_event_handler("click", open_vendor)
      return link

    
    def delete_formatter(cell, **params):
      key = params['key']
      tag = cell.getData()[key]
      
      def delete_tag(sender, **event_args):
        print("Deleting transaction: {0} from {1}".format(sender.tag, key))
        item = self.transactions.get(sender.tag)
        if confirm(f"About to delete '{item.description}'! Are you sure?"):
          item.delete()
          self.reload()
          self.budget_lines_table_table_built()
          return
  
      link = Link(icon='fa:trash', tag=tag)
      link.set_event_handler('click', delete_tag)
      return link
    
    
    self.budget_lines_table.columns = [
      {'title': '', 'field': 'delete', 'formatter': delete_formatter, 'formatterParams': {'key': 'transaction_id'}, 'width': 30 },
      {
        "title": "Owner",
        "field": "owner",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Vendor",
        "field": "vendor_name",
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
        "title": "Review?", 
        "field": "to_review", 
        "formatter": "tickCross", 
        "width": 100,
        "headerFilter": "tickCross",
        "hozAlign": 'center',
        'editor': 'tickCross'
      },
    ]

    self.budget_lines_table.options = {
      "index": "transaction_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': False,
      #"pagination_size": 10,
    }

    self.budget_lines_table.data = self.budget_data


  def budget_lines_table_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    data = dict(cell.getData())
    transaction = self.transactions.get(data["transaction_id"])
    transaction.update(data)
    transaction.save()

  #def delete_transaction_button_click(self, **event_args):
  #  """This method is called when the button is clicked"""
  #  num_lines = len(self.selected_lines)
  #  if confirm(f"About to delete {num_lines} users! Are you sure?"):
  #    for row in self.selected_lines:
  #      transaction = self.transactions.get(dict(row.getData())["transaction_id"])
  #      try:
  #        transaction.delete()
  #      except Exception as e:
  #        alert(
  #          f"Could not delete - perhaps there are still existing Entries for {transaction['transaction_id']}"
  #        )
  #    self.vendors.load()
  #    self.budget_lines_table_table_built()
  #    self.selected_lines = []
  #    self.refresh_data_bindings()

  def budget_lines_table_row_selection_changed(self, rows, data, **event_args):
    """This method is called when the row selection changes"""
    self.selected_vendors = rows
    if len(rows) == 1:
      pass
      # Set item in vendor details
    self.refresh_data_bindings()

  def add_new_entries(self, new_entries):
    pass

  def add_new_vendors(self, new_vendors):
    vendor_ids = []
    for v_data in new_vendors:
      new_vendor = self.vendors.blank(v_data)
      new_vendor.save_as_new()
      vendor_ids.append(self.vendors.new(new_vendor))
    return vendor_ids

  def add_new_actual_lines(self, new_actual_lines):
    actual_line_ids = []
    for a_data in new_actual_lines:
      new_trans = self.transactions.blank(a_data)
      new_trans.save
    
  def import_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    import_form = ImportActuals()
    ret = alert(import_form, title="Import Actuals", buttons=(("Import", True), ("Cancel", False)), large=True)
    if ret:
      new_vendors, new_actual_lines, new_entries = import_form.get_new_entries()
      
      if len(new_vendors)>0:
        print(new_vendors)
        self.add_new_vendors(new_vendors)

      if len(new_actual_lines)>0:
        print(new_actual_lines)
        self.add_new_actual_lines(new_actual_lines)
        
      if len(new_entries)>0:
        print(new_entries)
        self.add_new_entries(new_entries)
      

