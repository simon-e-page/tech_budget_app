from ._anvil_designer import PositionsTemplate
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

class Positions(PositionsTemplate):
  def __init__(self, **properties):
    self.positions = PositionsModel.POSITIONS
    self.employees = EmployeesModel.EMPLOYEES
    
    self.po_index = self.positions.__d__
    self.year = Data.CURRENT_YEAR
    self.year_months = [ (self.year - (x>6))* 100 + x for x in [ 7,8,9,10,11,12,1,2,3,4,5,6 ]  ]
    
    self.positions_table.options = {
      "index": "position_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': True,
      'paginationSize': 5,
      #'frozenRows': 0,
      #'height': '30vh',
      #'autoResize': False,
      #"pagination_size": 10,
    }

    self.get_data()
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
  def get_data(self):
    self.data = self.employees.get_position_view(brand=Data.CURRENT_BRAND, year=self.year)

  
  def positions_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""

    def open_position(sender, **event_args):
      print(f"Got link for {sender.text}")
      cell = sender.tag
      data = cell.get_data()
      position_id = data['position_id']
      #all_ids = self.po_index.keys()
      #print(f"All IDS: {all_ids}")
      position = self.po_index[position_id]
      _form = Position(item=position)
      _form.show()

    def change_assignment(sender, **event_args):
        assignment = sender.tag
        employee_id = assignment['employee_id']
        if employee_id is not None:
            open_employee(sender)
        else:
            self.open_vacancy_form(assignment)

    def open_employee(sender, **event_args):
      assignment = sender.tag
      employee_id = assignment['employee_id']
      year_month = assignment.get('year_month', None)
      position_id = assignment.get('position_id', None)
      salary = assignment.get('salary')
      print(f"Opening employee: {employee_id}")
      employee = self.employees.get(employee_id)
      emp_form = Employee(item=employee, year_month=year_month, position_id=position_id, salary=salary)
      result = emp_form.show()
      
    def title_formatter(cell, **params):
      val = cell.get_value()
      link = Link(text=val, tag=cell)
      link.add_event_handler('click', open_position)
      return link

    def salary_formatter(cell, **params):
      # Each value should be a dict with the following keys: cost, employee_id, full_name, prev_employee_id, cost_type
      # Where if employee_id and prev_employee_id differ then we know there is a new employee in the position
      # Cost type: actual, forecast, costed vacancy, uncosted vacancy
      val = cell.get_value()
      #print(f"Formatting: {val}")
      year_month = cell.get_field()
      data = cell.get_data()
      position_id = data['position_id']
      title = data['title']
      amount = val['amount']
      salary = val['salary']
      employee_id = val.get('employee_id', None)
      full_name = val['full_name'] or None
      prev_id = val['prev_employee_id']
      cost_type = val['cost_type']
      background = COLORS.get(cost_type, 'white')
      
      tag = {
        'position_id': position_id,
        'year_month': int(year_month),
        'title': title,
        'employee_id': employee_id,
        'cost_type': cost_type,
        'salary': salary
      }

      # Idenfity if this column is a change in employment (or the first column)
      if employee_id != prev_id or year_month[4:] == '07':
        icon = "fa:user"
      else:
        icon = None
      
      cell.getElement().style.backgroundColor = background

      label = Link(text=f"{salary:,.0f}", icon=icon, tag=tag, tooltip=full_name )
      label.add_event_handler('click', change_assignment)
      return label
      
    columns = [
      {
        'title': 'Title',
        'field': 'title',
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        'width': 250,
        'formatter': title_formatter
      },
      {
        'title': 'Line Manager',
        'field': 'line_manager_title',
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        'width': 250
      },
      {
        'title': 'Team',
        'field': 'team',
        "headerFilter": "input",
        "headerFilterFunc": "contains",
      },
      {
        'title': 'Type',
        'field': 'role_type',
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        'title': 'Reason',
        'field': 'reaosn',
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      
    ]


    salary_cols = [ {
        'title': str(year_month),
        'field': str(year_month),
        'formatter': salary_formatter
      } for year_month in self.year_months ]
    
    columns += salary_cols
    #print(columns)
    
    self.positions_table.columns = columns
    self.positions_table.data = self.data

  def open_vacancy_form(self, assignment):
    # Only for unassigned (vacant) positions
    # Choice is between an costed and uncosted vacancy, and to set the salary
    # Costed vacancies are for expected start dates for new assignments / recruits
    position_id = assignment['position_id']
    year_month = assignment['year_month']
    position = self.positions.get(position_id)
    title = assignment['title']
    salary = position.get_salary(year_month)
    items = ['Uncosted vacancy', 'Costed Vacancy']
    last_month = self.year_months[-1]
    index = self.year_months.index(year_month)
    remaining = self.year_months[index:]

    
    form_title = f"Manage vacancy for {title}"
    label = Label(text=f"Period: From {year_month} to {last_month}")
    label2 = Label(text="Select vacancy type: ")
    dd = DropDown(items=items, selected_value=items[0])
    label3 = Label(text="Set Salary:")
    textbox = TextBox(text=salary if salary else 0, type='number')
    panel = LinearPanel()
    fp1 = FlowPanel()
    fp1.add_component(label2)
    fp1.add_component(dd)
    fp2 = FlowPanel()
    fp2.add_component(label3)
    fp2.add_component(textbox)
    panel.add_component(label)
    panel.add_component(fp1)
    panel.add_component(fp2)

    result = alert(content=panel, title=form_title, large=True, buttons=[('OK', True), ('Cancel', False)])
    if result:
      new_salary = int(textbox.text)
      if new_salary != salary:
        position.set_salary(new_salary, remaining)
      if dd.selected_value == 'Uncosted vacancy':
        position.unassign(remaining)
      else:
        position.set_costed_vacancy(remaining)
    
