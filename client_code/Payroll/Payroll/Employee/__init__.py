from ._anvil_designer import EmployeeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ....Data import EmployeesModel, PositionsModel
from ....Data.CrudForm import CrudForm

class Employee(EmployeeTemplate):
  def __init__(self, new=False, **properties):
    self.employees = EmployeesModel.EMPLOYEES
    self.positions = PositionsModel.POSITIONS
    
    self.new = new
    self.year_month = properties.get('year_month', None)
    position_id = properties.get('position_id', None)
    self.salary = properties.get('salary', None)
    if position_id:
      self.position = self.positions.get(position_id)
    else:
      self.position = None
    
    if new:
      self.item = self.employees.blank()
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
  def show(self):
    editables = [
      { 
        'key': 'employee_id', 
        'label': 'Employee ID'
      },
      { 
        'key': 'firstname',
        'label': 'First name',
      },
      {
        'key': 'lastname',
        'label': 'Last name'
      },
      {
        'key': 'gender',
        'label': 'Gender',
        'list': ['M', 'F']
      },
      {
        'key': 'email',
        'label': 'Email Address:',
        'type': 'email'
      }
    ]
    
    crud_form = CrudForm(item=self.item, editables=editables)
    if not self.new and self.year_month and self.position is not None:
      title = self.position.title
      salary = self.salary
      fp1 = FlowPanel()
      label = Label(text=f"Adjust salary for {title} from {self.year_month}:")
      textbox = TextBox(text=salary, type='number', tag=salary)
      fp1.add_component(label)
      fp1.add_component(textbox)
      crud_form.add_component(fp1)
    else:
      textbox = None

    save_button = Button(text='Save', icon='fa:save', role='primary-button', bold=True, tag=(crud_form, textbox))
    save_button.add_event_handler('click', self.save)
    fp2 = FlowPanel()
    fp2.add_component(save_button)
    crud_form.add_component(fp2)
    
    #crud_form.build_form()
    title = "Create New Employee" if self.new else "Edit Employee"
    ret = crud_form.show(title=title)
    print(ret)

  def save(self, sender, **event_args):
    crud_form, salary_box = sender.tag
    try:
      self.item.save()
      
      new_salary = int(salary_box.text)
      if salary_box is not None and new_salary != salary_box.tag:
        month = self.year_month % 100
        year = (self.year_month // 100) + (month>6)
        year_months = [ (year - (x>6))*100+6 for x in [7,8,9,10,11,12,1,2,3,4,5,6] ]
        index = year_months.index(self.year_month)
        remaining = year_months[index:]
        self.position.set_salary(new_salary, remaining)
        print(f"Salary updated to {new_salary} for {remaining}")
        
      crud_form.raise_event('x-close-alert', value=True)
    except Exception as e:
      alert(f"Error saving object: {e}")
      print(e)
      raise    
