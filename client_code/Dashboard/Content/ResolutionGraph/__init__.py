from ._anvil_designer import ResolutionGraphTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class ResolutionGraph(ResolutionGraphTemplate):
  """This 'ResolutionGraph' custom component accepts 'labels' and 'datasets' properties will take care of its own display.
  
  Component properties:
    labels: a list of dates in the form '%A, %d'
    datasets: list of data in the form:
              [{
                    'label': 'Resolved',
                    'backgroundColor': '#9389DF',
                    'borderColor': '#7D71D8',
                    'data': list of data e.g [1,0,1,2,3,4,5]
                },{
                    'label': 'Unresolved',
                    'backgroundColor': '#00FFAF',
                    'borderColor': '#00FFAF',
                    'data': list of data e.g [1,0,1,2,3,4,5]
                }]
  """
  
  def __init__(self, **properties):
    self._shown = False
    self.display_datasets = None
    self.labels = None
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
  @property
  def labels(self):
    return self.display_labels

  @labels.setter
  def labels(self, labels):
    self.display_labels = labels
    self.maybe_draw_chart()
    
  @property
  def datasets(self):
    return self.display_datasets

  @datasets.setter
  def datasets(self, datasets):
    self.display_datasets = datasets
    self.maybe_draw_chart()

  def form_show(self, **event_args):
    self._shown = True
    self.maybe_draw_chart()
    
  def maybe_draw_chart(self):
    if self.display_datasets is not None and self.display_labels is not None and self._shown:
      self.call_js('buildChart', self.display_datasets, self.display_labels)
