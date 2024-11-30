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


class Payroll(PayrollTemplate):
  def __init__(self, **properties):

  def add_employee_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def add_position_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
