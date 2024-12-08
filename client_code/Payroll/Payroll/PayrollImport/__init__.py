from ._anvil_designer import PayrollImportTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import Data
from ....Data import EmployeesModel, PositionsModel, PayrollImporterModel

class PayrollImport(PayrollImportTemplate):
  def __init__(self, **properties):
    self.employees = EmployeesModel.EMPLOYEES
    self.positions = PositionsModel.POSITIONS
    self.importer = PayrollImporterModel.PAYROLL_IMPORTER
    self.year = Data.CURRENT_YEAR
    self.year_months = [ (self.year - (x>6)) * 100 + x for x in [7,8,9,10,11,12,1,2,3,4,5,6] ]
    self.brand = Data.CURRENT_BRAND
    self.actuals_updated = self.employees.get_actuals_updated(self.brand, self.year)
    
    if self.actuals_updated == 0:
      self.next_month = (self.year - 1)*100 + 7
    elif self.actuals_updated % 100 == 6:
      self.next_month = "N/A"
    else:
      index = self.year_months.index(self.actuals_updated)
      self.next_month = self.year_months[index+1]
      
      
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def payroll_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    year_month = self.importer.check_brand(file.name)
    process = False
    
    if year_month is not None:
      if year_month == self.next_month:
        process = True
      elif year_month > self.next_month:
        print(f"{year_month} > {self.actuals_to_date}??")
        alert(f"File is for for a non-consecutive future month! Please choose a file for {self.next_month}")
      elif year_month == self.actuals_to_date and confirm("Importing this file will overwrite existing records. Are you sure?"):
        process = True
      elif confirm(f"File is for a previous month. Proceeding will delete all months after {year_month}. Are you sure?"):
        process = True
        
    if process:
      #try:
      new_data = self.importer.parse(year_month, file)
      try:
        self.new_data = new_data
        self.employees = new_data['employees']
        self.total = new_data['totals']
        self.costs = new_data['costs']
        self.unassigned = new_data['unassigned']
        self.render_unassigned_table()
      except Exception as e:
        alert(f"Error parsing import file! Message: {e}")
        print(e)
        
      #print(self.cost_centres)
    else:
      alert("Please choose another file!")

  def render_unassigned_table(self):
    def position_selected(sender, **event_args):
      cell = sender.tag
      employee_id = cell.get_data()['employee_id']
      action = sender.selected_value
      print(f"Got action {action} for {employee_id}")
      
    def action_formatter(cell, **params):
      items = [ ('Create New', 0) ]
      dd = DropDown(items=items, include_placeholder=True, placeholder='Select Position', tag=cell)
      dd.add_event_handler('change', position_selected)
      return dd
      
    columns = [
      {
        'title': 'Employee ID',
        'field': 'employee_id'
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
        'title': 'Action',
        'field': '',
        'formatter': action_formatter
      },
    ]
    data = [ x for x in self.employees if x['employee_id'] in self.unassigned ]
    self.unassigned_table.columns = columns
    self.unassigned_table.data = data