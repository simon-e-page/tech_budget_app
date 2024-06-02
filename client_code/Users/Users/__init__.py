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
from ... import Data

class Users(UsersTemplate):
  """This Form displays transaction and account information for a single transaction. It also allows you to edit the transaction being displayed.

  Keyword Arguments:
    item - a row from the 'Transaction' Data Table
    back - a dictionary containg the form to open and the filters to apply when back is clicked

  A copy of this row from the 'Transaction' table is initialised as self.transaction_copy in form_refreshing_data_bindings()
  """

  def __init__(self, **properties):
    self.users = Data.USERS
    self.roles = Data.ROLES
    self.init_components(**properties)

  def roles_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    self.roles_table.columns = [
      {"title": 'Role Name', "field": 'role_name' },
      {"title": 'Description' , "field": 'role_description' },
      {"title": 'Create User' , "field": 'perm_create_user' },
      {"title": 'Create Actuals' , "field": 'perm_create_actual' },
      {"title": 'Create Vendors' , "field": 'perm_create_vendor' },
      {"title": 'Create Budgets' , "field": 'perm_create_budget' },
      {"title": 'Read Budgets' , "field": 'perm_read_budget' },    
    ]
    
    self.roles_table.options = {
        "index": "role_name", # or set the index property here
    }
    
    self.roles_table.data = self.roles.to_records()

  def users_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    self.users_table.columns = [
      {"title": 'Email', "field": 'email' },
      {"title": 'Full Name' , "field": 'full_name' },
      {"title": 'Role' , "field": 'role_name' },
      {"title": 'Team' , "field": 'team' }
    ]
    
    self.users_table.options = {
        "index": "email", # or set the index property here
    }
    
    self.users_table.data = self.users.to_records()
