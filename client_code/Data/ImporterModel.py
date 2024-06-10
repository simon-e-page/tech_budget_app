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
      #new_data = {
      #  'year_month': 202407,
      #  'month_total': 100000.0,
      #  'cost_centres': [ 'IT (6000)', 'Online (3121)'],
      #  'entries': [
      #    { 'vendor_name': 'Testing Vendor PLC Ltd', 'vendor_id': 1003, 'existing_vendor': True, 'IT (6000)': 500000.0, 'Online (3121)': 0.0, 'total': 500000.0 },
      #    { 'vendor_name': 'New Vendor', 'vendor_id': None, 'existing_vendor': False, 'IT (6000)': 0.0, 'Online (3121)': 500000.0, 'total': 500000.0 },
      #  ]
      #}
    except Exception as e:
      print("Error importing file!")
      raise
    return new_data

  
  def check_brand(self, filename):
    match = re.search(FILENAME_PATTERNS[CURRENT_BRAND], filename)
    ret = None
    actuals_to_date = None
    if match:
      month = match.group(1)  # The month is the first group in the pattern
      year = match.group(2)   # The year is the second group in the pattern
      month_num = MONTH_TO_NUMBER[month]
      year_month = (int(year) * 100) + MONTH_TO_NUMBER[month]
      fin_year = int(year) + int(month_num>6)

      actuals_to_date = get_actuals_updated(CURRENT_YEAR)
      if actuals_to_date is None:
        actuals_to_date = (CURRENT_YEAR - 1) * 100 + 6

      print(f"Selected file matches Brand {CURRENT_BRAND} and is for {year_month} in the {fin_year} financial year")
      print(f"Current year is {CURRENT_YEAR} and actuals have been imported up to {actuals_to_date}")

      #if year_month > actuals_to_date:
      ret = year_month
        
    else:
      print(f"Filename does not match expected pattern for {CURRENT_BRAND}!")

    return ret, actuals_to_date
    
  def get_import_ids(self, brand):
    return [] #anvil.server.call('get_import_ids', account_name)

IMPORTER = Importer()