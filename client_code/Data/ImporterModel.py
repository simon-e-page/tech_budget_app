import anvil.server
import anvil.users
import re

from ..Data import CURRENT_BRAND, CURRENT_YEAR, get_actuals_updated, actuals_updated

#####################################################################
# IMPORTER
#####################################################################
MONTH_TO_NUMBER = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

# Examp

FILENAME_PATTERNS = {
  r"FY\d\d IT Spend - \b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b.xlsx": 'JB_AU',
  r"FY\d\d IT Spend - \b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b.xlsx": 'JB_AU',
}

class Importer:
  def parse(self, year_month, file_obj):
    try:
      new_data = anvil.server.call('Importer', 'parse', CURRENT_BRAND, year_month, file_obj)
    except Exception as e:
      print("Error importing file!")
      print(e)
      raise
    return new_data

  def get_filename_patterns(self, brand=None):
    if brand is None:
      brand = CURRENT_BRAND

    patterns = anvil.server.call('Importer', 'get_filename_patterns', brand=brand)
    return patterns
  
  def check_brand(self, filename):
    patterns = self.get_filename_patterns()
    #patterns = [ pattern for pattern,brand in self.get_filename_patterns() if brand == CURRENT_BRAND ]
    match = False
    ret = None
    
    for pattern in patterns:
      match = re.search(pattern, filename)
      if match:
        month = match.group(1)[0:3]  # The month is the first group in the pattern - shorten to first three characters
        year = match.group(2)   # The year is the second group in the pattern
        month_num = MONTH_TO_NUMBER[month]
        year_month = (int(year) * 100) + MONTH_TO_NUMBER[month]
        fin_year = int(year) + int(month_num>6)
        print(f"Selected file matches Brand {CURRENT_BRAND} and is for {year_month} in the {fin_year} financial year")
        ret = year_month
        break
        
    if not match:
      print(f"Filename does not match expected pattern(s) for {CURRENT_BRAND}!")

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

  def brand_import_data(self, brand, fin_year, excel_file):
    return anvil.server.call('Importer', 'brand_import_data', brand=brand, fin_year=fin_year, file=excel_file)

  def import_first_budget(self, fin_year, new_vendor_names, vendor_aliases, transactions_with_entries, defaults):
    return anvil.server.call('Importer', 'import_first_budget', fin_year=fin_year, new_vendor_names=new_vendor_names, vendor_aliases=vendor_aliases, transactions_with_entries=transactions_with_entries, defaults=defaults)
    #return True
    
IMPORTER = Importer()