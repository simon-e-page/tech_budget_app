from ._anvil_designer import EmployeeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ....Data import EmployeeModel

class Employee(EmployeeTemplate):
  def __init__(self, **properties):
    self.employees = EmployeeModel.EMPLOYEES
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
  def show(self, new=False):
    title = "Create New Employee" if new else "Edit Employee"
    ret = alert(self, buttons=[('Cancel', False)], large=True, title=title)

    if ret:
      self.employees.save(self.item)
      
  def save_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
