import anvil.server
import anvil.users
import re

from ..Data import CURRENT_BRAND, CURRENT_YEAR, get_actuals_updated, actuals_updated

#####################################################################
# IMPORTER
#####################################################################
MONTH_TO_NUMBER = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

# Examp

FILENAME_PATTERNS = {
  'JB_AU': r"FY\d\d IT Spend - \b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b.xlsx"
}

class Importer:
  def parse(self, year_month, file_obj):
    try:
      new_data = anvil.server.call('Importer', 'parse', CURRENT_BRAND, year_month, file_obj)
    except Exception as e:
      print("Error importing file!")
      raise
    return new_data

  
  def check_brand(self, filename):
    match = re.search(FILENAME_PATTERNS[CURRENT_BRAND], filename)
    ret = None
    if match:
      month = match.group(1)  # The month is the first group in the pattern
      year = match.group(2)   # The year is the second group in the pattern
      month_num = MONTH_TO_NUMBER[month]
      year_month = (int(year) * 100) + MONTH_TO_NUMBER[month]
      fin_year = int(year) + int(month_num>6)
      print(f"Selected file matches Brand {CURRENT_BRAND} and is for {year_month} in the {fin_year} financial year")
      ret = year_month
        
    else:
      print(f"Filename does not match expected pattern for {CURRENT_BRAND}!")

    return ret
    
  def get_import_ids(self, brand):
    return [] #anvil.server.call('get_import_ids', account_name)

  def get_import_months(self, fin_year = None, brand = None):
    if brand is None:
      brand = CURRENT_BRAND
    if fin_year is None:
      fin_year = CURRENT_YEAR
    return anvil.server.call("Importer", 'list_import_files', brand=brand, fin_year=fin_year)

  def get_import_file(self, year_month, brand = None):
    if brand is None:
      brand = CURRENT_BRAND
    try:
      file_obj = anvil.server.call("Importer", 'get_import_file', brand=brand, year_month=year_month)
    except Exception:
      file_obj = None
      raise
    return file_obj
    
IMPORTER = Importer()