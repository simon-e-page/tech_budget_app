import anvil.server
import re

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

ICONS = {}

class AttributeToKey:
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

  def items(self):
    return self.__d__.items()

  def to_dict(self):
    return self.__d__

  def __len__(self):
    return len(self.__d__)


#####################################################################
# BUDGET
#####################################################################

class Entry(AttributeToKey):
  def __init__(self, entry_json=None, account_name=None, amount=None):
    if entry_json is None:
      self.account_name = account_name
      self.amount = amount
    else:
      self.account_name = entry_json['account_name']
      self.amount = entry_json['amount']



class Budget(AttributeToDict):
  def __init__(self, fin_year, entry_list=None):
    self.fin_year = fin_year
    self.__d__ = {}
    if entry_list:
      for e in entry_list:
        self.add(e.account_name, e)

  def save(self):
    try:
      ret = {} #anvil.server.call('save_budget_entries', fin_year=self.fin_year, entries=self.to_dict())
    except Exception as e:
      print("Exception saving Budget Entries!")
      print(e)
      print(self.__d__)
      ret = {}
    return ret

  def to_dict(self):
    return { k: v.amount for k, v in self.__d__.items() }

class Budgets(AttributeToDict):
  def __init__(self, budget_list=None):
    self.__d__ = {}
    if budget_list:
      for b in budget_list:
        self.add(b.fin_year, b)


#####################################################################
# ACCOUNT
#####################################################################


class Vendor(AttributeToKey):
  _defaults = {
    'vendor_id': None,
    'description': '',
    'finance_tags': [],
    'prior_year_tags': [],
    'deleted': False,
    'active': True,
    'notes': '',
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

    for field, default in self._defaults.items():
      if default is not None:
        self[field] = item.get(field, default)
      else:
        self[field] = item.get(field)

  
  def save(self):
    # Saves to backend as new or updated object
    props = { x: self[x] for x in list(self._defaults.keys()) }
    print("Save Account")
    anvil.server.call('Vendors', 'add_vendor', props)    
    
  def to_dict(self):
    return { x: self[x] for x in self._defaults }


class Vendors(AttributeToDict):
  def __init__(self, vendor_list=None):
    self.__d__ = {}
    if vendor_list:
      for vn in vendor_list:
        self.add(vn.vendor_id, vn)
        
  def get_dropdown(self):
    return [(x, x) for x in self.__d__.keys() ]
    
  def get(self, vendor_id):
    if vendor_id in self.indexed:
      return self.indexed[vendor_id]

  



#####################################################################
#  ICON
#####################################################################


class Icon(AttributeToKey):
  def __init__(self, name, content, icon_id=None):
    """ Two variations to construct Icon objects:
          1) Existing loaded from Mongo with name, content and existing ID: need name, content, icon_id
          2) New from file, needs to get a new ID from Mongo: need name, content
    """
    ACCEPTABLE = {'image/png': 'png', 'image/jpg': 'jpg', 'image/jpeg': 'jpeg'}

    if icon_id is None:
      try:
        # Max file size of 100kB (note not Kibibytes to be technical!)
        if content.length > 100000:
          alert("Selected file is too large. Please reduce and try again!")
        elif (content.content_type in ACCEPTABLE.keys()):
          name = name + "." + ACCEPTABLE[content.content_type]
          icon_id = None #anvil.server.call('create_account_icon_file', name, content)
        else:
          alert('Not an acceptable image file. Please try again!')
      except Exception as e:    
        alert("Error uploading new icon!")
          
      if not icon_id:
        raise Error("Could not create new Icon")

    self.name = name
    self.content = content
    self.icon_id = icon_id    

class Icons(AttributeToDict):
  def __init__(self):
    self.__d__ = {}

  def length(self):
    return len(self.__d__)

  def load(self):
    icons_cache = {} #anvil.server.call('get_icons')
    for k, v in icons_cache.items():
      self.add(k, Icon(name=v.name, content=v, icon_id=k))

    

#####################################################################
# TRANSACTION
#####################################################################



class Transaction(AttributeToKey):
  _defaults = {
    'transaction_id': None,
    'vendor_id': None,
    'description': None,
    'owner': 'simon.page@gjbhifi.com.au',
    'transaction_type': 'Budget',
    'account_code': 'Software Maintenance',
    'cost_centre': '6000',
    'service_description': None,
    'notes': '',
    'updated_by': '',
    'updated': None,
    'lifecycle': 'Core',
    'budget_locked': 0,
    'source': '',
    'to_review': False,
    'import_id': '',
    'business_contact': False,
    'brand': 'JB_AU',
    'deleted': False,
    'last_actual': 0,
    'contract_start_date': None,
    'contract_end_date': None,
    'expected_monthly_amount': 0.0,
    'status': 'active'
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

  def update(self, updated):
    try:
      #orig = self.to_dict()
      for k in updated.keys():
        self[k] = updated[k]
      anvil.server.call('Transactions', 'update_transaction', self.transaction_id, self.to_dict())
    except Exception as e:
      print("Error updating transaction: {0}".format(self.transaction_id))

  def get_all_entries(self, transaction_type):
    return anvil.server.call('Transactions', 'get_all_entries_by_transaction_id', 
                           transaction_id=self.transaction_id,
                          )

    
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
                                  filters={ 'brand': CURRENT_BRAND }, 
                                  date_filter={}, 
                                  #filters=self.filters, 
                                  #date_filter=self.date_filter, 
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


class Importer:
  def start(self, file_obj, account_name):
    return None #anvil.server.call('upload_transactions', file_obj, account_name)

  def next_batch(self, code):
    return None #anvil.server.call('upsert_batch', code)

  def process_paypal(self, account_name, start, end):
    return None #anvil.server.call('process_paypal', account_name, start=start, end=end)

  def get_import_ids(self, account_name):
    return [] #anvil.server.call('get_import_ids', account_name)


VENDORS = Vendors()
TRANSACTIONS = LazyTransactionList()
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
  #ICONS.load()

#####################################################################
# ORGANISATIONS
#####################################################################
  


def get_icon(icon_id):
  # Loads icons on first load
  if ICONS.length() == 0:
    ICONS.load()

  source = None
  icon = ICONS.get(icon_id, None)
  if icon:
    source = icon.content
  return source


def gpt_set_account_data(account_name):
  return None #anvil.server.call('gpt_set_account_data', account_name=account_name)

def gpt_run(prompt):
  return None #anvil.server.call('gpt_run', prompt=prompt)

refresh()
