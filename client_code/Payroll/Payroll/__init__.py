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

class Payroll(PayrollTemplate):
  def __init__(self, **properties):
    self.employees = EmployeesModel.EMPLOYEES
    self.positions = PositionsModel.POSITIONS
    self.employees.load()
    self.positions.load()
    
  def add_employee_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    _form = Employee(new=True)
    _form.show()
    
  def add_position_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    _form = Position(new=True)
    _form.show()
    pass
