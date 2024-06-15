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
    
    self.params = {
      'Budget': { 'background': '#ffffcc', 'color': 'black', 'editor': 'number' },
      'Forecast': { 'background': '#ffffcc', 'color': 'black', 'editor': 'number' },
      'Actual': { 'background': '#ffffcc', 'color': 'black', 'editor': None }
    }
    
    self.budget_lines_table.options = {
      "index": "transaction_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': True,
      'paginationSize': None,
      'frozenRows': 0,
      'height': '70vh',
      #'autoResize': False,
      #"pagination_size": 10,
    }

    self.show_empty = False
    self.selected_lines = []
    self.reload()
    self.add_event_handler("x-refresh-tables", self.refresh_tables)
    self.init_components(**properties)

  def reload(self):
    self.transactions.load(transaction_type=self.mode)
    budget_data = self.transactions.to_records(with_vendor_name=True, with_vendor=True)
    self.entry_lines = self.transactions.get_entry_lines(self.mode, self.budget_data)
    #print(self.entry_lines)
    self.year_months = self.entry_lines['columns']
    self.budget_data = []
    for row in budget_data:
      entry = self.entry_lines['data'].get(str(row['transaction_id']), None)
      for year_month in self.year_months:
        row[year_month] = entry[year_month] if entry else 'NA'
      row['total'] = sum(entry.values()) if entry else 0.0
      self.show_empty and self.budget_data.append(row)
  
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
    
    def format_entry(cell, **params):
      val = cell.getValue()
      if params.get('backgroundColor', None):
        cell.getElement().style.backgroundColor = params['backgroundColor']
      if params.get('color', None):
        cell.getElement().style.color = params['color']
      try:
        val = "{:,.0f}".format(val)
      except Exception:
        pass
      return val

    def format_total(cell, **params):
      val = cell.get_value()
      cell.getElement().style.backgroundColor = '#424140'
      cell.getElement().style.color = 'white'
      try:
        val = "{:,.0f}".format(val)
      except Exception:
        val = 'NA'
      return val
    
    columns = [
      {'title': '', 'field': 'delete', 'formatter': delete_formatter, 'formatterParams': {'key': 'transaction_id'}, 'width': 30 },
      {
        "title": "Owner",
        "field": "owner",
        'width': 150,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Team",
        "field": "team",
        'width': 100,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Vendor",
        "field": "vendor_name",
        'width': 200,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        'formatter': vendor_formatter
      },
      {
        "title": "Description",
        "field": "description",
        'width': 350,
        "headerFilter": "input",
        'formatter': link_formatter
      },
      {
        "title": "Lifecycle",
        "field": "lifecycle",
        'width': 150,        
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Category",
        "field": "category",
        'width': 150,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Account Code",
        "field": "account_code",
        'width': 150,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Cost Centre",
        "field": "cost_centre",
        'width': 150,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Service Change",
        "field": "service_change",
        'width': 150,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Business Contact",
        "field": "business_contact",
        'width': 150,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Project",
        "field": "project",
        'width': 150,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Review?", 
        "field": "to_review", 
        "formatter": "tickCross", 
        "width": 90,
        "headerFilter": "tickCross",
        "hozAlign": 'center',
        'editor': 'tickCross'
      },
    ]

    for c in self.year_months:
      columns.append({
        "title": c, 
        "field": c, 
        "formatter": format_entry, 
        "hozAlign": "right",
        "formatterParams": { 'backgroundColor': self.params[self.mode]['background'], 'color': self.params[self.mode]['color']},
        "width": 130,
        "headerFilter": "number",
        'editor': self.params[self.mode]['editor']
      })

    columns.append({
        "title": "Total", 
        "field": 'total', 
        "formatter": format_total, 
        "formatterParams": { 'backgroundColor': self.params[self.mode]['background'], 'color': self.params[self.mode]['color']},
        "width": 130,
        "headerFilter": "number",
        "hozAlign": 'right',
        'editor': None   
    })
    
    self.budget_lines_table.columns = columns
    self.budget_lines_table.data = self.budget_data


  def budget_lines_table_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    # TODO: fix to update Entries!
    data = dict(cell.getData())
    transaction = self.transactions.get(data["transaction_id"])
    transaction.update()
    transaction.save()


  def budget_lines_table_row_selection_changed(self, rows, data, **event_args):
    """This method is called when the row selection changes"""
    self.selected_vendors = rows
    if len(rows) == 1:
      pass
      # Set item in vendor details
    self.refresh_data_bindings()


  def add_new_vendors(self, new_vendors):
    vendor_ids = []
    for v_data in new_vendors:
      new_vendor = self.vendors.blank(v_data)
      try:
        new_vendor.save_as_new()
        self.vendors.add(new_vendor.vendor_id, new_vendor)
        vendor_ids.append(new_vendor.vendor_id)
      except ValueError as e:
        print("Vendor already exists - ignoring!")
        
    return vendor_ids

  def add_new_actual_lines(self, new_actual_lines):
    actual_line_ids = []
    for a_data in new_actual_lines:
      # Lookup vendor_id including if just created!
      vendor = self.vendors.get_by_name(a_data['vendor_name'])
      if vendor:
        a_data['vendor_id'] = vendor.vendor_id
        a_data.pop('vendor_name', None)
        new_trans = self.transactions.blank(a_data)
        new_trans = self.transactions.new(new_trans)
        actual_line_ids.append(new_trans.transaction_id)
      else:
        print(f"Error finding vendor records for Actual! {a_data}")
    return actual_line_ids
      
  def add_new_entries(self, new_entries):
    new_entries_count = 0
    for new_entry in new_entries:
      transaction = None

      # Look up transaction_id for newly created Actual Line
      if new_entry['transaction_desc'] is not None:
        filter = new_entry['transaction_desc']
        transactions = self.transactions.search(**filter)
        if len(transactions)==1:
          transaction = transactions[0]
          new_entry['transaction_id'] = transaction.transaction_id
      else:
        transaction = self.transactions.get(new_entry['transaction_id'])

      if transaction is not None:
        new_entry.pop('transaction_desc', None)
        transaction.add_entries([new_entry], overwrite=True)
        new_entries_count += 1
      else:
        print(f"Cannot find Actual Line for entry: {new_entry}")
        
    return new_entries_count
        
  def import_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    import_form = ImportActuals()
    ret = alert(import_form, title="Import Actuals", buttons=(("Import", True), ("Cancel", False)), large=True)
    if ret:
      new_vendors, new_actual_lines, new_entries = import_form.get_new_entries()
      vendor_ids = []
      actual_line_ids = []
      entry_count = 0
      
      if len(new_vendors)>0:
        #print(new_vendors)
        vendor_ids = self.add_new_vendors(new_vendors)

      if len(new_actual_lines)>0:
        #print(new_actual_lines)
        actual_line_ids = self.add_new_actual_lines(new_actual_lines)
        
      if len(new_entries)>0:
        print(new_entries)
        entry_count = self.add_new_entries(new_entries)

      Notification(f"Successful import! {len(vendor_ids)} new vendors, {len(actual_line_ids)} Actual Lines and {entry_count} new entries created").show()

  def new_year_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if confirm("This will lock the Budget, set the Forecast starting a new Current Year, and create a new starting Budget for next year. Do you want to continue?"):
      try:
        Data.start_new_year()
      except Exception as e:
        alert("Operation failed! Check logs!")
        self.refresh_data_bindings()

  def snapshot_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if confirm("This will create a snaphshot version of the current Budget. Do you want to contiunue?"):
      try:
        Data.create_new_snapshot()
      except Exception as e:
        alert("Operation failed! There may be too many snapshots! Check logs!")
        self.refresh_data_bindings()

  def show_empty_toggle_x_change(self, **event_args):
    """This method is called when the switch is toggled"""
    self.show_empty = self.show_empty_toggle.checked
    self.reload()
      

