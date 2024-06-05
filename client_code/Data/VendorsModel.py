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
    
  def to_dict(self):
    d = { x: self[x] for x in self._defaults }
    d['vendor_id'] = self.vendor_id
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
    else
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

  def blank(self):
    return Vendor()

  def get_dropdown(self):
    return [ (x.vendor_name, x.vendor_id) for i,x in self.__d__.items() ]

  def get_name_dropdown(self):
    return [ (x.vendor_name, x.vendor_name) for i,x in self.__d__.items() ]
    
VENDORS = Vendors()
VENDORS.load()
