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

class Employee(AttributeToKey):
  _defaults = {
    'brand': 'JB_AU',
    'employee_id': None,
    'firstname': '',
    'lastname': '',
    'gender': 'M',
    'email': '',
    'status': 'active'
  }

  def __init__(self, emp_json=None, **kwargs):
    if emp_json:
      # TODO: Convert JSON object?
      item = emp_json
    else:
      item = kwargs
      
    # Remove any None values to force defaults to be used
    item = { k:v for k,v in item.items() if v is not None }

    self['employee_id'] = item.get('employee_id', None)
    for field, default in self._defaults.items():
      if default is not None:
        self[field] = item.get(field, default)
      else:
        self[field] = item.get(field, None)

  @property
  def full_name(self):
    return f"{self['firstname']} {self['lastname']}"
  
  def save(self):
    # Saves to backend as new or updated object
    if self.employee_id is None:
      return None
      
    try:
      ret = anvil.server.call('Employees', 'add_employee', self.to_dict())
    except Exception as e:
      ret = None
      print("Error saving Employee!")
      raise
    return ret

  def unassign(self, year_months):
    return anvil.server.call('Employees', 'unassign_employee', employee_id=self.employee_id, year_months=year_months)

  def assign(self, position_id, year_months):
    return anvil.server.call('Employees', 'assign', employee_id=self.employee_id, position_id=position_id, year_months=year_months)

  def add_actual(self, year_month, amount):
    return anvil.server.call('Employees', 'add_actual', employee_id=self.employee_id, year_month=year_month, amount=amount)








class Employees(AttributeToDict):
  def __init__(self, emp_list=None):
    self.__d__ = {}
    self.name_index = {}
    
    if emp_list:
      for e in emp_list:
        self.add(e.employee_id, e)

  def add(self, employee_id, employee):
    self.__d__[employee_id] = employee
  
  def get(self, employee_id, **kwargs):
    if employee_id in self.__d__:
      return self.__d__[employee_id]
    elif 'default' in kwargs:
      return kwargs['default']
    else:
      raise KeyError(f"Cant find Employee with ID: {employee_id}")

      
  def new(self, emp_data):
    employee_id = emp_data['employee_id']
    if employee_id is None:
      print("Need to include a unique ID!")
      raise ValueError("No Employee ID!")
    if employee_id in self.__d__:
      print("Already an existing Employee with that ID!")
      return None
    else:
      self.add(employee_id, Employee(emp_json=emp_data))
      return self.get(employee_id)
      
  def load(self, _list=None, brand=None):
    self.__d__ = {}
    if _list is None:
      _list = anvil.server.call('Employees', 'get_employees', brand=brand)
    for employee in _list:
      self.new(employee)

  
  def blank(self, emp_data=None):
    return Employee(emp_json=emp_data)

  def all(self):
    return [ x.to_dict() for x in self.__d__.values() ]
  
  def get_dropdown(self, **filters):
    ret = [ (f"{x.lastname}, {x.firstname}", x.employee_id) for x in sorted(self.__d__, key=attrgetter('lastname', 'firstname')) ]
    return ret

  def delete(self, employee_ids):
    try:
      num = anvil.server.call('Employees', 'delete_employees', employee_ids)
    except Exception as e:
      print(e)
      print("Error deleting employees!")
      num = 0
    self.load()
    return num

  def get_employee_view(self, brand, year):
    return anvil.server.call('Employees', 'get_employee_view', year=year, brand=brand)

  def get_position_view(self, brand, year):
    return anvil.server.call('Employees', 'get_position_view', year=year, brand=brand)

  def get_actuals_updated(self, brand, year):
    return anvil.server.call('Employees', 'get_actuals_updated', brand=brand, year=year)

  def refresh_cache(self):
    return anvil.server.call('Employees', 'refresh_cache')

  def get_annual_summary(self, brand, year):
    return anvil.server.call('Employees', 'get_annual_summary', brand=brand, year=year)

EMPLOYEES = Employees()
#EMPLOYEES.load()