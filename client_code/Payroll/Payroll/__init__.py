from ._anvil_designer import PayrollTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server

import datetime as dt
from tabulator.Tabulator import row_selection_column

from ... import Data
from ...Data import EmployeesModel
from ...Data import PositionsModel
from .Employee import Employee
from .Position import Position
from .PayrollImport import PayrollImport

class Payroll(PayrollTemplate):
  def __init__(self, **properties):
    self.employees = EmployeesModel.EMPLOYEES
    self.positions = PositionsModel.POSITIONS
    self.year = Data.CURRENT_YEAR
    #self.employees.load()
    #self.positions.load()
    
  def add_employee_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    _form = Employee(new=True)
    _form.show()
    
  def add_position_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    _form = Position(new=True)
    _form.show()
    pass

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    import_form = PayrollImport()
    import_form.show()

  def button_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.employees.refresh_cache()

  def update_budget_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if confirm(f'Update all actuals and forecasts for each month in {self.year}?'):
      Data.update_payroll_budget(self.year)
