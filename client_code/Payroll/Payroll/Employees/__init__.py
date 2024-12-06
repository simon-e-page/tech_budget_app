from ._anvil_designer import EmployeesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ....Data import PositionsModel, EmployeesModel
from .... import Data
from ..Position import Position
from ..Employee import Employee

COLORS={
  'active': '#ffffcc',
  'inactive': 'grey',
  'forecast': '#ccffcc'
}

class Employees(EmployeesTemplate):
  def __init__(self, **properties):
    self.employees = EmployeesModel.EMPLOYEES
    self.positions = PositionsModel.POSITIONS
    
    self.year = Data.CURRENT_YEAR
    self.year_months = [ (self.year - (x>6))* 100 + x for x in [ 7,8,9,10,11,12,1,2,3,4,5,6 ]  ]

    self.employees_table.options = {
      "index": "employee_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      "pagination": True,
      "paginationSize": 5,
      #"frozenRows": 0,
      #"height": "50vh",
      #'autoResize': False,
    }

    self.get_data()
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def get_data(self):
    #self.data = self.employees.all()
    self.data = self.employees.get_employee_view(brand=Data.CURRENT_BRAND, year_months=self.year_months)
    
  def rebuild_table(self, set_focus=None):
    current_page = self.employees_table.get_page()
    self.employees_table_table_built()
    self.employees_table.set_page(current_page)
    
    if set_focus is not None:
      index, column = set_focus
      self.employees_table.scrollToColumn(column, 'middle')

  def employees_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""

    def change_assignment(sender, **event_args):
      print(f"Got assignment change for {sender.tag}")
      assignment = sender.tag
      #all_ids = self.po_index.keys()
      #print(f"All IDS: {all_ids}")
      self.open_assignment_form(assignment)

    def open_employee(sender, **event_args):
      cell = sender.tag
      employee_id = cell.get_value()
      print(f"Opening employee: {employee_id}")
      employee = self.employees.get(employee_id)
      emp_form = Employee(item=employee)
      result = emp_form.show()
      
    def emp_formatter(cell, **params):
      val = cell.get_value()
      link = Link(text=val, tag=cell)
      link.add_event_handler('click', open_employee)
      return link

    def cost_formatter(cell, **params):
      # Each value should be a dict with the following keys: amount, position_id, prev_position_id, cost_type, title
      # Where if position_id and prev_position_id differ then we know there is a new role for this employee in the period
      # The type field should be either 'actual', 'forecast', or 'unassigned' (is the last valid?)
      val = cell.get_value()
      data = cell.get_data()
      employee_id = data['employee_id']
      field = cell.get_field()
      cost = val['amount']
      position_id = val['position_id']
      title = val['title']
      prev_position_id = val['prev_position_id']
      cost_type = val['cost_type']
      
      tag = {
        'employee_id': employee_id,
        'position_id': position_id,
        'year_month': int(field)
      }

      if position_id != prev_position_id:
        icon = 'fa:star'
      else:
        icon = None

      background = COLORS.get(cost_type, 'white')
      
      label = Link(text=f"{cost:,.0f}", icon=icon, tag=tag, tooltip=title, background=background)
      label.add_event_handler('click', change_assignment)
      return label

    columns = [
      {
        "title": "ID",
        "field": "employee_id",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        'width': 100,
        "formatter": emp_formatter
      },
      {
        "title": "Lastname",
        "field": "lastname",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        "width": 200
      },
      {
        "title": "First Name",
        "field": "firstname",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        "width": 200
      },
      {
        "title": "Gender",
        "field": "gender",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        "width": 60        
      },
    ]

    cost_cols = [ {
        'title': str(year_month),
        'field': str(year_month),
        'formatter': cost_formatter,
        'width': 100
      } for year_month in self.year_months ]
    
    columns += cost_cols

    self.employees_table.columns = columns
    self.employees_table.data = self.data

  def open_assignment_form(self, assignment):
    position_id = assignment['position_id']
    employee_id = assignment['employee_id']
    year_month = assignment['year_month']
    brand = Data.CURRENT_BRAND
    
    position_list = [('Exit', 0)]
    # TODO: implement method to return vacant positions
    position_list += self.positions.get_vacant(brand, year_month)
    last_month = self.year_months[-1]
    index = self.year_months.index(year_month)
    remaining = self.year_months[index:]
    employee = self.employees.get(employee_id)

    form_title = f"Change assignment for {employee.full_name}"
    label1 = Label(text=f"From {year_month} to {last_month}")
    label2 = Label(text="Select new position or Exit: ")
    dd = DropDown(items=position_list, selected_value=position_id)

    panel = LinearPanel()
    panel.add_component(label1)
    fp = FlowPanel()
    fp.add_component(label2)
    fp.add_component(dd)
    panel.add_component(fp)

    result = alert(title=form_title, text=panel, large=True, buttons=[('OK', True), ('Cancel', False)])
    if result:
      new_position_id = dd.selected_value
      if new_position_id == 0:
        new_position_id = None
        # TODO: Catch errors..
        ok = self.employees.assign(employee_id, new_position_id, remaining)
        coord = (employee_id, str(year_month))
        self.rebuild_table(set_focus=coord)

