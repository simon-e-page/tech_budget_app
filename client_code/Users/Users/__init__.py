from ._anvil_designer import UsersTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# import anvil.google.auth, anvil.google.drive
# from anvil.google.drive import app_files
import anvil.users

# import anvil.tables as tables
# import anvil.tables.query as q
# from anvil.tables import app_tables
import anvil.server
from datetime import datetime
from ...Data import UsersModel

from tabulator.Tabulator import row_selection_column

class Users(UsersTemplate):

  def __init__(self, **properties):
    self.users = UsersModel.USERS
    self.roles = UsersModel.ROLES

    self.selected_users = []
    self.selected_roles = []

    self.add_event_handler('x-refresh-tables', self.refresh_tables)
    self.init_components(**properties)

  def refresh_tables(self, *args, **kwargs):
    self.roles_table_table_built()
    self.users_table_table_built()
    
  def roles_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    self.roles_table.columns = [
      {"title": 'Role Name', "field": 'role_name' },
      {"title": 'Description' , "field": 'role_description', 'editor': 'input' },
      {"title": 'Create User' , "field": 'perm_create_user', 'editor': 'tickCross', 'formatter': 'tickCross' },
      {"title": 'Create Actuals' , "field": 'perm_create_actual', 'editor': 'tickCross', 'formatter': 'tickCross' },
      {"title": 'Create Vendors' , "field": 'perm_create_vendor', 'editor': 'tickCross', 'formatter': 'tickCross' },
      {"title": 'Create Budgets' , "field": 'perm_create_budget', 'editor': 'tickCross', 'formatter': 'tickCross' },
      {"title": 'Read Budgets' , "field": 'perm_read_budget', 'formatter': 'tickCross' },  
      {'title': '', 'field': 'delete', 'formatter': self.delete_formatter, 'formatterParams': {'key': 'role_name'}, 'width': 50 }
      
    ]
    
    self.roles_table.options = {
        "index": "role_name", # or set the index property here
        "selectable": "highlight",
    }
    
    self.roles_table.data = self.roles.to_records()

  def users_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""

    def date_formatter(cell, **params):
      val = cell.get_value()
      if val is None:
        return ''
      else:
        return val.strftime('%Y-%m-%d')
      
    listParams = {
      'values': list(self.roles.to_dict().keys())
    }
    
    self.users_table.columns = [
      {"title": 'Email', "field": 'email', 'headerFilter': 'input', 'headerFilterFunc': 'starts' },
      {"title": 'Full Name' , "field": 'full_name', 'editor': 'input' },
      {"title": 'Role' , "field": 'role_name', 'editor': 'list', 'editorParams': listParams },
      {"title": 'Team' , "field": 'team', 'editor': 'input' },
      {"title": 'Last Login' , "field": 'last_login', 'formatter': date_formatter },      
      {"title": 'Active' , "field": 'active', 'editor': 'tickCross', 'formatter': 'tickCross', 'width': 100 },
      {'title': '', 'field': 'delete', 'formatter': self.delete_formatter, 'formatterParams': {'key': 'email'}, 'width': 50 }
    ]
    
    self.users_table.options = {
        "index": "email", # or set the index property here
        "selectable": "highlight",
    }
    
    self.users_table.data = self.users.to_records()

  def users_table_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    data = dict(cell.getData())
    user = self.users.get(data['email'])
    user.update(data)
    user.save()
    
  def roles_table_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    data = dict(cell.getData())
    role = self.roles.get(data['role_name'])
    role.update(data)
    role.save()

  def delete_formatter(self, cell, **params):
    key = params['key']
    tag = cell.getData()[key]
    if key == 'email':
      table = self.users
      tablename = 'Users'
    else:
      table = self.roles
      tablename = 'Roles'
    
    def delete_tag(sender, **event_args):
      id_value = sender.tag
      if confirm(f"About to delete {id_value} from {tablename}! Are you sure?"):
        print(f"Deleting {id_value} from {tablename}")
        table.get(id_value).delete()
        self.refresh_data_bindings()
  
    link = Link(icon='fa:trash', tag=tag)
    link.set_event_handler('click', delete_tag)
    return link

  def delete_role_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    num_roles = len(self.selected_roles)
    if confirm(f"About to delete {num_roles} roles! Are you sure?"):
      for row in self.selected_roles:
        role = self.roles.get(dict(row.getData())['role_name'])
        role.delete()
      self.roles.load()
      self.roles_table_table_built()
      self.selected_roles = []
      self.refresh_data_bindings()  

  def delete_user_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    num_users = len(self.selected_users)
    if confirm(f"About to delete {num_users} users! Are you sure?"):
      for row in self.selected_users:
        user = self.users.get(dict(row.getData())['email'])
        user.delete()
      self.users.load()
      self.users_table_table_built()
      self.selected_users = []
      self.refresh_data_bindings()  
      
  def users_table_row_selection_changed(self, rows, data, **event_args):
    """This method is called when the row selection changes"""
    self.selected_users = rows
    self.refresh_data_bindings()

  def roles_table_row_selection_changed(self, rows, data, **event_args):
    """This method is called when the row selection changes"""
    self.selected_roles = rows
    self.refresh_data_bindings()
