import anvil.server
import anvil.users

from ..Data import AttributeToDict, AttributeToKey

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
      
  def load(self, _users=None):
    self.__d__ = {}
    if _users is None:
      _users = anvil.server.call('Users', 'search')
    for user in _users:
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

  def load(self, _roles=None):
    self.__d__ = {}
    if _roles is None:
      _roles = anvil.server.call('Users', 'get_roles')
    for role in _roles:
      self.new(role)

############
# MAIN
############

# TODO: Extract from Users!
OWNERS = ['SimonPage', 'AnitaMatuszewski']
OWNERS_DD = [ (x,x) for x in OWNERS ]

TEAMS = {
  'simon.page@jbhifi.com.au': ['Unknown', 'IT'],
  'anita,matuszewski@jbhifi.com.au': ['Unknown', 'Engineering', 'FOH', 'BOH', 'Commercial', 'Online', 'Core Retail'],
  'julie.chivers@jbhifi.com.au': ['Unknown', 'NCI - C', 'NCI - CIS', 'NCI - N', 'NCI - GRC', 'NCI - DSU'],
  'graham.wilson@jbhifi.com.au': ['Unknown', 'App Support', 'Store Support', 'Desktop'],
  'harrishaitidis@thegoodguys.com.au': ['Unknown', 'Data and Analytics'],
  'mariaalquiza@thegoodguys.com.au': ['Unknown', 'Finance'],
  'albertosimongini@thegoodguys.com.au': ['Unknown', 'Engineering', 'Online', 'Merch and Finance', 'Fulfilment', 'Selling']
}

TEAMS_DD = { k: [ (i, i) for i in v ] for k,v in TEAMS.items() }

USERS = Users()
ROLES = Roles()

