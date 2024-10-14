from ._anvil_designer import ImportActualsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.media

import datetime as dt

from .... import Data
from ....Data import CURRENT_YEAR, ImporterModel, VendorsModel, CURRENT_BRAND, TransactionsModel

MONTH = []

def month_number_to_name(month_number):
    # Dictionary mapping month numbers to month names
    month_names = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }

    # Get the month name from the dictionary, return None if invalid number
    return month_names.get(month_number, "Invalid month number")

class ImportActuals(ImportActualsTemplate):
  def __init__(self, **properties):
    self.importer = ImporterModel.IMPORTER
    self.vendors = VendorsModel.VENDORS
    self.transactions = TransactionsModel.get_transactions()

    self.actuals_to_date = Data.get_actuals_updated(CURRENT_YEAR)
    import_months = self.importer.get_import_months(CURRENT_YEAR)
    self.download_months = [ (str(x), x) for x in import_months ]

    self.new_entries = []
    self.new_year_month = None
    self.fin_year = None
    self.month_total = 0
    self.cost_centres = []
    print(f"{self.actuals_to_date} vs {CURRENT_YEAR}")
    
    if self.actuals_to_date == CURRENT_YEAR * 100 + 6:
      self.next_month = 'Current year Actuals complete!'
    else:
      next_month = self.actuals_to_date + 1
      month_label = month_number_to_name(int(str(next_month)[4:]))
      year = str(next_month)[0:4]
      self.next_month = f"{month_label} {year}"

    self.imported_table.options = {
      'selectable': "highlight",
      'pagination': True,
      'pagination_size': 10,
      'css_class': ["table-striped", "table-bordered", "table-condensed"]
    }
      
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
  def get_year_month(self):
    if self.new_entries is None or len(self.new_entries)==0:
      return None, None
    else:
      return self.fin_year, self.new_year_month
      
  def get_new_entries(self):
    """ Returns new vendors, actual_lines and entries from import that need to be created """
    if self.new_entries is None or len(self.new_entries)==0:
      return [], [], []

    start = dt.datetime.now()
    
    new_vendors = []
    renamed_vendors = {}
    new_actual_lines = []
    new_entries = []
      
    year = int(str(self.new_year_month)[0:4])
    month = int(str(self.new_year_month)[4:])
    fin_year = year + int(month>6)
    self.fin_year = fin_year
    owner = anvil.users.get_user()['email']
    timestamp = dt.date(year, month, 1)
    
    for r in self.new_entries:
      print(f"Working on {r['vendor_name']}")
      
      if not r['existing_vendor']:
        if r['mapped_vendor'] is None:
          # Add new vendor
          new_vendors.append({
            'vendor_name': r['vendor_name'],
            'description': 'New Vendor from Finance System',
            'from_finance_system': True,
            'notes': f"Created by Finance Import in month: {self.new_year_month}"
          })
          vendor_id = None
        else:
          # Rename a different but existing vendor to the name provided by Finance
          renamed_vendors[r['mapped_vendor']] = r['vendor_name']
          vendor_id = self.vendors.get_by_name(r['mapped_vendor']).vendor_id
      else:
        vendor_id = r['vendor_id']
        
      vendor_name = r['vendor_name']
      
      for c in self.cost_centres:
        
        new_desc = f"Finance System Actuals - {c}"
        key = f"{vendor_name}_{new_desc}"

        # Only try and add Actuals for non-zero values
        if r.get(c, 0.0) != 0.0:
          new_actual_lines.append({
            'vendor_name': vendor_name,
            'vendor_id': vendor_id,
            'brand': CURRENT_BRAND,
            'description': new_desc,
            'owner': owner,
            'transaction_type': 'Actual',
            'cost_centre': c,
            'source': 'finance import',
            'account_code': 'Software Maintenance',
            'service_change': 'Organic growth',
            'lifecycle': 'New - Discretionary',
            'category': 'Operations',
            'import_id': str(self.new_year_month)
          })
          
          new_entries.append({
            'transaction_id': None,
            'transaction_type': 'Actual',
            'key': key,
            'timestamp': timestamp,
            'fin_year': fin_year,
            'year_month': self.new_year_month,
            'amount': r[c]
          })

    end = dt.datetime.now()
    dur = (end-start).seconds
    print(f"Got entries prepared in: {dur}s")
    
    return new_vendors, renamed_vendors, new_actual_lines, new_entries


  def file_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    year_month = self.importer.check_brand(file.name)
    process = False
    
    if year_month is not None:
      if year_month == self.actuals_to_date + 1:
        process = True
      elif year_month > self.actuals_to_date + 1:
        print(f"{year_month} > {self.actuals_to_date}??")
        alert(f"File is for for a non-consecutive future month! Please choose a file for {self.next_month}")
      elif year_month == self.actuals_to_date and confirm("Importing this file will overwrite existing records. Are you sure?"):
        process = True
      elif confirm(f"File is for a previous month. Proceeding will delete all months after {year_month}. Are you sure?"):
        process = True
        
    if process:
      try:
        new_data = self.importer.parse(year_month, file)
        self.new_entries = new_data['entries']
        self.cost_centres = new_data['cost_centres']
        self.new_year_month = new_data['year_month']
        self.month_total = new_data['month_total']
        self.render_table()
      except Exception as e:
        alert("Error importing file! Check logs!")
        print(e)
        
      #print(self.cost_centres)
    else:
      alert("Please choose another file!")

  
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
      { 
        'title': 'Map to',
        'field': 'mapped_vendor',
        'headerFilter': None,
        "editor": "list",
        'editorParams': {
          'valuesLookup': "active",
          'valuesLookupField': 'suggested_vendors',
          'clearable': True,
          'defaultValue': "",
          'emptyValue': None,
          'maxWidth': True,
          'allowEmpty': True,
        },
      },
      
    ]

    columns += [
      {
        'title': x,
        'field': x,
        'hozAlign': 'right',
        'formatter': 'money',
        'formatterParams': { 'precision': 0 }
      } for x in self.cost_centres
    ]

    columns += [
      {
        'title': 'Total',
        'field': 'total',
        'hozAlign': 'right',
        'formatter': 'money',
        'formatterParams': { 'precision': 0 }
      }
    ]

    
    self.imported_table.columns = columns
    self.imported_table.data = self.new_entries
    self.label_panel.visible = True
    self.imported_table.visible = True
    self.refresh_data_bindings()

  def delete_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if confirm("This will delete the current month Actuals! Are you sure?"):
      pass

  def download_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    year_month = self.download_dropdown.selected_value
    media_object = self.importer.get_import_file(year_month)
    if media_object is not None:
      #filename = file_info['filename']
      #content = file_info('excel_file')
      #content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      #media_object = anvil.BlobMedia(content_type=content_type, content=content, name=filename)
      anvil.media.download(media_object)

  def download_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.download_dropdown.selected_value is not None:
      self.download_button.enabled = True
    else:
      self.download_button.enabled = False

  
  def run_import(self):
    ret = alert(self, title="Import Actuals", buttons=(("Import", True), ("Cancel", False)), large=True)
    if ret:
      new_vendors, renamed_vendors, new_actual_lines, new_entries = self.get_new_entries()
      fin_year, year_month = self.get_year_month()

      vendor_ids = []
      actual_line_ids = []
      entry_count = 0
      
      if len(new_vendors)>0:
        #print(new_vendors)
        vendor_ids = self.add_new_vendors(new_vendors)

      if len(renamed_vendors)>0:
        renamed = self.rename_vendors(renamed_vendors)
      else:
        renamed = 0
        
      if len(new_actual_lines)>0:
        #print(new_actual_lines)
        actual_line_ids = self.add_new_actual_lines(new_actual_lines)
        
      if len(new_entries)>0:
        print(new_entries)
        self.transactions.delete_entries(year_month=year_month)
        entry_count = self.add_new_entries(new_entries)

      if len(vendor_ids)>0 or len(actual_line_ids)>0 or entry_count>0:
        fin_year, year_month = self.get_year_month()
        if fin_year is not None and year_month is not None:
          Data.actuals_updated(year=fin_year, year_month=year_month)

      return (True, len(vendor_ids), renamed, len(actual_line_ids), entry_count)
    else:
      return (False, 0, 0, 0, 0)

  
  def add_new_vendors(self, new_vendors):
    print(f"Adding {len(new_vendors)} vendors")
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
    count = self.transactions.search_and_add_entries(entries=new_entries, overwrite=True)        
    return count

  def rename_vendors(self, renamed_vendors):
    for old_name, new_name in renamed_vendors:
      try:
        v = self.vendors.get_by_name(old_name)
        if v is not None:
          v.vendor_name = new_name
          v.save()
      except Exception:
        print(f"Error renaming vendor: {old_name} to {new_name}!")
        raise
