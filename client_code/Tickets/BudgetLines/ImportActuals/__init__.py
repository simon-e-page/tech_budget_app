from ._anvil_designer import ImportActualsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.media

import datetime as dt

from .... import Data
from ....Data import ImporterModel, VendorsModel, TransactionsModel
from .ProgressForm import ProgressForm

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

    self.actuals_to_date = Data.get_actuals_updated(Data.CURRENT_YEAR)
    import_months = self.importer.get_import_months(Data.CURRENT_YEAR)
    self.download_months = [ (str(x), x) for x in import_months ]

    self.new_entries = []
    self.new_year_month = None
    self.fin_year = None
    self.month_total = 0.0
    self.import_total = 0.0
    self.cost_centres = []
    self.transactions_with_entries = []
    self.new_data = {}
    print(f"{self.actuals_to_date} vs {Data.CURRENT_YEAR}")
    
    if self.actuals_to_date == Data.CURRENT_YEAR * 100 + 6:
      self.next_month = 'Current year Actuals complete!'
    else:
      actuals_month = self.actuals_to_date % 100
      actuals_year = int(self.actuals_to_date / 100)
      if actuals_month == 12:
        month_label = month_number_to_name(1)
        year = str(actuals_year + 1)
        self.next_month_int = (actuals_year + 1) * 100 + 1
      else:
        month_label = month_number_to_name(actuals_month + 1)
        year = str(actuals_year)
        self.next_month_int = (actuals_year) * 100 + actuals_month + 1
      #month_label = month_number_to_name(int(str(next_month)[4:]))
      #year = str(next_month)[0:4]
      self.next_month = f"{month_label} {year}"

    self.import_panel.visible = False
    self.vendor_panel.visible = False
    self.final_panel.visible = False
      
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    
    # Any code you write here will run before the form opens.
  def get_year_month(self):
    if self.new_entries is None or len(self.new_entries)==0:
      return None, None
    else:
      return self.fin_year, self.new_year_month
      


  def file_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    year_month = self.importer.check_brand(file.name)
    process = False
    
    if year_month is not None:
      if year_month == self.next_month_int:
        process = True
      elif year_month > self.next_month_int:
        print(f"{year_month} > {self.actuals_to_date}??")
        alert(f"File is for for a non-consecutive future month! Please choose a file for {self.next_month}")
      elif year_month == self.actuals_to_date and confirm("Importing this file will overwrite existing records. Are you sure?"):
        process = True
      elif confirm(f"File is for a previous month. Proceeding will delete all months after {year_month}. Are you sure?"):
        process = True
        
    if process:
      #try:
      new_data = self.importer.parse(year_month, file)
      try:
        self.new_data = new_data
        self.new_entries = new_data['entries']
        self.new_vendors = new_data['new_vendors']
        self.cost_centres = new_data['cost_centres']
        self.new_year_month = new_data['year_month']
        self.month_total = new_data['month_total']
        self.render_vendor_table()
      except Exception as e:
        alert("Error importing file! Check logs!")
        print(e)
        
      #print(self.cost_centres)
    else:
      alert("Please choose another file!")


  
  def render_vendor_table(self):
    self.vendor_selector.build_vendor_table(self.new_vendors)
    self.vendor_panel.visible = True
    self.prior_panel.visible = False
    self.select_panel.visible = False
    self.refresh_data_bindings()


  
  def render_transaction_review_table(self, vendor_map):
    fin_year, year_month = self.get_year_month()
    
    try:
      self.transactions_with_entries = self.importer.process(year_month, self.new_data)
    except ValueError as v_mesg:
      alert(v_mesg)
      return
    except Exception as e:
      alert("Import Error!")
      print(e)
      raise
      return
      
    self.transaction_review.import_data = self.transactions_with_entries
    self.import_total, num_of_lines = self.transaction_review.build_entry_table(vendor_map, year_month=year_month)
    self.import_panel.visible = True
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
    ret = alert(self, title="Import Actuals", buttons=[("Cancel", False)], large=True, dismissible=False)
    if ret:
      transactions_with_entries = self.transaction_review.get_final_import_data()
      fin_year, year_month = self.get_year_month()

      vendor_ids = len(self.new_vendor_names)
      actual_line_ids = len(transactions_with_entries)
      entry_count = 0
      renamed = len(self.vendor_aliases)

      ts = dt.datetime.now().strftime("%Y%m%d")
      filename = self.file_loader.file.name
      
      defaults = {
        'source': "actuals_import_{0}".format(ts),
        'description': "New vendor for {0}".format(Data.CURRENT_BRAND),
        'notes': "New vendor imported from {0} on {1}".format(filename, ts)
      }

      #print("Ready To Commit:")
      #print(f"New Vendors: {self.new_vendor_names}")
      #print(f"Synonyms: {self.vendor_aliases}")
      #print(f"Transaction lines & Entries: {transactions_with_entries}")

      if confirm(f"About to create {vendor_ids} new vendors, {renamed} new synonyms, {actual_line_ids} new Actual Lines/Entries for {year_month}. Ready?"):
        #entry_count = self.importer.commit(year_month, self.new_vendor_names, self.vendor_aliases, transactions_with_entries, defaults)
        progress = ProgressForm()
        progress.initiate(1, len(transactions_with_entries), 1)
        result = progress.begin(self.importer.commit_background, year_month, self.new_vendor_names, self.vendor_aliases, transactions_with_entries, defaults)
        print(f"Progress result: {result}")
        entry_count = result
      return ((entry_count>0), vendor_ids, renamed, actual_line_ids, entry_count)
    else:
      return (False, 0, 0, 0, 0)


  def to_import_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.new_vendors = self.vendor_selector.get_data()
    result, new_vendor_names, vendor_map, vendor_aliases = self.vendor_selector.check_vendor_table()

    # These are ready to submit to the final import
    self.new_vendor_names = new_vendor_names
    self.vendor_aliases = vendor_aliases

    if result:
      self.vendor_panel.visible = False
      self.new_data['new_vendors'] = self.new_vendors
      self.render_transaction_review_table(vendor_map=None)
      self.final_panel.visible = True
      #self.render_table(vendor_map)

  
  def back_to_vendor_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.import_panel.visible = False
    self.vendor_panel.visible = True
    self.final_panel.visible = False


  
  def back_to_select_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.vendor_panel.visible = False
    self.select_panel.visible = True
    self.prior_panel.visible = True
    self.file_loader.clear()

  
  def import_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.raise_event('x-close-alert', value=True)
      

