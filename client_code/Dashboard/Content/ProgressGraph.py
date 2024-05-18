from ._anvil_designer import ProgressGraphTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class ProgressGraph(ProgressGraphTemplate):
  """This 'ProgressGraph' custom component accepts 'percentage' and (optional)'display_value' properties will take care of its own display.
  
  Component properties:
    percentage - float: percentage to be displayed
    display_value - integer: value to be displayed in the centre of the chart
  """
  
  def __init__(self, **properties):
    self._shown = False
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
  @property
  def percentage(self):
    return self.value

  @percentage.setter
  def percentage(self, percentage):
    self.value = percentage

  @property
  def display_value(self):
    return self.display

  @display_value.setter
  def display_value(self, value):
    self.display = value
    
  def form_show(self, **event_args):
    self._shown = True
    self.maybe_draw_chart()
    
  def maybe_draw_chart(self):
    if self.percentage is not None and self._shown:
      self.call_js('drawChart3', self.value, self.display)