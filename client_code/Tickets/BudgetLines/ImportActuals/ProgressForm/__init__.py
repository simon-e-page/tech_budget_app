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


  def initiate(self, start, end, interval, callback_obj, callback_func):
    self.progress_bar.clear_progress()
    self.start = start
    self.current = start
    self.end = end
    self.progress_bar.value = 0
    self.interval = interval
    self.callback_obj = callback_obj
    self.callback_func = callback_func
    

  def begin(self):
    def update(sender, **event_args):
      new_val = Data.callback(self.callback_obj, self.callback_func)
      if new_val >= self.end:
        t.interval = 0
        self.raise_event("x-close-alert", value=1)
      else:
        self.current = new_val
        self.progress_bar.value = new_val
        self.refresh_data_bindings()
    
    t = Timer(interval=self.interval)
    t.add_event_handler('tick', update)
    self.flow_panel_1.add_component(t)

    ret = alert(self, dismissible=False, buttons=[])
    return ret
      