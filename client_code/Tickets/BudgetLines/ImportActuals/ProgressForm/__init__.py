from ._anvil_designer import ProgressFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..... import Data

class ProgressForm(ProgressFormTemplate):
  def __init__(self, **properties):
    self.current = 0
    self.end = 100
    # Set Form properties and Data Bindings.
    self.init_components(**properties)


  def initiate(self, start, end, interval):
    self.progress_bar.clear_progress()
    self.start = start
    self.current = start
    self.end = end
    self.progress_bar.value = 0
    self.interval = interval
    self.refresh_data_bindings()
    

  def begin(self, background_func, *args, **kwargs):
    def update(sender, **event_args):
      try:
        status = task.get_termination_status()
        if status is None:
          state_object = task.get_state()
          if state_object is not None:
            new_val = state_object.get('row_count')
          else:
            print("No state object!")
            new_val = self.end

          perc_complete = new_val / self.end * 100
          self.current = new_val
          self.progress_bar.value = perc_complete
          self.refresh_data_bindings()
          
        elif status == "completed":
          t.interval = 0
          entry_count = task.get_return_value()
          self.raise_event("x-close-alert", value=entry_count)
        elif status == "failed":
          print("Background error!")
          task.get_error()
          t.interval = 0
          self.raise_event("x-close-alert", value=0)
        else:
          print(f"Error? {status}")
          
          t.interval = 0
          self.raise_event("x-close-alert", value=0)
      except Exception as e:
        print(e)
        self.raise_event("x-close-alert", value=0)

    task = background_func(*args, **kwargs)
    
    t = Timer(interval=self.interval)
    t.add_event_handler('tick', update)
    self.flow_panel_1.add_component(t)

    ret = alert(self, dismissible=False, buttons=[])
    return ret
      