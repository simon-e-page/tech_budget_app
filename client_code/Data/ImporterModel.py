import anvil.server
import anvil.users
import re

from .. import Data
from ..Data import get_actuals_updated, actuals_updated

#####################################################################
# IMPORTER
#####################################################################

class Importer:
  def parse(self, year_month, file_obj):
    try:
      new_data = anvil.server.call('Importer', 'parse', Data.CURRENT_BRAND, year_month, file_obj)
    except Exception as e:
      print("Error importing file!")
      print(e)
      raise
    return new_data

  def process(self, year_month, new_data):
     return anvil.server.call('Importer', 'process', brand=Data.CURRENT_BRAND, year_month=year_month, new_data=new_data)

  def commit(self, year_month, new_vendor_names, vendor_aliases, transactions_with_entries, defaults):
     return anvil.server.call('Importer', 'commit', Data.CURRENT_BRAND, year_month, new_vendor_names, vendor_aliases, transactions_with_entries, defaults)

  def commit_background(self, year_month, new_vendor_names, vendor_aliases, transactions_with_entries, defaults):
    defaults['updated_by'] = anvil.users.get_user()['email']
    return anvil.server.call('Importer_launcher', '_background_commit', Data.CURRENT_BRAND, year_month, new_vendor_names, vendor_aliases, transactions_with_entries, defaults)
    
  def get_filename_patterns(self, brand=None):
    if brand is None:
      brand = Data.CURRENT_BRAND

    patterns = anvil.server.call('Importer', 'get_filename_patterns', brand=brand)
    return patterns
  
  def check_brand(self, filename):
    year_month = anvil.server.call('Importer', 'check_filename_patterns', brand=Data.CURRENT_BRAND, filename=filename)
    if year_month is None:
      print(f"Filename does not match expected pattern(s) for {Data.CURRENT_BRAND}!")
    return year_month
    
    
  def get_import_ids(self, brand):
    return [] #anvil.server.call('get_import_ids', account_name)

  def get_import_months(self, fin_year = None, brand = None):
    if brand is None:
      brand = Data.CURRENT_BRAND
    if fin_year is None:
      fin_year = Data.CURRENT_YEAR
    return anvil.server.call("Importer", 'list_import_files', brand=brand, fin_year=fin_year)

  def get_import_file(self, year_month, brand = None):
    if brand is None:
      brand = Data.CURRENT_BRAND
    try:
      file_obj = anvil.server.call("Importer", 'get_import_file', brand=brand, year_month=year_month)
    except Exception:
      file_obj = None
      raise
    return file_obj

  def brand_import_data(self, brand, fin_year, excel_file):
    return anvil.server.call('Importer', 'brand_import_data', brand=brand, fin_year=fin_year, file=excel_file)

  def import_first_budget(self, fin_year, new_vendor_names, vendor_aliases, transactions_with_entries, defaults):
    return anvil.server.call('Importer', 'import_first_budget', fin_year=fin_year, new_vendor_names=new_vendor_names, vendor_aliases=vendor_aliases, transactions_with_entries=transactions_with_entries, defaults=defaults)
    #return True
    
IMPORTER = Importer()