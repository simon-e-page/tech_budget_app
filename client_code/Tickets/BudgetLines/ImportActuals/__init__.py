from ._anvil_designer import ImportActualsTemplate
from anvil import *
import anvil.server
import anvil.users

import datetime as dt

from .... import Data
from ....Data import CURRENT_YEAR, ImporterModel, VendorsModel, CURRENT_BRAND, TransactionsModel


class ImportActuals(ImportActualsTemplate):
  def __init__(self, **properties):
    self.next_month = Data.get_actuals_updated(CURRENT_YEAR)
    self.importer = ImporterModel.IMPORTER
    self.vendors = VendorsModel.VENDORS

    # Expected to have all 'Actual Lines' loaded
    self.transactions = TransactionsModel.get_transactions()

    self.new_entries = None
    self.new_year_month = None
    self.month_total = None
    self.cost_centres = None
    
    if self.next_month is None or self.next_month == 0:
      self.next_month = (CURRENT_YEAR - 1) * 100 + 7
      
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def get_new_entries(self):
    """ Returns new vendors, actual_lines and entries from import that need to be created """
    if self.new_entries is None or len(self.new_entries)==0:
      return [], [], []

    new_vendors = []
    new_actual_lines = []
    new_entries = []
      
    year = int(str(self.new_year_month)[0:4])
    month = int(str(self.new_year_month)[4:])
    fin_year = year + int(month>6)
    
    for r in self.new_entries:
      if not r['existing_vendor']:
        new_vendors.append({
          'vendor_name': r['vendor_name'],
          'description': 'New Vendor from Finance System',
          'from_finance_system': True,
          'notes': f"Created by Finance Import in month: {self.new_year_month}"
        })
        for c in self.cost_centres:
          new_desc = f"Finance System Actuals - {c}"
          filter = { 'brand': CURRENT_BRAND, 'vendor_name': r['vendor_name'], 'description': new_desc }
          existing_transaction = self.transactions.search(**filter)
          if len(existing_transaction)==0 and r[c]!=0.0:
            new_actual_lines.append({
              'vendor_name': r['vendor_name'],
              'brand': CURRENT_BRAND,
              'description': new_desc,
              'owner': anvil.users.get_user()['email'],
              'transaction_type': 'Actual',
              'cost_centre': c,
              'source': 'finance import',
              'import_id': str(self.new_year_month)
            })
            new_entries.append({
              'transaction_id': None,
              'transaction_desc': filter,
              'transaction_type': 'Actual',
              'timestamp': dt.date(year, month, 1),
              'fin_year': fin_year,
              'year_month': self.new_year_month,
              'amount': r[c]
            })
          elif len(existing_transaction)==1 and r[c]!=0.0:
            transaction_id = existing_transaction[0].transaction_id
            new_entries.append({
              'transaction_id': transaction_id,
              'transaction_desc': None,
              'transaction_type': 'Actual',
              'timestamp': dt.date(year, month, 1),
              'fin_year': fin_year,
              'year_month': self.new_year_month,
              'amount': r[c]
            })
          elif r[c]!=0.0:
            alert(f"Should not happen! Multiple Actual Lines found for {CURRENT_BRAND}, {r['vendor_name']}, {c}")
          else:
            print(f"Amount should equal zero: {r[c]}")
                  
    return new_vendors, new_actual_lines, new_entries


  def file_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    year_month, actuals_to_date = self.importer.check_brand(file.name)
    
    if year_month is not None:
      process = False
      if year_month == actuals_to_date + 1:
        process = True
      elif year_month > actuals_to_date + 1:
        alert("FIle is for for a non-consecutive future month which will leave a gap!")
        process = False
      elif year_month <= actuals_to_date and confirm("Importing this file will overwrite existing records. Are you sure?"):
        process = True

      if process:        
        new_data = self.importer.parse(year_month, file)
        self.new_entries = new_data['entries']
        self.cost_centres = new_data['cost_centres']
        self.new_year_month = new_data['year_month']
        self.month_total = new_data['month_total']
        self.render_table()

  
  def render_table(self):

    def vendor_formatter(cell, **params):
      data = cell.get_data()
      vendor_id = data['vendor_id']
      vendor_name = cell.get_value()
      if vendor_id is None:
        vendor_name = f"<b>*{vendor_name}*</b>"
      return vendor_name
    
    columns = [
      { 
        'title': 'Vendor',
        'field': 'vendor_name',
        'formatter': vendor_formatter,
        'headerFilter': 'input',
        "headerFilterFunc": "starts"        
      },
      { 
        'title': 'Existing',
        'field': 'existing_vendor',
        'formatter': 'tickCross',
        'headerFilter': 'tickCross',
        'width': 100
      },
      
    ]

    columns += [
      {
        'title': x,
        'field': x,
      } for x in self.cost_centres
    ]

    columns += [
      {
        'title': 'Total',
        'field': 'total'
      }
    ]

    self.imported_table.options.update(
      selectable="highlight",
      pagination=False,
      pagination_size=15,
      css_class=["table-striped", "table-bordered", "table-condensed"]
    )
    
    self.imported_table.columns = columns
    self.imported_table.data = self.new_entries
    self.label_panel.visible = True
    self.imported_table.visible = True
    self.refresh_data_bindings()
    
  
