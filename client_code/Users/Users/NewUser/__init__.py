from ._anvil_designer import NewUserTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import Data

class NewUser(NewUserTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.user = {}
    self.role_obj = {}
    self.can_save = False
    self.roles = Data.ROLES
    self.users = Data.USERS
    
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def email_textbox_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.test_save()

  def save_user_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    new_email = self.user['email']
    if self.users.get(new_email) is not None:
      alert("Error: User already exists!")
    else:
      print(self.user)

  def test_save(self):
    self.save_user_button.enabled = self.user.get('email', None) and self.user.get('role_name', None)
    #self.refresh_data_bindings()

  def role_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.test_save()

  def role_name_textbox_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.save_role_button.enabled = (self.role_obj.get('role_name', None) is not None)

  def save_role_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    new_role = self.role_obj['role_name']
    if self.roles.get(new_role) is not None:
      alert("Error: Role already exists!")
    else:
      self.role_obj['perm_read_budget'] = True
      print(self.role_obj)
      