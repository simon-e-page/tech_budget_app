from ._anvil_designer import EmployeesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ....Data import EmployeesModel


class Employees(EmployeesTemplate):
  def __init__(self, **properties):
    self.employees = EmployeesModel.EMPLOYEES

    self.employees_table.options = {
      "index": "employee_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      "pagination": False,
      "paginationSize": 250,
      "frozenRows": 0,
      "height": "50vh",
      #'autoResize': False,
      # "pagination_size": 10,
    }

    self.get_data()
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def get_data(self):
    self.data = self.employees.all()

  def employees_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    columns = [
      {
        "title": "Employee ID",
        "field": "employee_id",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Lastname",
        "field": "lastname",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "First Name",
        "field": "firstname",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
      {
        "title": "Gender",
        "field": "gender",
        "headerFilter": "input",
        "headerFilterFunc": "starts",
      },
    ]

    self.employees_table.columns = columns
    self.employees_table.data = self.data
