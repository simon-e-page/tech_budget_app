import anvil.server
import anvil.users
import re
import datetime as dt

"""This module collects global variables to be used throughout the app"""
"""
TODO:
"""

class FinancialNumber:
    def __init__(self, number):
        self.number = number

    def __format__(self, format_spec):
        if self.number < 0:
            return f'({format(abs(self.number), format_spec)})'
        else:
            return format(self.number, format_spec)


# TODO: Move into app_tables?
BRANDS = [ 'JB_AU', 'JB_NZ', 'TGG']
BRANDS_DD = [ (x,x) for x in BRANDS ]

ATTRIBUTE_NAMES = ['account_code', 'cost_centre', 'lifecycle', 'category', 'service_change', 'billing_type']
  
#ACCOUNT_CODES = [  'Software Maintenance', 'Hardware Maintenance', 'Consulting', 'Salary', 'Communications' ]
REFS = anvil.server.call('Reference', 'get_attributes', attribute_names=ATTRIBUTE_NAMES)
ACCOUNT_CODES = REFS['account_code']
ACCOUNT_CODES_DD = [ (x, x) for x in ACCOUNT_CODES ]

#COST_CENTRES = [ 'IT', 'Online', 'Stores', 'HR', 'Commercial', 'Legal', 'Finance', 'Supply Chain' ]
COST_CENTRES = REFS['cost_centre']
COST_CENTRES_DD = [ (x, x) for x in COST_CENTRES ]

#LIFECYCLES = [ 'Existing', 'Existing - Discretionary', 'New - Committed', 'New - Discretionary', 'Legacy', 'Peripherals', 'New - Ex-IT' ]
LIFECYCLES = REFS['lifecycle']
LIFECYCLES_DD = [ (x, x) for x in LIFECYCLES ]

#CATEGORIES = [ 'Operations', 'Network & Infrastructure', 'E-Commerce & Marketing', 'Cybersecurity', 'Finance & HR', 'Supply Chain', 'SaaS Consulting', 'Non-IT', 'Commercial', 'Microsoft', 'API platform' ]
CATEGORIES = REFS['category']
CATEGORIES_DD = [ (x,x) for x in CATEGORIES ]

#SERVICE_CHANGES = ['Organic growth', 'Strategic projects', 'Commercial', 'Decommissioning']
SERVICE_CHANGES = REFS['service_change']
SERVICE_CHANGES_DD = [ (x,x) for x in SERVICE_CHANGES ]

#BILLING_TYPES = [ 'Prepayments', 'Consumption' ]
BILLING_TYPES = REFS['billing_type']
BILLING_TYPES_DD = [ (x,x) for x in BILLING_TYPES ]


ACCEPTABLE_IMAGES = {'image/png': 'png', 'image/jpg': 'jpg', 'image/jpeg': 'jpeg'}

class AttributeToKey:
  _defaults = {}
  def __getitem__(self, key):
      try:
          return self.__getattribute__(key)
      except AttributeError:
          raise KeyError(str(key))

  def __setitem__(self, key, item):
      self.__setattr__(key, item)

  def get(self, key, default=None):
      try:
          return self.__getattribute__(key)
      except AttributeError:
          return default

  def to_dict(self):
    d = { x: self[x] for x in self._defaults }
    return d

  def update(self, new_data):
    for k,v in new_data.items():
      if self.get(k, None) is not None:
        self[k] = v

class AttributeToDict:
  def __getitem__(self, key):
    try:
      return self.__d__.get(key, None)
    except AttributeError:
      return None

  def __setitem__(self, key, item):
    self.__d__[key]=item

  def get(self, key, default=None):
    return self.__d__.get(key, None)
  
  def add(self, key, item):
    self.__d__[key]=item

  def keys(self):
    return self.__d__.keys()

  def values(self):
    return self.__d__.values()

  def items(self):
    return self.__d__.items()

  def to_dict(self):
    return self.__d__

  def __len__(self):
    return len(self.__d__)

  def get_dropdown(self):
    return [(x, x) for x in self.__d__.keys() ]

  def to_list(self):
    return list(self.values())

  def to_records(self):
    return [ x.to_dict() for x in self.values() ]



FIN_YEARS = None
CURRENT_YEAR = None
BUDGET_YEAR = None
CURRENT_BRAND = 'JB_AU'

def get_tracking_table(year):
  return anvil.server.call('Calendar', 'get_tracking_table', brand=CURRENT_BRAND, agg_column='vendor_name', year=year, keep_columns=['vendor_name', 'vendor_id'])

def get_tracking_table_background(year):
  # This signature kicks off a background process
  task = anvil.server.call('Calendar_launcher', '_background_get_tracking_table', brand=CURRENT_BRAND, agg_column='vendor_name', year=year, keep_columns=['vendor_name', 'vendor_id'])
  #print(task)
  return task

def get_vendor_detail(year, vendor_id, mode='Actual'):
  return anvil.server.call('Calendar', 'get_tracking_table', brand=CURRENT_BRAND, agg_column=None, year=year, keep_columns=['transaction_id'], vendor_id=vendor_id)

def get_budget_detail(year, mode='Actual'):
  return anvil.server.call('Calendar', 'get_tracking_table', brand=CURRENT_BRAND, agg_column=None, year=year, keep_columns=None)

def get_excel_table(year):
  return anvil.server.call('Calendar', 'get_excel_table', brand=CURRENT_BRAND, agg_column=None, year=year, keep_columns=None)
  
def refresh():
  global FIN_YEARS, CURRENT_YEAR, BUDGET_YEAR
  FIN_YEARS, BUDGET_YEAR, CURRENT_YEAR = anvil.server.call('Calendar', 'get_fin_years')
  print(f"Fin Years: {FIN_YEARS}, Budget Year: {BUDGET_YEAR}, Current Year: {CURRENT_YEAR}")
  #actuals_updated(202406, 2025)

def get_actuals_updated(year):
  return anvil.server.call('Calendar', 'get_actuals_updated', year=year)

def actuals_updated(year_month, year):
  return anvil.server.call('Calendar', 'actuals_updated', year_month=year_month, year=year)

def get_year():
  return CURRENT_YEAR

def get_brand():
  return CURRENT_BRAND
  
def move_year(diff=1):
  global CURRENT_YEAR
  next_year = CURRENT_YEAR + diff
  if next_year in FIN_YEARS:
    print(f"OK to change year to {next_year}")
    CURRENT_YEAR = next_year
  else:
    print(f"No data for {next_year}")


def create_forecast(year=None):
  if year is None:
    year = CURRENT_YEAR
  return anvil.server.call("Calendar", 'create_forecast', lock_budget=True, year=year)

def create_new_budget(year=None):
  if year is None:
    year = CURRENT_YEAR + 1
  return anvil.server.call("Calendar", 'create_new_budget', lock=True, year=year)
  
    
      
#####################################################################
# MISCELLANEOUS
#####################################################################

def record_login():
  user = anvil.users.get_user()
  email = user['email']
  try:
    anvil.server.call('Users', 'record_login', email)
  except Exception as e:
    print(f"Could not record login for {email}")
    
  
def gpt_set_account_data(account_name):
  return None #anvil.server.call('gpt_set_account_data', account_name=account_name)

def gpt_run(prompt):
  return None #anvil.server.call('gpt_run', prompt=prompt)

def get_attribute_names():
  return ATTRIBUTE_NAMES

def get_attributes(attribute_names, with_count=True):
  ret = anvil.server.call('Reference', 'get_attributes', attribute_names=attribute_names, with_count=with_count)
  #if with_count:
  #  # TODO: replace with server-side call
  #  ret = [ { 'value': x, 'used': True } for x in ret[attribute_names] ]
  return ret


def remove_attribute(attribute_name, attribute_value):
  return anvil.server.call('Reference', 'remove_attribute', attribute_name, attribute_value)


def assign_actual_dimensions(brand = None, year = None):
  if brand is None:
    brand = CURRENT_BRAND
  if year is None:
    year = CURRENT_YEAR

  return anvil.server.call('Calendar', 'assign_actual_dimensions', brand, year)

def apply_attribute_splits(vendor_name, forecast_ids, actual_ids, splits, year=None):
  if year is None:
    year = CURRENT_YEAR
  return anvil.server.call('Calendar', 'apply_attribute_splits', year, vendor_name, forecast_ids, actual_ids, splits)
  
## Create import config for JB_AU
def create_import_config():
  # TODO: do we need this anymore?
  COST_CENTRE_MAP: dict = {
          'SUPPORT - IT': 'IT',
          'ONLINE': 'Online',
          'SOLUTIONS': 'Commercial',
          'STORES': 'Stores',
          '(blank)': 'Other',
          'MARKETPLACE': 'Marketplace',
          'JB COMMERCIAL': 'Commercial',
          'NZ RECHARGE': 'IT'
      }
  VENDOR_COLUMN = "VENDOR"
  TOTAL_COLUMN = "Grand Total"
  FILENAME_PATTERNS = [
  r"FY\d\d IT Spend - \b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b.xlsx",
  r"FY\d\d IT Spend - \b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b.xlsx",    
  ]
  BRAND = 'JB_AU'
  
  ret = anvil.server.call("Importer", 'add_import_config', brand=BRAND, cost_centre_map=COST_CENTRE_MAP, vendor_column=VENDOR_COLUMN, total_column=TOTAL_COLUMN, filename_patterns=FILENAME_PATTERNS)
  if not ret:
    print("Failed to make initial import config!")

    
create_import_config()
refresh()
