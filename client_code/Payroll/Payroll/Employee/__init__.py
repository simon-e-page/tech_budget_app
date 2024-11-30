from ._anvil_designer import EmployeeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ....Data import EmployeeModel

class Employee(EmployeeTemplate):
  def __init__(self, new=False, **properties):
    self.employees = EmployeeModel.EMPLOYEES
    self.new = new
    if new:
      self.item = self.employees.blank()
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
  def show(self):
    title = "Create New Employee" if self.new else "Edit Employee"
    ret = alert(self, buttons=[('Cancel', False)], large=True, title=title)
    if ret:
      pass      

  def save_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    try:
      self.item.save()
      self.raise_event('x-close-alert', True)
    except Exception as e:
      print(e)
      alert(f"Error wile saving: {e}")
      raise      
