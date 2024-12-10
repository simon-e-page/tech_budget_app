import anvil.server
import anvil.users
import re

from .. import Data

MONTHS = {
  'JUL': 7,
  'AUG': 8,
  'SEP': 9,
  'OCT': 10,
  'NOV': 11,
  'DEC': 12,
  'JAN': 1,
  'FEB': 2,
  'MAR': 3,
  'APR': 4,
  'MAY': 5,
  'JUN': 6,  
}

#####################################################################
# PAYROLL IMPORTER
#####################################################################

class PayrollImporter:
  def parse(self, year_month, file_obj):
    try:
      new_data = anvil.server.call('PayrollImporter', 'parse', Data.CURRENT_BRAND, year_month, file_obj)
    except Exception as e:
      print("Error importing file!")
      print(e)
      raise
    return new_data


  def commit(self, year_month, new_positions, costs):
     return anvil.server.call('PayrollImporter', 'commit', Data.CURRENT_BRAND, year_month, new_positions, costs)

    
  def get_filename_patterns(self, brand=None):
    if brand is None:
      brand = Data.CURRENT_BRAND

    patterns = anvil.server.call('Importer', 'get_filename_patterns', brand=brand)
    return patterns
  
  def check_brand(self, filename):
    #year_month = anvil.server.call('PayrollImporter', 'check_filename_patterns', brand=Data.CURRENT_BRAND, filename=filename)
    if Data.CURRENT_BRAND == 'JB_AU':
      pattern = r'([A-Z]{3})(\d{2})!'
    match = re.search(pattern, filename)
    
    if match:
      month = match.group(1)
      year = int(match.group(2))
      month_num = MONTHS[month]
      year_month = (2000 + year) * 100 + month_num
    if year_month is None:
      print(f"Filename does not match expected pattern(s) for {Data.CURRENT_BRAND}!")
      year_month = None
    return year_month
    
    

  def get_import_months(self, fin_year = None, brand = None):
    if brand is None:
      brand = Data.CURRENT_BRAND
    if fin_year is None:
      fin_year = Data.CURRENT_YEAR
    return anvil.server.call("PayrollImporter", 'list_import_files', brand=brand, fin_year=fin_year)

  def get_import_file(self, year_month, brand = None):
    if brand is None:
      brand = Data.CURRENT_BRAND
    try:
      file_obj = anvil.server.call("PayrollImporter", 'get_import_file', brand=brand, year_month=year_month)
    except Exception:
      file_obj = None
      raise
    return file_obj

    
PAYROLL_IMPORTER = PayrollImporter()