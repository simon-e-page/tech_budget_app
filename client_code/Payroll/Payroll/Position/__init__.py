from ._anvil_designer import PositionTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import Data
from ....Data.CrudForm import CrudForm
from ....Data.PositionsModel import POSITIONS


class Position(PositionTemplate):
  def __init__(self, new=False, year_month=None, save=True, **properties):
    self.positions = POSITIONS
    self.brand = Data.CURRENT_BRAND
    self.line_manager_titles = [ (x.title, x) for x in self.positions.get_line_managers() if x is not None ]
    #print(f"Titles: {self.line_manager_titles}")
    self.team_list = self.positions.get_teams()
    
    self.new = new
    self.save = save
    
    if year_month is not None:
      self.year_month = year_month
    else:
      self.year_month = (Data.CURRENT_YEAR -1) * 100 + 7
    self.salary = 0.0
    
    if new:
      self.item = self.positions.blank()
    else:
      self.item = properties['item']
      self.salary = self.item.get_salary(self.year_month)
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
  def show(self):
    editables = [
      { 
        'key': 'position_id', 
        'label': 'Position ID',
        'enabled': False
      },
      { 
        'key': 'title',
        'label': 'Title',
      },
      {
        'key': 'team',
        'label': 'Team',
        'list': self.team_list
      },
      {
        'key': 'line_manager',
        'label': 'Line Manager',
        'reference': 'title',
        'list': self.line_manager_titles
      },
      {
        'key': 'description',
        'label': 'Description',
        'type': 'area'
      },
      {
        'key': 'role_type',
        'label': 'Role Type',
        'list': ['Permanent', 'Part-time', 'Intern']
      },
      {
        'key': 'reason',
        'label': 'Reason',
        'list': ['Backfill', 'New', 'Intern']
      },
      {
        'key': 'recruitment_code',
        'label': 'Recruitment Code',
      },
      {
        'key': 'status',
        'label': 'Status',
        'list': ['active', 'inactive']
      },
      
    ]
    
    crud_form = CrudForm(item=self.item, editables=editables)
    
    fp1 = FlowPanel()
    if self.new:
      label_text = f"Set salary from {self.year_month}"
    else:
      label_text = f"Adjust salary for {self.item.title} from {self.year_month}:"
    label = Label(text=label_text)
    textbox = TextBox(text=self.salary, type='number', tag=self.salary)
    fp1.add_component(label)
    fp1.add_component(textbox)
    crud_form.add_component(fp1)
    
    save_button = Button(text='Save', icon='fa:save', role='primary-button', bold=True, tag=(crud_form, textbox))
    save_button.add_event_handler('click', self.save_button_click)
    fp2 = FlowPanel()
    fp2.add_component(save_button)
    crud_form.add_component(fp2)

    title = "Create New Position" if self.new else "Edit Position"
    ret = crud_form.show(title=title)
    if ret:
      return self.item, self.salary
    else:
      return None, None
    
  def save_button_click(self, sender, **event_args):
    crud_form, salary_box = sender.tag
    self.salary = salary_box.text
    
    if self.save:
      crud_form, salary_box = sender.tag
      self.save_position(crud_form, salary_box)
    else:
      crud_form.raise_event('x-close-alert', value=True)
    
    
  def save_position(self, crud_form, salary_box):
    try:
      if self.item.save():
        self.positions.add(self.item.position_id, self.item)
        
      if salary_box.text != salary_box.tag:
        year_months = [ (Data.CURRENT_YEAR - (x>6)) * 100 + x for x in [7,8,9,10,11,12,1,2,3,4,5,6]]
        index = year_months.index(self.year_month)
        remaining = year_months[index:]
        print(f"Salary updated to: {salary_box.text} for {remaining}")
        self.item.set_salary(salary_box.text, remaining)
      crud_form.raise_event('x-close-alert', value=True)
    except Exception as e:
      print(e)
      raise