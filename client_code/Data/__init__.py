import anvil.server
import anvil.users
import re
import datetime as dt

"""This module collects global variables to be used throughout the app"""
"""
TODO:
"""

# TODO: Move into app_tables?
BRANDS = [ 'JB_AU', 'JB_NZ', 'TGG']
BRANDS_DD = [ (x,x) for x in BRANDS ]

ACCOUNT_CODES = [  'Software Maintenance', 'Hardware Maintenance', 'Consulting' ]
ACCOUNT_CODES_DD = [ (x, x) for x in ACCOUNT_CODES ]

COST_CENTRES = [ 'IT (6000)', 'Online (3121)', 'Stores', 'HR', 'Commercial' ]
COST_CENTRES_DD = [ (x, x) for x in COST_CENTRES ]

LIFECYCLES = [ 'Existing', 'Existing - Discretionary', 'New - Committed', 'New - Discretionary', 'Legacy', 'Peripherals', 'New - Ex-IT' ]
LIFECYCLES_DD = [ (x, x) for x in LIFECYCLES ]

CATEGORIES = [ 'Operations', 'Network & Infrastructure', 'E-Commerce & Marketing', 'Cybersecurity', 'Finance & HR', 'Supply Chain', 'SaaS Consulting', 'Non-IT', 'Commercial' ]
CATEGORIES_DD = [ (x,x) for x in CATEGORIES ]

SERVICE_CHANGES = ['Organic Growth', 'Strategic Projects', 'Commercial', 'Decommissioning']
SERVICE_CHANGES_DD = [ (x,x) for x in SERVICE_CHANGES ]

BILLING_TYPES = [ 'Prepayments', 'Consumption' ]
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


def refresh():
  global FIN_YEARS, CURRENT_YEAR, BUDGET_YEAR
  FIN_YEARS, BUDGET_YEAR, CURRENT_YEAR = anvil.server.call('Calendar', 'get_fin_years')

def get_actuals_updated(year):
  return anvil.server.call('Calendar', 'get_actuals_updated', year)

def actuals_updated(year, year_month):
  return anvil.server.call('Calendar', 'actuals_updated', year_month, year)

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

refresh()
