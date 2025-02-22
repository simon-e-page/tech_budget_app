from ._anvil_designer import PayrollImportTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import Data
from ....Data import EmployeesModel, PositionsModel, PayrollImporterModel
from ..Position import Position
from ....Tickets.BudgetLines.ImportActuals.ProgressForm import ProgressForm

COLORS = {
  'new': '#ccffcc',
  'existing': '#E7E7E7'
}

ICONS = {
  'new': 'fa:star',
  'existing': None
}

GENDERS = ['M', 'F']

class PayrollImport(PayrollImportTemplate):
  def __init__(self, **properties):
    self.employees = EmployeesModel.EMPLOYEES
    self.positions = PositionsModel.POSITIONS
    self.importer = PayrollImporterModel.PAYROLL_IMPORTER
    self.year = Data.CURRENT_YEAR
    self.year_months = [ (self.year - (x>6)) * 100 + x for x in [7,8,9,10,11,12,1,2,3,4,5,6] ]
    self.brand = Data.CURRENT_BRAND
    self.actuals_updated = self.employees.get_actuals_updated(self.brand, self.year)
    self.year_month = None
    
    if self.actuals_updated == 0:
      self.next_month = (self.year - 1)*100 + 7
    elif self.actuals_updated % 100 == 6:
      self.next_month = "N/A"
    else:
      index = self.year_months.index(self.actuals_updated)
      self.next_month = self.year_months[index+1]
      
    self.vacancies = [ ('Create New', 0) ]
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def show(self):
    res = alert(self, title='Import Actuals', buttons=[('Cancel', False)], large=True)
    if res:
      Notification("Import successful!").show()

  def get_input_box(self):
    input_box = TextBox(placeholder="Enter Password")
    label = Label(text="Excel Password: ")
    fp = FlowPanel()
    fp.add_component(label)
    fp.add_component(input_box)
    return fp, input_box
    
  def payroll_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    if file is None:
      return

    year_month = self.importer.check_brand(file.name)
    process = False
    
    if year_month is not None:
      if year_month == self.next_month:
        process = True
      elif self.next_month != "N/A" and year_month > self.next_month:
        print(f"{year_month} > {self.next_month}??")
        alert(f"File is for for a non-consecutive future month! Please choose a file for {self.next_month}")
      elif year_month in self.year_months and confirm(f"Importing this file for {year_month} will overwrite existing records. Are you sure?"):
        process = True
      else:
        alert("File is for a different year?!")
        process = False
        
    if process:
      input_form, input_box = self.get_input_box()
      result = alert(input_form, title='Enter password', buttons=[('OK', True), ('Cancel', False)], large=True)
      if result:
        password = input_box.text
      else:
        password = None
        
      self.year_month = year_month
      try:
        new_data = self.importer.parse(year_month, file, password=password)
        if new_data is None:
          raise ValueError("Error parsing file - wrong password?")
      except Exception as e:
        alert("Error parsing file - wrong password?")
        return None

        
      try:
        self.new_data = new_data
        self.employee_data = new_data['employees']
        self.totals = new_data['totals']
        self.costs = new_data['costs']
        self.unassigned = new_data['unassigned']
        if len(self.unassigned)>0:
          self.generate_vacancies()
          self.set_initial_table_data()
          self.render_unassigned_table()
        else:
          self.move_to_import_click()
      except Exception as e:
        alert(f"Error parsing import file! Message: {e}")
        print(e)
        
      #print(self.cost_centres)
    else:
      alert("Please choose another file!")

  def generate_vacancies(self):
    vacant_postions = [ self.positions.get(x) for x in  self.positions.get_vacant(self.brand, self.year_month) ]
    self.vacancies += [ (x.title, x) for x in vacant_postions ]


  def set_initial_table_data(self):
    data = [ x for x in self.employee_data if x['employee_id'] in self.unassigned ]
    for item in data:
      item['position'] = { 'choice': None, 'position': None }
    self.unassigned_table.data = data
    
  def render_unassigned_table(self):
    
    def position_selected(sender, **event_args):
      cell = sender.tag
      data = cell.get_data()
      employee_id = data['employee_id']
      choice = sender.selected_value
      print(f"Got action {choice} for {employee_id}")
      if choice == 0:
        new_position, new_salary = self.get_new_position()
        if new_position is not None:
          data['position']['position'] = new_position
          data['position']['choice'] = 'new'
          data['position']['salary'] = new_salary
      else:
          data['position']['position'] = sender.selected_value
          data['position']['choice'] = 'existing'
          data['position']['salary'] = None
          self.remove_vacancy(sender.selected_value)
      self.render_unassigned_table()
      
    def action_formatter(cell, **params):
      #TODO: how to reverse a choice?
      data = cell.get_data()
      position = data['position']['position']
      choice = data['position']['choice']
      if position is not None:
        icon = ICONS.get(choice, None)
        obj = Label(text=position.title, icon=icon)
        #cell.getElement().style.backgroundColor = COLORS[choice]
      else:
        obj = DropDown(items=self.vacancies, include_placeholder=True, placeholder='Select Position', tag=cell)
        obj.add_event_handler('change', position_selected)
      return obj

    def reset_action(sender, **event_args):
      cell = sender.tag
      data = cell.get_data()
      position = data['position']['position']
      choice = data['position']['choice']
      if choice == 'existing':
        self.add_vacancy(position)
      data['position'] = { 'position': None, 'choice': None }
      self.render_unassigned_table()
      
    def reset_formatter(cell, **params):
      data = cell.get_data()
      position = data['position'].get('position', None)
      if position is not None:
        icon = 'fa:undo'
        obj = Link(icon=icon, tag=cell)
        obj.add_event_handler('click', reset_action)
      else:
        obj = None
      return obj

    def id_formatter(cell, **params):
      employee_id = cell.get_value()
      data = cell.get_data()
      if self.employees.get(employee_id, default=None) is None:
        icon='fa:star'
        data['position']['employee'] = 'new'
      else:
        icon = None
        data['position']['employee'] = 'existing'
      obj = Label(text=employee_id, icon=icon)
      return obj

    def set_gender(sender, **event_args):
      sender.tag['gender'] = sender.selected_value
      
    def gender_formatter(cell, **params):
      data = cell.get_data()
      employee_id = data['employee_id']
      employee = self.employees.get(employee_id, default=None)
      if employee is None:
        gender = data.get('gender') or 'M'
        print(f"Gender value for {employee_id}: {gender}")
        obj = DropDown(items=GENDERS, selected_value=gender, tag=data)
        obj.add_event_handler('change', set_gender)
      else:
        data['gender'] = employee.gender
        obj = Label(text=employee.gender)
      return obj

    
    columns = [
      {
        'title': 'Employee ID',
        'field': 'employee_id',
        'formatter': id_formatter
      },
      {
        'title': 'Last Name',
        'field': 'lastname'
      },
      {
        'title': 'First Name',
        'field': 'firstname'
      },
      {
        'title': 'Gender',
        'field': 'gender',
        'formatter': gender_formatter
      },
      {
        'title': 'Action',
        'field': '',
        'formatter': action_formatter
      },
      {
        'title': 'Reset',
        'field': '',
        'formatter': reset_formatter
      },
    ]
    
    self.unassigned_table.columns = columns
    self.unassigned_table.data = self.unassigned_table.data

  def get_new_position(self):
    position_form = Position(new=True, year_month=self.year_month, save=False)
    return position_form.show()

  def add_vacancy(self, position):
    self.vacancies.append((position.title, position))
    
  def remove_vacancy(self, position):
    self.vacancies = [ x for x in self.vacancies if x[1] != position ]
    
  def move_to_import_click(self, **event_args):
    """This method is called when the button is clicked"""
    new_positions = {}
    new_assignments = {}
    new_employees = {}
    
    for emp in self.unassigned_table.data:
      if emp['position']['position'] is None:
        alert("Need to assign employees to a position to continue!")
        return
      elif emp['position']['choice'] == 'new':
        new_positions[emp['employee_id']] = {
          'position': emp['position']['position'],
          'salary': emp['position']['salary']
        }        
      else:
        new_assignments[emp['employee_id']] = {
          'position': emp['position']['position']
        }
        
      if emp['position']['employee'] == 'new':
        new_employees[emp['employee_id']] = emp
    
    finance_total = self.totals[str(self.year_month)]
    costs_total = sum(x[str(self.year_month)] for x in self.costs[str(self.year_month)] )

    if abs(costs_total - finance_total)<=1:
      message = f"""Ready to execute:
      - {len(new_employees)} employees to create
      - {len(new_positions)} new positions to create
      - {len(new_assignments)} assignments to existing vacancies
      - {len(self.costs[str(self.year_month)])} payroll entries to add
      Total payroll costs for {self.year_month}: {costs_total}
      """
      
      if confirm(message):
        results = {}
        results['New Employees'] = self.add_new_employees(new_employees)
        results['New Positions'] = self.add_new_positions(new_positions)
        results['Assignments'] = self.make_assignments(new_assignments)
        if not all(results.values()):
          error_message = [ f"Error in step: {k}\m" for k,v in results.items() if not v ]
          alert(f"Errors: {error_message}")
          return
        result = self.add_costs(self.costs[str(self.year_month)])
        if not result:
          alert(f"Error saving actuals for {self.year_month}!")
          return
        else:
          self.raise_event('x-close-alert',  value=True)
    else:
      message = f"Total as per payroll report: {finance_total}. Sum of employee costs: {costs_total}"
      alert(f"Costs do not match! {message}")
      return

  def add_new_positions(self, pos_dict):
    index = self.year_months.index(self.year_month)
    remaining = self.year_months[index:]
    ret = True
    try:
      for employee_id, info in pos_dict.items():
        position = info['position']
        new_id = position.save()
        if new_id is not None:
          position.set_salary(info['salary'], remaining)
          position.assign(employee_id, remaining)
          ret = ret and True
        else:
          ret = False
      
    except Exception as e:
      print(e)
      ret = False
    return ret

  def add_new_employees(self, emp_dict):
    ret = True
    try:
      for employee_id, info in emp_dict.items():
        employee = self.employees.blank()
        employee.brand = self.brand
        employee.employee_id = employee_id
        employee.firstname = info['firstname']
        employee.lastname = info['lastname']
        gender = info.get('gender')
        if gender is None:
          gender= 'M'
        employee.gender = gender
        new_id = employee.save()
        if new_id is not None:
          ret = ret and True
        else:
          ret = False
    except Exception as e:
      print(e)
      ret = False

    return ret

  
  def make_assignments(self, pos_dict):
    index = self.year_months.index(self.year_month)
    remaining = self.year_months[index:]
    ret = False
    try:
      for employee_id, info in pos_dict.items():
        position = info['position']
        pos_id = position.position_id
        if pos_id is not None:
          position.assign(employee_id, remaining)
      ret = True
    except Exception as e:
      print(e)
    return ret


  
  def add_costs(self, costs):
    progress = ProgressForm()
    progress.initiate(1, len(costs), 1)
    result = progress.begin(self.importer.background_bulk_actuals, self.year_month, costs)
    
    #for cost_entry in costs:
    #  employee_id = cost_entry['employee_id']
    #  amount = cost_entry[str(self.year_month)]
    #  employee = self.employees.get(employee_id)
    #  ret = ret and employee.add_actual(self.year_month, amount)
    return result
      
      