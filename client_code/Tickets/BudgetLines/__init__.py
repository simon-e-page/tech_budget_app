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

  def __init__(self, mode = 'Budget', initial_filters={}, **properties):
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
    self.data_filters = initial_filters
    
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
    self.budget_data = []
    self.year_months = []
    self.reload()
    self.add_event_handler("x-refresh-tables", self.refresh_tables)
    self.init_components(**properties)

  def reload(self):
    self.transactions.load(transaction_type=self.mode)
    self.loaded_data = self.transactions.to_records(with_vendor_name=True, with_vendor=True)
    self.entry_lines = self.transactions.get_entry_lines(self.mode, self.loaded_data)
    self.year_months = self.entry_lines['columns']
    
  
  def refresh_tables(self):
    def data_filter(data, **params):
      if len(self.data_filters)>0:
        found = all(data.get(field)==value for field, value in self.data_filters.items())
      else:
        found = True
      #print(f"{data['vendor_name']}: {non_zero}")
      return found

    self.budget_data = []
    for row in self.loaded_data:
      entry = self.entry_lines['data'].get(str(row['transaction_id']), {})
      for year_month in self.year_months:
          row[year_month] = entry.get(year_month, 0.0)
          
      row['total'] = sum(entry.values()) if entry else 0.0
      (entry or self.show_empty) and self.budget_data.append(row)
    self.refresh_data_bindings()
    self.budget_lines_table.set_filter(data_filter)
    self.render_table()
  
  def budget_lines_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    self.refresh_tables()

  
  def render_table(self):
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
    print(f"Adding {len(new_vendors)} vendots")
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
    print(f"Adding up to {len(new_actual_lines)} actual lines")
    for a_data in new_actual_lines:
      # Lookup vendor_id including if just created!
      if a_data['vendor_id'] is None:
        vendor = self.vendors.get_by_name(a_data['vendor_name'])
        if vendor:
          a_data['vendor_id'] = vendor.vendor_id
        else:
          print(f"Error finding vendor records for Actual! {a_data}")
          
      a_data.pop('vendor_name', None)
    new_trans_ids = self.transactions.bulk_add(new_actual_lines, update=False)
    return new_trans_ids

  
  def add_new_entries(self, new_entries):
    print(f"Adding {len(new_entries)} new entries")

    new_entries_count = 0
    for trans in new_entries.values():
        count = self.transactions.search_and_add_entries(filter=trans['filter'], new_entries=trans['entries'], overwrite=True)
        if count is not None:
          new_entries_count += count
        
    return new_entries_count

  def delete_entries(self, new_entries, year_month):
    transaction_ids = [ x['transaction_id'] for x in new_entries ]
    transaction_ids = list(set(transaction_ids))
    for transaction_id in transaction_ids:
      self.transactions.delete_entries(transaction_id=transaction_id, year_month=year_month)
    
  def import_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    import_form = ImportActuals()
    ret = alert(import_form, title="Import Actuals", buttons=(("Import", True), ("Cancel", False)), large=True)
    if ret:
      new_vendors, new_actual_lines, new_entries = import_form.get_new_entries()
      fin_year, year_month = import_form.get_year_month()

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
        self.delete_entries(new_entries, year_month)
        entry_count = self.add_new_entries(new_entries)

      if len(vendor_ids)>0 or len(actual_line_ids)>0 or entry_count>0:
        fin_year, year_month = import_form.get_year_month()
        if fin_year is not None and year_month is not None:
          Data.actuals_updated(year=fin_year, year_month=year_month)
          
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
    print(self.show_empty_toggle.checked)
    print(event_args)
    self.show_empty = self.show_empty_toggle.checked
    self.refresh_tables()

  def clear_filter_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.data_filters = {}
    self.refresh_tables()
      

