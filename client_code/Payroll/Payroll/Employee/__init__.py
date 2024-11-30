from ._anvil_designer import EmployeeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ....Data import EmployeeModel
from ....Data.CrudForm import CrudForm

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
    editables = [
      { 'key': 'employee_id' },
      { 'key': 'firstname' },
      {'key': 'lastname' },
      {'key': 'gender', 'list': ['M', 'F'] },
      {'key': 'email' }
    ]
    
    crud_form = CrudForm(item=self.item, editables=editables)
    title = "Create New Employee" if self.new else "Edit Employee"
    ret = crud_form.show(title=title)
    print(ret)
    
#  def save_button_click(self, **event_args):
#    """This method is called when the button is clicked"""
#    try:
#      self.item.save()
#      self.raise_event('x-close-alert', True)
#    except Exception as e:
#      print(e)
#      alert(f"Error wile saving: {e}")
#      raise      
