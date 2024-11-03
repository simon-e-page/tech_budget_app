from ._anvil_designer import BudgetLinesTemplate
from anvil import *
import anvil.users
import anvil.server

from datetime import datetime
from tabulator.Tabulator import row_selection_column

from ... import Data
from ...Data import VendorsModel, TransactionsModel
from ...Vendors.Vendors.Vendor import Vendor
from ..Transaction import Transaction
from .ImportActuals import ImportActuals

class BudgetLines(BudgetLinesTemplate):

  def __init__(self, mode = 'Budget', initial_filters={}, **properties):
    self.mode = mode
    self.year = properties.get('year', Data.get_year())
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
    print(f"Öpening {mode} for {self.year}")
    self.init_components(**properties)

  def reload(self):
    #self.transactions.load(transaction_type=self.mode)
    #self.loaded_data = self.transactions.to_records(with_vendor_name=True, with_vendor=True)
    #self.entry_lines = self.transactions.get_entry_lines(self.mode, self.loaded_data)
    transaction_type = "Actual" if self.mode == 'Actual' else 'Budget'
    d = Data.get_budget_detail(year = self.year, transaction_type=transaction_type)
    self.year_months = d["year_months"]
    self.transaction_types = d["transaction_types"]
    self.loaded_data = d["data"]
    
    #self.year_months = self.entry_lines['columns']
    
  
  def refresh_tables(self):
    def data_filter(data, **params):
      if len(self.data_filters)>0:
        found = all(data.get(field)==value for field, value in self.data_filters.items())
      else:
        found = True
      #print(f"{data['vendor_name']}: {non_zero}")
      return found

    # TODO: fix at backend..
    if self.mode == 'Budget':    
      for row in self.loaded_data:
        for c in self.year_months:
          row[c] = row[f"{c}B"]
        row['total'] = row['totalB']
    elif self.mode == 'Forecast':
      for row in self.loaded_data:
        for c in self.year_months:
          row[c] = row[f"{c}F"]
        row['total'] = row['totalF']
      
    self.budget_data = [ x for x in self.loaded_data if self.show_empty or not all(x[c]==0 for c in self.year_months) ]
    #for row in self.loaded_data:
      #entry = self.entry_lines['data'].get(str(row['transaction_id']), {})
      #for year_month in self.year_months:
      #    row[year_month] = entry.get(year_month, 0.0)
          
      #row['total'] = sum(entry.values()) if entry else 0.0
      #(entry or self.show_empty) and self.budget_data.append(row)
    self.refresh_data_bindings()
    self.budget_lines_table.set_filter(data_filter)
    self.render_table()
  
  def budget_lines_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    self.refresh_tables()

  
  def render_table(self):
    def link_formatter(cell, **params):
      tag = dict(cell.getData())['transaction_id']

      def open_transaction(sender, **event_args):
        transaction = self.transactions.get(sender.tag)
        print("Opening transaction: {0}".format(transaction.description))
        print(transaction.to_dict(with_vendor=True))
        trans_form = Transaction(item=transaction, show_save=False)
        trans_form.show(title='Transaction Details')
  
      link = Link(text=cell.getValue(), tag=tag)
      link.set_event_handler("click", open_transaction)
      return link

    
    def vendor_formatter(cell, **params):
      vendor_name = cell.get_value()
      vendor = self.vendors.get_by_name(vendor_name)
  
      def open_vendor(sender, **event_args):
        print("Opening vendor: {0}".format(sender.tag.vendor_name))
        vendor_form = Vendor(item=sender.tag, show_save=False)        
        if vendor_form.show(title=sender.tag.vendor_name):
          #ret = alert(, large=True, title="Vendor Details", buttons=[ ('Save Changes', True), ('Cancel', False) ])
            #vendor.update()
          self.reload()
          self.refresh_tables()
        return

      link = Link(text=vendor_name, tag=vendor)
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
      month = cell.getField()
      if self.mode == 'Actual':
        background_color = self.params[self.transaction_types[month]]['background']
        color = self.params[self.transaction_types[month]]['color']
      else:
        background_color = params.get('backgroundColor', "white")
        color = params.get('color', "black")

      cell.getElement().style.backgroundColor = background_color
      cell.getElement().style.color = color
          
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
        "formatterParams": { 'backgroundColor': self.params[self.mode]['background'], 'color': self.params[self.mode]['color'] },
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
    self.budget_lines_table.set_sort('vendor_name', 'asc')


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


  
  def import_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    import_form = ImportActuals()
    (success, num_vendor_ids, num_renamed, num_actual_line_ids, num_entries) = import_form.run_import()
    if success:
      alert(f"Successful import! {num_vendor_ids} new vendors, {num_renamed} existing vendors remapped, {num_actual_line_ids} Actual Lines and {num_entries} new entries created")


  def create_budget_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    ret = False
    if confirm("This will create a new starting Budget for next year. Do you want to continue?"):
      try:
        ret = Data.create_new_budget(year=self.year+1)
        if not ret:
          alert("Operation failed! Check logs!")
      except Exception as e:
        print(e)
        alert("Operation failed! Check logs!")
      if ret:
        Notification("New budget created successfully!").show()
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

  
  def create_forecast_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    ret = False
    if confirm(f"This will lock this Budget and create a forecast for {self.year}. Do you want to continue?"):
      try:
        ret = Data.create_forecast(year=self.year)
        if not ret:
          alert("Operation failed! Check logs!")
      except Exception as e:
        print(e)
        alert("Operation failed! Check logs!")
      if ret:
        Notification("New budget created successfully!").show()
      self.refresh_data_bindings()

  def add_new_forecast_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.add_new(transaction_type='Forecast')

  def add_new(self, transaction_type="Forecast"):
    new_trans = self.transactions.blank({'transaction_type': transaction_type})
    trans_form = Transaction(new_trans, transaction_type=transaction_type)
    if trans_form.show(new=True):
      Notification(f"Created new {transaction_type} Line!").show()

  def add_actual_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.add_new(transaction_type='Actual')

  def add_budget_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.add_new(transaction_type='Budget')
    

      

