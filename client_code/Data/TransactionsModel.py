import anvil.server
import anvil.users

import datetime as dt

from ..Data import AttributeToDict, AttributeToKey, CURRENT_BRAND, VendorsModel, CURRENT_YEAR, BUDGET_YEAR

#####################################################################
# TRANSACTION
#####################################################################



class Transaction(AttributeToKey):
  _defaults = {
    'brand': 'JB_AU',
    'vendor_id': None,
    'description': None,
    'owner': 'simon.page@jbhifi.com.au',
    'team': 'Unknown',
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
    else:
      d.pop('vendor', None)
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

  def add_entries(self, new_entries, overwrite=False):
    try:
      ret = anvil.server.call('Transactions', 'add_entries', self.transaction_id, new_entries, overwrite)
    except Exception as e:
      print('Error updating entries!')
      ret = None
    return ret

    
class LazyTransactionList(AttributeToDict):  
  def __init__(self, sort='owner', filters={'deleted': False}, date_filter={}, direction='descending', page_size=10, initial_page=0):
    self.sort = sort
    self.direction = direction
    self.filters = filters
    self.filters['brand'] = CURRENT_BRAND
    self.__d__ = {}
     
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

  def get(self, transaction_id):
    """ Load and return a single transaction by ID """
    transaction = anvil.server.call('Transactions', 'get_transaction_by_id', transaction_id=transaction_id)
    if transaction is not None:
      trans = Transaction(transaction_json=transaction)
    else:
      trans = None
    return trans
    
  def load(self, start=None, end=None, **kwargs):
    self.length, slice = self._load(start=start, end=end, **kwargs)
    self.__d__ = { x['transaction_id'] : Transaction(transaction_json=x) for x in slice }
    
  def bulk_add(self, transactions, update=True):
    """ Adds a list of transactions present as a list of dictionaries """
    try:
      transaction_ids = anvil.server.call('Transactions', 'add_transaction', transactions, update=update)
    except Exception as e:
      print("Error adding new transactions as bulk addition!")
      raise
    return transaction_ids

  def new(self, transaction, update=True):
    try:
      transaction_ids = anvil.server.call('Transactions', 'add_transaction', transaction.to_dict(), update=update)
      new_trans_id = transaction_ids[0]
      transaction['transaction_id'] = new_trans_id
      self.__d__[transaction.transaction_id] = transaction
    except Exception as e:
      print("Error adding new transaction!")
      raise
    return transaction

  def delete(self, transaction_ids):
    for transaction_id in transaction_ids:
        t = self.__d__.pop(transaction_id, None)
        t.delete()

 
  def update(self, transaction_ids, updates):
    count = 0
    try:
      count = anvil.server.call('Transactions', 'update_transactions_bulk', transaction_ids, updates)
    except Exception as e:
      print("Error in update_transactions_bulk")
    return count

  def search(self, **kwargs):
    trans = self.__d__.copy()
    for k,v in kwargs.items():
      for t_id, t in trans.items():
        keep = {}
        found = True
        if k=='vendor_name':
          found = (t.vendor.vendor_name == v)
        elif k=='vendor_id':
          found = (t.vendor.vendor_id == v)
        else:
          found = (t.get(k, None) == v)
        if found:
          keep[t_id] = t
      trans = keep
      print(f"After looking for {k}={v} we have {len(keep)} transactions")
    return list(trans.values())
    
  def get_entry_lines(self, transaction_type, data):
    year = BUDGET_YEAR if transaction_type=='Budget' else CURRENT_YEAR
    print(year)
    transaction_ids = [ x['transaction_id'] for x in data ]
    entries = anvil.server.call('Transactions', 'get_entries_by_transaction', fin_year=year, transaction_type=transaction_type, transaction_ids=transaction_ids)
    return entries
    
  def to_records(self, with_vendor_name=True, with_vendor=True, with_vendor_id=False):
    return [ x.to_dict(with_vendor_name=with_vendor_name, with_vendor_id=with_vendor_id, with_vendor=with_vendor) for x in self.__d__.values() ]

  def blank(self, transaction_data=None):
    return Transaction(transaction_json=transaction_data)

  def search_and_add_entries(self, entries, overwrite=False):
    try:
      ret = anvil.server.call('Transactions', 'search_and_add_entries', brand=CURRENT_BRAND, entries=entries, overwrite=overwrite)
    except Exception as e:
      print('Error updating entries!')
      ret = None
      raise
    return ret

  def delete_entries(self, year_month, transaction_type='Actual'):
    return anvil.server.call('Transactions', 'delete_entries', brand=CURRENT_BRAND, year_month=year_month, transaction_type='Actual')

  
#############
# MAIN
###############

TRANSACTIONS = LazyTransactionList()

def get_transactions():
  global TRANSACTIONS
  if TRANSACTIONS is None:
    TRANSACTIONS = LazyTransactionList()
  return TRANSACTIONS
