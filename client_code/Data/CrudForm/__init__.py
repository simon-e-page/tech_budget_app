from ._anvil_designer import CrudFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class CrudForm(CrudFormTemplate):
  def __init__(self, **properties):
    self.editables = properties.get('editables', None)
    if self.editables is None:
      self.editables = [ { 'key': k } for k in self.item.keys() ]
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  
  def build_form(self, item):
    panel = LinearPanel()
      
    for editable in self.editables:
      k = editable['key']
      v = self.item[k]
      flow_panel = None

      if 'list' in editable:
        flow_panel = self.get_dropdown(k, v, editable['list'])
        panel.add_component(flow_panel)
        
      elif isinstance(v, str):
        flow_panel = self.get_textbox(k, v)
        panel.add_component(flow_panel)
        
      elif isinstance(v, int):
        flow_panel = self.get_textbox(k, v, number=True)
        panel.add_component(flow_panel)
        
      elif isinstance(v, float):
        flow_panel = self.get_textbox(k, v, number=True)
        panel.add_component(flow_panel)
        
      else:
        pass

    save_button = Button(text='Save', icon='fa:save')
    save_button.add_event_handler('click', self.save)
    flow_panel = FlowPanel()
    flow_panel.add_component(save_button)
    panel.add_component(flow_panel)
    
    self.add_component(panel)
    self.refresh_data_bindings()
    return self
  
  def show(self, title=''):
    #self.build_form()
    ret = alert(self, title=title, large=True, buttons=[('Cancel', False)])
    return ret
  
  def get_textbox(self, k, v, number=False):
    label = Label(f"{k}:")
    placeholder = f"Enter {k}"
    box_type = 'numeric' if  number else None
    widget = TextBox(placeholder=placeholder, tag=k, type=box_type)
    def str_update_event(sender, **event_args):
      self.item[sender.tag] = sender.text
    widget.add_event_handler('lost_focus', str_update_event)
    fp = FlowPanel()
    fp.add_component(label)
    fp.add_component(widget)
    return fp


  def get_dropdown(self, k, v, items=None):
    if items is None:
      items = []

    label = Label(f"{k}:")
    placeholder = f"Enter {k}"
    widget = DropDown(items=items, placeholder=placeholder, include_placeholder=True)

    def dd_selected(sender, **event_args):
      self.itemp[sender.tag] = sender.selected_value

    widget.add_event_handler('change', dd_selected)
    fp = FlowPanel()
    fp.add_component(label)
    fp.add_component(widget)
    return fp

  
  def save(self):
    try:
      self.item.save()
      self.raise_event('x-close-alert', True)
    except Exception as e:
      alert(f"Error saving object: {e}")
      print(e)
      raise