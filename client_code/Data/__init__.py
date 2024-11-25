import anvil.server
import anvil.users
import re
import datetime as dt

#from . import VendorsModel
#from . import UsersModel

"""This module collects global variables to be used throughout the app"""
"""
TODO:
"""



#def get_tracking_table(year):
#  return anvil.server.call('Calendar', 'get_tracking_table', brand=CURRENT_BRAND, agg_column='vendor_name', year=year, keep_columns=['vendor_name', 'vendor_id'])
def get_quarterly_table(year=None, quarter = 0):
  brand = CURRENT_BRAND
  if year is None:
    year = CURRENT_YEAR
  return anvil.server.call('Calendar', 'get_quarterly_table', brand, year, quarter)

def get_quarterly_table_excel(year=None, quarter=0):
  brand = CURRENT_BRAND
  if year is None:
    year = CURRENT_YEAR
  return anvil.server.call('Calendar', 'get_quarterly_table_excel', brand, year, quarter)
  
def get_tracking_table_background(year, refresh=False):
  # This signature kicks off a background process
  task = anvil.server.call('Calendar_launcher', 
                           'background_get_tracking_table', 
                           brand=CURRENT_BRAND, 
                           agg_column='vendor_name', 
                           year=year, 
                           keep_columns=['vendor_name', 'vendor_id', 'to_review'],
                           account_code=['Consulting', 'Hardware Maintenance', 'Software Maintenance'],
                          )
  #print(task)
  return task


def get_vendor_detail(year, vendor_id, mode='Actual'):
  return anvil.server.call('Calendar', 'get_tracking_table', brand=CURRENT_BRAND, agg_column=None, year=year, keep_columns=['transaction_id'], vendor_id=vendor_id)


def get_budget_detail(year, transaction_type=None, mode=None):
  return anvil.server.call('Calendar', 'get_tracking_table', brand=CURRENT_BRAND, agg_column=None, year=year, keep_columns=None, transaction_type=transaction_type)


def get_excel_table(year):
  return anvil.server.call('Calendar', 'get_excel_table', brand=CURRENT_BRAND, agg_column=None, year=year, keep_columns=None)


def refresh_cache():
  """Trigger the backend to reload everything from the database """
  global REFRESH_UI
  anvil.server.call('Calendar', 'refresh_cache')
  REFRESH_UI = True


def refresh(brand=None):
  global FIN_YEARS, CURRENT_YEAR, BUDGET_YEAR, CURRENT_BRAND
  if brand is None:
    if len(BRANDS)>0:
      CURRENT_BRAND = BRANDS[0]['code']
    else:
      CURRENT_BRAND = None
      print("No Brands are configured!")
      return
  else:
    CURRENT_BRAND = brand
    
  FIN_YEARS, BUDGET_YEAR, CURRENT_YEAR = anvil.server.call('Calendar', 'get_fin_years', CURRENT_BRAND)
  print(f"Fin Years: {FIN_YEARS}, Budget Year: {BUDGET_YEAR}, Current Year: {CURRENT_YEAR}")
  


def get_actuals_updated(year):
  return anvil.server.call('Calendar', 'get_actuals_updated', CURRENT_BRAND, year=year)

def actuals_updated(year_month, year):
  return anvil.server.call('Calendar', 'actuals_updated', CURRENT_BRAND, year_month=year_month, year=year)

def get_year():
  return CURRENT_YEAR

def get_brand():
  return CURRENT_BRAND

def create_brand(code, name):
  return anvil.server.call('Brands', 'add_brand', code=code, name=name)

def add_brand_icon(code, content):
  return anvil.server.call('Brands', 'add_icon', code=code, content=content)

def get_brand_icon(code):
  return anvil.server.call('Brands', 'get_icon', code=code)

def move_year(diff=1):
  global CURRENT_YEAR
  next_year = CURRENT_YEAR + diff
  if next_year in FIN_YEARS:
    print(f"OK to change year to {next_year}")
    CURRENT_YEAR = next_year
    return True
  else:
    print(f"No data for {next_year}")
    return False


def create_forecast(year=None):
  if year is None:
    year = CURRENT_YEAR
  try:
    ret = anvil.server.call("Calendar", 'create_forecast', CURRENT_BRAND, lock_budget=True, year=year)
    refresh_cache()
  except Exception as e:
    print(f"Error! {e}")
    ret = None
  return ret

def create_new_budget(year=None):
  if year is None:
    year = CURRENT_YEAR + 1
  try:
    ret = anvil.server.call("Calendar", 'create_new_budget', CURRENT_BRAND, year=year)
    refresh_cache()
  except Exception as e:
    print(f"Error! {e}")
    ret = None
  return ret

def is_locked(year):
  return anvil.server.call("Calendar", 'is_locked', CURRENT_BRAND, year=year)

def get_fin_years():
  fin_years, budget_year, current_year = anvil.server.call("Calendar", 'get_fin_years', CURRENT_BRAND)
  return fin_years
  
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
  return ret


def remove_attribute(attribute_name, attribute_value):
  ret = anvil.server.call('Reference', 'remove_attribute', attribute_name, attribute_value)
  refresh_cache()
  return ret


def assign_actual_dimensions(brand = None, year = None, selected_vendor_name=None):
  if brand is None:
    brand = CURRENT_BRAND
  if year is None:
    year = CURRENT_YEAR

  ret = anvil.server.call('Calendar', 'assign_actual_dimensions', brand, year, selected_vendor_name=selected_vendor_name)
  refresh_cache()
  return ret

def apply_attribute_splits(vendor_name, forecast_ids, actual_ids, splits, year=None):
  if year is None:
    year = CURRENT_YEAR
  try:
    ret = anvil.server.call('Calendar', 'apply_attribute_splits', year, vendor_name, forecast_ids, actual_ids, splits)
    refresh_cache()
  except Exception as e:
    print(f"Error: {e}")
    ret = False
  return ret




#def callback(callback_obj, callback_func):
#  #return anvil.server(callback_obj, callback_func)
#  global TEST_CALLBACK
#  TEST_CALLBACK += 1
#  return TEST_CALLBACK

#TEST_CALLBACK = 0


FIN_YEARS = None
CURRENT_YEAR = None
BUDGET_YEAR = None
CURRENT_BRAND = None
REFRESH_UI = False

TEMPLATE_URL = '"_/theme/budget_template_202411.xlsx"'
ATTRIBUTE_NAMES = ['account_code', 'cost_centre', 'lifecycle', 'category', 'service_change', 'billing_type']

initial_load = [
  { 'classname': 'Brands', 'methodname': 'get_brands', 'kwargs': {} },
  { 'classname': 'Reference', 'methodname': 'get_attributes', 'kwargs': { 'attribute_names': ATTRIBUTE_NAMES } },  
  { 'classname': 'Users', 'methodname': 'get_roles', 'kwargs': {} },
  { 'classname': 'Users', 'methodname': 'search', 'kwargs': {} },
  { 'classname': 'Vendors', 'methodname': 'get_vendors', 'kwargs': {} },
]


BRANDS, REFS, _roles, _users, _vendors = anvil.server.call('multi_launcher', initial_load)

#BRANDS = anvil.server.call('Brands', 'get_brands')
BRANDS_DD = [ (x['code'], x['code']) for x in BRANDS ]

  
#REFS = anvil.server.call('Reference', 'get_attributes', attribute_names=ATTRIBUTE_NAMES)
ACCOUNT_CODES = REFS['account_code']
ACCOUNT_CODES_DD = [ (x, x) for x in ACCOUNT_CODES ]

COST_CENTRES = REFS['cost_centre']
COST_CENTRES_DD = [ (x, x) for x in COST_CENTRES ]

LIFECYCLES = REFS['lifecycle']
LIFECYCLES_DD = [ (x, x) for x in LIFECYCLES ]

CATEGORIES = REFS['category']
CATEGORIES_DD = [ (x,x) for x in CATEGORIES ]

SERVICE_CHANGES = REFS['service_change']
SERVICE_CHANGES_DD = [ (x,x) for x in SERVICE_CHANGES ]

BILLING_TYPES = REFS['billing_type']
BILLING_TYPES_DD = [ (x,x) for x in BILLING_TYPES ]


UsersModel.ROLES.load(_roles=_roles)
UsersModel.USERS.load(_users=_users)
VendorsModel.VENDORS.load(_vendors=_vendors)

refresh()
