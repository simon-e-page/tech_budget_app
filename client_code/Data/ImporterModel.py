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
  def parse(self, file_obj):
    try:
      #new_entries = anvil.server.call('Importer', 'import_file', CURRENT_BRAND, file_obj)
    except Exception as e:
      print("Error importing file!")
      raise
    return new_entries

  
  def check_brand(self, filename):
    match = re.search(FILENAME_PATTERNS[CURRENT_BRAND], filename)
    ret = False
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

      if year_month > actuals_to_date:
        ret = True
        
    else:
      print(f"Filename does not match expected pattern for {CURRENT_BRAND}!")

    return ret
    
  def get_import_ids(self, brand):
    return [] #anvil.server.call('get_import_ids', account_name)

IMPORTER = Importer()