import anvil.server
import anvil.users

import datetime as dt

from ..Data import AttributeToDict, AttributeToKey, CURRENT_BRAND, VendorsModel

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
      elif field=='vendor_id':
        self['vendor'] = VendorsModel.VENDORS.get(item['vendor_id'])
      else:
        self[field] = item.get(field)

  def delete(self):
    try:
      anvil.server.call('Transactions', 'delete_transactions', [self.transaction_id])
    except Exception as e:
      print("Error deleting transaction")
      return False
    return True
      
  def to_dict(self, with_vendor_id=True, with_vendor_name=False, with_vendor=False):
    d = { x: self[x] for x in list(self._defaults.keys()) if x != 'vendor_id' }
    d['transaction_id'] = self.transaction_id
    if with_vendor_name:
      d['vendor_name'] = self.vendor['vendor_name']
    if with_vendor_id:
      d['vendor_id'] = self.vendor['vendor_id']
    if with_vendor:
      d['vendor'] = self.vendor
    return d

  # TODO: Review - do we need this?
  def copy(self):
    props = { x: self[x] for x in list(self._defaults.keys()) if x != 'vendor_id' }
    props['vendor_id'] = self.vendor.vendor_id
    #print(props)
    t = Transaction(transaction_json=props)
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
    try:
      ret = anvil.server.call('Transactions', 'add_entries', self.transaction_id, new_entries)
    except Exception as e:
      print('Error updating entries!')
      ret = None
    return ret

    
class LazyTransactionList:  
  def __init__(self, sort='owner', filters={'deleted': False}, date_filter={}, direction='descending', page_size=10, initial_page=0):
    # Page numbers are zero indexed to match DataGrid
    self.page_loaded = []
    self.indexed = {}
    self.max_page = 0
    self.current_page = initial_page
    self.sort = sort
    self.direction = direction
    self.filters = filters
    self.filters['brand'] = CURRENT_BRAND
    self.length = 0
    self.data = []
    
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
      self.length, slice = self._load(start=start, end=end)
      
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
      
  def _load(self, start=None, end=None, **kwargs):
    """ Setup backend dataset using filters """
    filters = {**self.filters, **kwargs}
    length, slice = anvil.server.call('Transactions', 'get_transaction_slice', 
                                  sort=self.sort, 
                                  filters=filters, 
                                  date_filter={},  # UNUSED
                                  direction=self.direction,
                                  start=start,
                                  end=end
                                 )
    
    return length, slice

  def load(self, start=None, end=None, **kwargs):
    self.length, slice = self._load(start=start, end=end, **kwargs)
    self.data = [ Transaction(transaction_json=x) for x in slice ]
    
  def get_page(self, page):
    start = int(page * self.page_size)
    end = start + self.page_size
    if not self.page_loaded[page]:
      ignore, slice = self._load(start=start, end=end)
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
      # FAIL: Not sure what this was trying to do..!!
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

  def search(self, **kwargs):
    trans = []
    for t in self.data:
      found = True
      for k,v in kwargs.items():
        if k in t and t[k]!=v:
          found = False
      if found:
        trans.append(t)
    return trans
    
  #def search(self, sort='timestamp', filters = {}, date_filter={}, direction='descending'):
  #  """ Returns a direct search of transactions from the backend. 
  #      Operates independently of cached items 
  #  """ 
  #  filters['brand']=CURRENT_BRAND
  #  _ignore, slice = anvil.server.call('Transactions', 'get_transactions_slice', 
  #                                sort=sort, 
  #                                filters=filters, 
  #                                date_filter=date_filter, 
  #                                direction=direction
  #                               )
  #  trans = [ Transaction(transaction_json=x) for x in slice ]
  #  return trans

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

  def to_records(self, with_vendor_name=True, with_vendor=True, with_vendor_id=False):
    return [ x.to_dict(with_vendor_name=with_vendor_name, with_vendor_id=with_vendor_id, with_vendor=with_vendor) for x in self.data ]
    

#############
# MAIN
###############

TRANSACTIONS = LazyTransactionList()

def get_transactions():
  global TRANSACTIONS
  if TRANSACTIONS is None:
    TRANSACTIONS = LazyTransactionList()
  return TRANSACTIONS
