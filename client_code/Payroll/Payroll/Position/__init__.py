from ._anvil_designer import PositionTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ....Data.CrudForm import CrudForm
from ....Data.PositionsModel import POSITIONS


class Position(PositionTemplate):
  def __init__(self, new=False, year_month=None, **properties):
    self.positions = POSITIONS
    self.line_manager_titles = [ x.title for x in self.positions.get_line_managers() if x is not None ]
    print(f"Titles: {self.line_manager_titles}")
    
    self.new = new
    self.year_month = year_month
    
    if new:
      self.item = self.positions.blank()
    else:
      self.item = properties['item']
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
        'label': 'Team'
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
    
    save_button = Button(text='Save', icon='fa:save', role='primary-button', bold=True, tag=crud_form)
    save_button.add_event_handler('click', self.save)
    fp2 = FlowPanel()
    fp2.add_component(save_button)
    crud_form.add_component(fp2)

    title = "Create New Position" if self.new else "Edit Position"
    ret = crud_form.show(title=title)
    

  def save(self, sender, **event_args):
    crud_form = sender.tag
    try:
      self.item.save()
      crud_form.raise_event('x-close-alert', value=True)
    except Exception as e:
      print(e)
      raise