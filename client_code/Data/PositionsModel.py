import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from operator import attrgetter
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from .Data import Module1
#
#    Module1.say_hello()
#

from .BaseModel import AttributeToDict, AttributeToKey
from .. import Data

class Position(AttributeToKey):
  _defaults = {
    'position_id': None,
    'brand': 'JB_AU',
    'title': '',
    'role_type': 'Permanent',
    'description': '',
    'team': '',
    'reason': 'Backfill',
    'recruitment_code': None,
    'status': 'active'
  }

  def __init__(self, json=None, **kwargs):
    if json:
      # TODO: Convert JSON object?
      item = json
    else:
      item = kwargs
      
    # Remove any None values to force defaults to be used
    item = { k:v for k,v in item.items() if v is not None }

    self['position_id'] = item.get('position_id', None)
    for field, default in self._defaults.items():
      if default is not None:
        self[field] = item.get(field, default)
      else:
        self[field] = item.get(field, None)

  
  def save(self):
    # Saves to backend as new or updated object
      
    try:
      ret = anvil.server.call('Positions', 'add_position', [self.to_dict()])
    except Exception as e:
      ret = None
      print("Error saving Position!")
      raise
    return ret


class Positions(AttributeToDict):
  def __init__(self, _list=None):
    self.__d__ = {}
    
    if _list:
      for e in _list:
        self.add(e['position_id'], e)

  def add(self, position_id, _data):
    self.__d__[position_id] = _data
  
  def get(self, position_id, **kwargs):
    if position_id in self.__d__:
      return self.__d__[position_id]
    elif 'default' in kwargs:
      return kwargs['default']
    else:
      raise KeyError(f"Cant find Position with ID: {position_id}")

      
  def new(self, _data):
    position_id = _data['position_id']
    if position_id is None:
      print("Need to include a unique ID!")
      raise ValueError("No Position ID! Save to Backend first!")
    if position_id in self.__d__:
      print("Already an existing Position with that ID!")
      return None
    else:
      self.add(position_id, Position(json=_data))
      return self.get(position_id)
      
  def load(self, _list=None):
    self.__d__ = {}
    if _list is None:
      _list = anvil.server.call('Positions', 'get_positions', brand=Data.CURRENT_BRAND)
    for position in _list:
      self.new(position)

  
  def blank(self, _data=None):
    return Position(json=_data)

  
  def get_dropdown(self, **filters):
    ret = [ (f"{x.title}, {x.team}", x.position) for x in sorted(self.__d__, key=attrgetter('team', 'title')) ]
    return ret

  def delete(self, _ids):
    try:
      num = anvil.server.call('Positions', 'delete_positions', _ids)
    except Exception as e:
      print(e)
      print("Error deleting positions!")
      num = 0
    self.load()
    return num

POSITIONS = Positions()