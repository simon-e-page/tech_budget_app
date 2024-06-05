import anvil.server
import anvil.users

from ..Data import AttributeToDict, AttributeToKey

#####################################################################
# VENDORS
#####################################################################


class Vendor(AttributeToKey):
  _defaults = {
    'vendor_name': 'New Vendor',
    'description': 'Unknown vendor',
    'finance_vendor': None,
    'prior_year_tags': [],
    'deleted': False,
    'active': True,
    'notes': '',
    'icon_id': '',
    'vendor_url': '',
    'from_finance_system': False
  }

  def __init__(self, vendor_json=None, **kwargs):
    if vendor_json:
      # TODO: Convert JSON object?
      item = vendor_json
    else:
      item = kwargs
      
    # Remove any None values to force defaults to be used
    item = { k:v for k,v in item.items() if v is not None }

    self['vendor_id'] = item.get('vendor_id', None)
    for field, default in self._defaults.items():
      if default is not None:
        self[field] = item.get(field, default)
      else:
        self[field] = item.get(field)

  def new(self):
    if self.vendor_id is not None:
      raise ValueError("Expecting a new vendor with no vendor_id set!")
    ids = self.save()
    if ids:
      self.vendor_id = ids[0]
    else:
      print("Error creating new Vendor!")
      raise ValueError("Error creating new Vendor!")
    
  def save(self):
    # Saves to backend as new or updated object
    try:
      ret = anvil.server.call('Vendors', 'add_vendors', [self.to_dict()])
    except Exception as e:
      ret = None
      print("Error saving Vendor!")
    return ret
    
  def to_dict(self, with_finance_vendor=True, with_finance_vendor_name=False, with_finance_vendor_id=False):
    d = { x: self[x] for x in self._defaults }
    d['vendor_id'] = self.vendor_id
    if with_finance_vendor_id:
      d['finance_vendor_id'] = self.finance_vendor.vendor_id
    if with_finance_vendor_name:
      d['finance_vendor_name'] = self.finance_vendor.vendor_name
    if not with_finance_vendor:
      d.pop('finance_vendor', None)
    return d



class Vendors(AttributeToDict):
  def __init__(self, vendor_list=None):
    self.__d__ = {}
    self.name_index = {}
    
    if vendor_list:
      for vn in vendor_list:
        self.add(vn.vendor_id, vn)

  def add(self, vendor_id, vendor):
    self.__d__[vendor_id] = vendor
    self.name_index[vendor.vendor_name] = vendor_id
    
  def get(self, vendor_id):
    if vendor_id in self.__d__:
      return self.__d__[vendor_id]
    else:
      raise KeyError(f"Cant find vendor with ID: {vendor_id}")

  def get_by_name(self, vendor_name):
    if vendor_name in self.name_index:
      return self.__d__[self.name_index[vendor_name]]
    else:
      raise KeyError(f"Cant find vendor by name {vendor_name}")
      
  def new(self, vendor_data):
    vendor_id = vendor_data['vendor_id']
    if vendor_id is None:
      print("Need to save the vendor first to create an ID!")
      raise ValueError("No Vendor ID!")
    if vendor_id in self.__d__:
      print("Already an existing Vendor with that ID!")
      return None
    else:
      self.add(vendor_id, Vendor(vendor_json=vendor_data))
      return self.get(vendor_id)
      
  def load(self):
    self.__d__ = {}
    for vendor in anvil.server.call('Vendors', 'get_vendors'):
      self.new(vendor)

    # Now follow internal references!
    for key, vendor in self.__d__.items():
      finance_vendor = vendor.finance_vendor
      if finance_vendor:
        vendor.finance_vendor = self.get(finance_vendor)
  
  def blank(self):
    return Vendor()

  def get_dropdown(self, finance_field=None):
    if finance_field is None:
      vendor_list = [ (x.vendor_name, x.vendor_id) for i,x in self.__d__.items() ]
    else:
      # Cannot map to a finance vendor if that vendor is already mapped!
      mapped_set = set([ (x.finance_vendor.vendor_name, x.finance_vendor.vendor_id) for x in self.__d__.values() if x.finance_vendor is not None ])
      all_set = set([ (x.vendor_name, x.vendor_id) for i,x in self.__d__.items() if x.finance_field==finance_field ])
      vendor_list = list(all_set | mapped_set)
    return vendor_list
    
  def get_name_dropdown(self):
    return [ (x.vendor_name, x.vendor_name) for i,x in self.__d__.items() ]

VENDORS = Vendors()
VENDORS.load()
