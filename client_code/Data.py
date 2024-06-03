import anvil.server
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

# TODO: Need to work out where to keep these!
OWNERS = ['SimonPage', 'AnitaMatuszewski']
OWNERS_DD = [ (x,x) for x in OWNERS ]

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

#####################################################################
# USERS and OWNERS
#####################################################################

class User(AttributeToKey):
  _defaults = {
    'email': None,
    'full_name': 'Unknown user',
    'role_name': None,
    'team': '',
    'active': True,
    'last_login': None
  }

  def __init__(self, user_json=None, **kwargs):
    if user_json:
      # TODO: Convert JSON object?
      item = user_json
    else:
      item = kwargs
      
    # Remove any None values to force defaults to be used
    for k, v in item.items():
      if v is None:
        del item[k]

    for field, default in self._defaults.items():
      if default is not None:
        self[field] = item.get(field, default)
      else:
        self[field] = item.get(field)

  def save(self):
    # Saves to backend as new or updated object
    try:
      count = anvil.server.call('Users', 'add_users', [self.to_dict()])    
    except Exception as e:
      print('Error adding User!')
      raise
    return count

  def delete(self):
    try:
      anvil.server.call('Users', 'delete_user', self.email)   
    except Exception as e:
      print('Error deleting User!')
      raise
    

class Users(AttributeToDict):
  def __init__(self, user_list=None):
    self.__d__ = {}
    if user_list:
      for user in user_list:
        self.add(user.email, user)
            
  def get(self, email):
    if email in self.__d__:
      return self.__d__[email]

  def new(self, user_data):
    email = user_data['email']
    if email in self.__d__:
      print("Already an existing User with that ID!")
      return None
    else:
      self.add(email, User(user_json=user_data))
      return self.get(email)
      
  def load(self):
    self.__d__ = {}
    for user in anvil.server.call('Users', 'search'):
      self.new(user)


class Role(AttributeToKey):
  _defaults = {
    'role_name': None,
    'role_description': '',
    'perm_create_user': False,
    'perm_create_actual': False,
    'perm_create_vendor': False,
    'perm_create_budget': False,
    'perm_read_budget': True
  }

  def __init__(self, role_json=None, **kwargs):
    if role_json:
      # TODO: Convert JSON object?
      item = role_json
    else:
      item = kwargs
      
    # Remove any None values to force defaults to be used
    for k, v in item.items():
      if v is None:
        del item[k]

    for field, default in self._defaults.items():
      if default is not None:
        self[field] = item.get(field, default)
      else:
        self[field] = item.get(field)

  def save(self):
    # Saves to backend as new or updated object
    try:
      count = anvil.server.call('Users', 'add_roles', [self.to_dict()])    
    except Exception as e:
      print('Error adding Role!')
      raise
    return count
  
  def delete(self):
    try:
      anvil.server.call('Users', 'delete_role', self.role_name)   
    except Exception as e:
      print('Error deleting User!')
      raise


class Roles(AttributeToDict):
  def __init__(self, role_list=None):
    self.__d__ = {}
    if role_list:
      for role in role_list:
        self.add(role.role_name, role)
        
  def get(self, role_name):
    if role_name in self.__d__:
      return self.__d__[role_name]

  def new(self, role_data):
    role_name = role_data['role_name']
    if role_name in self.__d__:
      print("Already an existing Role with that ID!")
      return None
    else:
      self.add(role_name, Role(role_json=role_data))
      return self.get(role_name)

  def load(self):
    self.__d__ = {}
    for role in anvil.server.call('Users', 'get_roles'):
      self.new(role)


#####################################################################
# VENDORS
#####################################################################



class Vendor(AttributeToKey):
  _defaults = {
    'vendor_name': 'New Vendor',
    'description': 'Unknown vendor',
    'finance_tags': [],
    'prior_year_tags': [],
    'deleted': False,
    'active': True,
    'notes': '',
    'icon_id': '',
    'vendor_url': ''
  }

  def __init__(self, vendor_json=None, **kwargs):
    if vendor_json:
      # TODO: Convert JSON object?
      item = vendor_json
    else:
      item = kwargs
      
    # Remove any None values to force defaults to be used
    for k, v in item.items():
      if v is None:
        del item[k]

    self['vendor_id'] = item.get('vendor_id', None)
    for field, default in self._defaults.items():
      if default is not None:
        self[field] = item.get(field, default)
      else:
        self[field] = item.get(field)

  def save(self):
    # Saves to backend as new or updated object
    return anvil.server.call('Vendors', 'add_vendors', [self.to_dict()])    
    
  def to_dict(self):
    d = { x: self[x] for x in self._defaults }
    d['vendor_id'] = self.vendor_id
    return d


class Vendors(AttributeToDict):
  def __init__(self, vendor_list=None):
    self.__d__ = {}
    if vendor_list:
      for vn in vendor_list:
        self.add(vn.vendor_id, vn)
            
  def get(self, vendor_id):
    if vendor_id in self.__d__:
      return self.__d__[vendor_id]

  def new(self, vendor_data):
    vendor_id = vendor_data['vendor_name']
    if vendor_id in self.__d__:
      print("Already an existing Vendor with that ID!")
      return None
    else:
      self.add(vendor_id, Vendor(vendor_json=vendor_data))
      return self.get(vendor_id)
      
  def load(self):
    self.__d__ = {}
    for role in anvil.server.call('Vendors', 'get_vendors'):
      self.new(role)




#####################################################################
#  ICON
#####################################################################


class Icon(AttributeToKey):
  
  def __init__(self, icon_id, content):
    try:
      # Max file size of 100kB (note not Kibibytes to be technical!)
      if content.length > 100000:
        print("Selected file is too large. Please reduce and try again!")
      elif (content.content_type in ACCEPTABLE_IMAGES.keys()):
        self.icon_id = icon_id
        self.content = content
      else:
        print('Not an acceptable image file. Please try again!')
    except Exception as e:    
      print("Error adding new icon!")
        
    if not icon_id:
      print("Could not create new Icon")
      return

  def save(self):
    #try:
    anvil.server.call('Vendors', 'add_icon', self.icon_id, self.content)
    #except Exception as e:
    #  print("Error uploading icon!")
      

class Icons(AttributeToDict):
  def __init__(self):
    self.__d__ = {}

  def length(self):
    return len(self.__d__)

  def load_all(self):
    icons_cache = anvil.server.call('Vendors', 'get_icons')
    for k, v in icons_cache.items():
      self.add(k, Icon(icon_id=k, content=v))

  def load(self, icon_id):
    try:
      content = anvil.server.call('Vendors', 'get_icon', icon_id)
      icon = Icon(icon_id=icon_id, content=content)
      self.add(icon_id, icon)
    except Exception as e:
      print(f"Could not find icon_id: {icon_id}!")
      icon = None
      
    return icon

  def get_content(self, icon_id):
    try:
      content = self.get(icon_id, self.load(icon_id)).content
    except Exception as e:
      content = None
    return content



    

#####################################################################
# TRANSACTION
#####################################################################



class Transaction(AttributeToKey):
  _defaults = {
    'brand': 'JB_AU',
    'vendor_id': None,
    'description': None,
    'owner': 'simon.page@jbhifi.com.au',
    'transaction_type': 'Budget',
    'account_code': 'Software Maintenance',
    'cost_centre': 'IT (6000)',
    'service_change': 'Organic Growth',
    'lifecycle': 'Existing',
    'updated': None,
    'source': '',
    'status': 'active',
    'budget_locked': 0,
    'to_review': False,
    'category': 'Operations',
    'business_contact': '',
    'project': '',
    'updated_by': '',
    'import_id': '',
    'deleted': False,
    'notes': '',
    'last_actual': 0,
    'billing_type': 'Consumption',
    'contract_start_date': None,
    'contract_end_date': None,
    'expected_monthly_amount': 0.0,
  }
  def __init__(self, transaction_json, **kwargs):
    if transaction_json:
      # TODO: Convert JSON object?
      item = transaction_json
    else:
      item = kwargs
      
    # Remove any None values to force defaults to be used
    for k, v in item.items():
      if v is None:
        pass
        #del item[k]

    
    self['transaction_id'] = item.get('transaction_id', None)
    for field, default in self._defaults.items():
      if default is not None:
        self[field] = item.get(field, default)
      else:
        self[field] = item.get(field)

  def delete(self):
    anvil.server.call('Transactions', 'delete_transactions', [self.transaction_id])

  def to_dict(self):
    return { x: self[x] for x in list(self._defaults.keys()) }

  # TODO: Review - do we need this?
  def copy(self):
    props = { x: self[x] for x in list(self._defaults.keys()) }
    #print(props)
    t = Transaction(transaction_json=props)
    print(t)
    return t

  def update(self):
    self['updated_by'] = anvil.users.get_user()['email']
    self['updated'] = dt.datetime.now()
    try:
      anvil.server.call('Transactions', 'update', self.transaction_id, self.to_dict())
    except Exception as e:
      print("Error updating transaction: {0}".format(self.transaction_id))

  def get_all_entries(self):
    return anvil.server.call('Transactions', 'get_all_entries_by_transaction_id', 
                           transaction_id=self.transaction_id,
                          )

  def add_entries(self, new_entries):
    return anvil.server.call('Transactions', 'add_entries', self.transaction_id, new_entries)

    
class LazyTransactionList:  
  def __init__(self, sort='timestamp', filters={'duplicate': False}, date_filter={}, direction='descending', page_size=10, initial_page=0):
    # Page numbers are zero indexed to match DataGrid
    self.page_loaded = []
    self.indexed = {}
    self.max_page = 0
    self.current_page = initial_page
    #self.reset(sort=sort, filters=filters, date_filter=date_filter, direction=direction, page_size=page_size, initial_page=initial_page)
        
  def __getitem__(self, item):
      if isinstance(item, (int, slice)):
          print("Got indexing: {0}".format(item))
          ret = self.list[item]
          if None in ret:
            print("Found a None in list!")
            print(ret)
          return self.list[item]
      print("Got getitem with {0}".format(item))
      return [self.list[i] for i in item]
    
  def __setitem__(self, item, value):
    print("Got setitem!")
    
  def __delitem__(self, item):
    print("Got delitem!")
    
  def __iter__(self):
    self.iter_obj = self.get_iterable()
    return self
    
  def __len__(self):
    return self.length
    
  def __next__(self):
    return next(self.iter_obj)

  def get_max_page(self):
    return self.max_page
    
  def get_page_size(self):
    return self.page_size

  def get_current_page(self):
    return self.current_page
      
  def next_page(self):
    if self.current_page < self.max_page:
      self.set_page(self.current_page + 1)

  def previous_page(self):
    if self.current_page > 0:
      self.set_page(self.current_page - 1)
      
  def set_page(self, page):
    """ Makes sure this page is loaded """
    self.current_page = page
    self.get_page(page)
    
  def clear_cache(self, page=None):
    """ Ensure pages get reloaded from server """
    if (page is not None) and (page >= 0) and (page <= self.max_page):
      self.page_loaded[page] = 0
    else:
      self.page_loaded = [ 0 for x in range(0, self.max_page+1) ]

  def initial_load(self, page):
    start = page * self.page_size
    end = start + self.page_size
    self.length, slice = self.load(start, end)
    
    # Check if the initial page desired is beyond the actual list!
    while start >= self.length and page > 0:
      page -= 1
      start = page * self.page_size
      end = start + self.page_size
      self.length, slice = self.load(start, end)
      
    self.current_page = page
    self.max_page = int(self.length / self.page_size) 
    
    trans_list = [ Transaction(transaction_json=x) for x in slice ]
    self.list = [ None for x in range(0, self.length) ]        
    self.list[start:end] = trans_list
    
    for t in trans_list:
      self.indexed[t.transaction_id] = t
      
    self.page_loaded = [ 0 for x in range(0, self.max_page+1) ]
    self.page_loaded[page] = 1
    print("{0} transactions in {1} pages of {2} items each".format(self.length, self.max_page+1, self.page_size))
      
  def load(self, start, end):
    """ Setup backend dataset using filters """
    length, slice = anvil.server.call('Transactions', 'get_transaction_slice', 
                                  sort=self.sort, 
                                  filters=self.filters, 
                                  date_filter={},  # UNUSED
                                  direction=self.direction,
                                  start=start,
                                  end=end
                                 )
    
    return length, slice
    
  def get_page(self, page):
    start = int(page * self.page_size)
    end = start + self.page_size
    if not self.page_loaded[page]:
      ignore, slice = self.load(start, end)
      self.page_loaded[page] = 1      
      trans_list = [ Transaction(transaction_json=x) for x in slice ]
      self.list[start:end] = trans_list
      for t in trans_list:
        self.indexed[t.transaction_id] = t

    ret = self.list[start:end]
    return ret    

  def reverse(self):
    self.direction = 'descending' if self.direction == 'ascending' else 'ascending'
    self.list = self.list[::-1]
    # Need to clear the cache if not all transactions are present (as reversing the sort order changes the pagination)
    if 0 in self.page_loaded:
      self.clear_cache()

  def new_sort(self, sort_value):
    self.sort = sort_value
    if 0 in self.page_loaded:
      self.clear_cache()
    else:
      reverse = True if self.direction == 'descending' else False
      self.list = sorted(self.list, key=itemgetter(sort_value), reverse=reverse)
    
  def get_iterable(self):
    page = 0
    while page <= self.max_page:
      items = self.get_page(page=page)
      for item in items:
          yield item
      page += 1

  def new(self, transaction):
    try:
      transactions = anvil.server.call('Transactions', 'add_transaction', transaction.to_dict())
      new_trans_dict = transactions[0]
      ret = Transaction(transaction_json=new_trans_dict)
      self.indexed[ret.transaction_id] = ret
    except Exception as e:
      print("Error adding new transaction!")
      raise
    return ret

  def get(self, transaction_id):
    if transaction_id in self.indexed:
      return self.indexed[transaction_id]
    else:
      trans = Transaction(transaction_json=anvil.server.call('Transactions', 'get_transaction_by_id', transaction_id))
      self.indexed[transaction_id] = trans
      return trans

  def delete(self, transaction_ids):
    for transaction_id in transaction_ids:
      if transaction_id in self.indexed:
        self.indexed[transaction_id].delete()
        del self.indexed[transaction_id]
    self.reset()

  def reset(self, sort='timestamp', filters={}, date_filter={}, direction='descending', page_size=10, initial_page=0):
    self.sort = sort
    self.filters = filters
    self.date_filter = date_filter
    self.direction = direction
    self.page_size = page_size
    self.initial_page = initial_page
    self.clear_cache()
    #self.initial_load(self.current_page)
    self.initial_load(self.initial_page)
    self.iter_obj = self.get_iterable()

  def update(self, transaction_ids, updates):
    count = 0
    try:
      count = anvil.server.call('Transactions', 'update_transactions_bulk', transaction_ids, updates)
    except Exception as e:
      print("Error in update_transactions_bulk")
    return count

  def search(self, sort='timestamp', filters = {}, date_filter={}, direction='descending'):
    """ Returns a direct search of transactions from the backend. 
        Operates independently of cached items 
    """ 
    filters['brand']=CURRENT_BRAND
    _ignore, slice = anvil.server.call('Transactions', 'get_transactions_slice', 
                                  sort=sort, 
                                  filters=filters, 
                                  date_filter=date_filter, 
                                  direction=direction
                                 )
    trans = [ Transaction(transaction_json=x) for x in slice ]
    return trans

  def reconcile(self, transactions):
    transaction_ids = [ x.transaction_id for x in transactions ]
    count = anvil.server.call('Transactions', 'reconcile_transactions', transaction_ids)
    return count
    
  def match(self, transaction):
    """ Returns a set of matching transactions from the backend
        Operates independently from the set of cached items
    """
    matched_trans_list = [] #anvil.server.call('match_transactions', transaction.to_dict())
    matched_trans = [ Transaction(transaction_json=x) for x in matched_trans_list ]
    return matched_trans





#####################################################################
# IMPORTER
#####################################################################


#class Importer:
#  def start(self, file_obj, account_name):
#    return None #anvil.server.call('upload_transactions', file_obj, account_name)
#
#  def next_batch(self, code):
#    return None #anvil.server.call('upsert_batch', code)
#
#  def process_paypal(self, account_name, start, end):
#    return None #anvil.server.call('process_paypal', account_name, start=start, end=end)
#
#  def get_import_ids(self, account_name):
#    return [] #anvil.server.call('get_import_ids', account_name)


VENDORS = Vendors()
TRANSACTIONS = LazyTransactionList()
USERS = Users()
ROLES = Roles()
ICONS = Icons()

FIN_YEARS = None
CURRENT_YEAR = None
BUDGET_YEAR = None
CURRENT_BRAND = None

def get_transactions():
  global TRANSACTIONS
  if TRANSACTIONS is None:
    TRANSACTIONS = LazyTransactionList()
  return TRANSACTIONS

def refresh():
  global VENDORS, FIN_YEARS, CURRENT_YEAR, BUDGET_YEAR
  vendors = anvil.server.call('Vendors', 'get_vendors')
  vendor_list = [ Vendor(vendor_json=x) for x in vendors ]
  VENDORS = Vendors(vendor_list=vendor_list)
  FIN_YEARS, BUDGET_YEAR, CURRENT_YEAR = anvil.server.call('Calendar', 'get_fin_years')
  USERS.load()
  ROLES.load()

#ICONS.load()

#####################################################################
# ORGANISATIONS
#####################################################################
  


#def get_icon(icon_id):
#  # Loads icons on first load
#  if ICONS.length() == 0:
#    ICONS.load()
#
#  source = None
#  icon = ICONS.get(icon_id, None)
#  if icon:
#    source = icon.content
#  return source


def gpt_set_account_data(account_name):
  return None #anvil.server.call('gpt_set_account_data', account_name=account_name)

def gpt_run(prompt):
  return None #anvil.server.call('gpt_run', prompt=prompt)

refresh()
