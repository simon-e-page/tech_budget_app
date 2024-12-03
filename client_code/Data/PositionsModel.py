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

class Position(AttributeToKey):
  _defaults = {
    'position_id': None,
    'brand': 'JB_AU',
    'title': '',
    'line_manager': None,
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
      
    for field, default in self._defaults.items():
        self[field] = item.get(field, default)

  
  def save(self):
    # Saves to backend as new or updated object
      
    try:
      ret = anvil.server.call('Positions', 'add_position', self.to_dict())
    except Exception as e:
      ret = None
      print("Error saving Position!")
      raise
    return ret

  def to_dict(self):
    d = { x: self[x] for x in self._defaults.keys() }
    #print(d)
    return d


class Positions(AttributeToDict):
  def __init__(self, _list=None):
    self.__d__ = {}
    
    if _list:
      for e in _list:
        self.add(e['position_id'], e)

  def add(self, position_id, position):
    self.__d__[position_id] = position
  
  def get(self, position_id, **kwargs):
    if position_id in self.__d__:
      return self.__d__[position_id]
    elif 'default' in kwargs:
      return kwargs['default']
    else:
      raise KeyError(f"Cant find Position with ID: {position_id}")

  def all(self):
    return [ x.to_dict() for x in self.__d__.values() ]
      
  def new(self, _data):
    position_id = _data['position_id']
    if position_id is None:
      print("Need to include a unique ID!")
      raise ValueError("No Position ID! Save to Backend first!")
    if position_id in self.__d__:
      print("Already an existing Position with that ID!")
      return None
    else:
      line_manager_position_id = _data.pop('line_manager_position_id', None)
      _data['line_manager'] = self.__d__.get(line_manager_position_id, None)
      p = Position(json=_data)
      self.add(position_id, p)
      return self.get(position_id)
      
  def load(self, _list=None, brand=None):
    self.__d__ = {}
    if _list is None:
      _list = anvil.server.call('Positions', 'get_positions', brand=brand)
    for _dict in _list:
      new_obj = self.new(_dict)

  
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

  def get_salaries(self, start_year_month, end_year_month, include_positions=True, brand=None):
    return anvil.server.call("Positions", 'get_salaries', start_year_month=start_year_month, end_year_month=end_year_month, include_positions=include_positions, brand=brand)

  def get_line_managers(self):
    line_managers = list(set(p.line_manager for p in self.__d__.values()))
    return line_managers
    
POSITIONS = Positions()
#POSITIONS.load()