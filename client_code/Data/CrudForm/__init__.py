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
    self.item = properties.get('item', None)
    
    if self.editables is None:
      self.editables = [ { 'key': k } for k in self.item.keys() ]

    self.build_form()
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  
  def build_form(self):
    panel = LinearPanel()
      
    for editable in self.editables:
      k = editable['key']
      v = self.item[k]
      flow_panel = None
      label = editable.get('label', None)
      enabled = editable.get('enabled', True)

      params = { param: editable.get(param, None) for param in ['label', 'enabled', 'precision'] }
        
      if 'list' in editable:
        flow_panel = self.get_dropdown(k, v, editable['list'], **params)
        panel.add_component(flow_panel)

      elif v is None:
        flow_panel = self.get_textbox(k, v, box_type='text', **params)
        panel.add_component(flow_panel)

      elif 'type' in editable:
        flow_panel = self.get_textbox(k, v, box_type=type,**params)
        panel.add_component(flow_panel)
        
      elif isinstance(v, str):
        flow_panel = self.get_textbox(k, v, box_type='text', **params)
        panel.add_component(flow_panel)
        
      elif isinstance(v, int):
        flow_panel = self.get_textbox(k, v, box_type='number', **params)
        panel.add_component(flow_panel)
        
      elif isinstance(v, float):
        precision = editable.get('precision', 2)
        flow_panel = self.get_textbox(k, v, box_type='text', **params)
        panel.add_component(flow_panel)
        
      else:
        print(f"Got: {v} of type {type(v)}")
        pass

    save_button = Button(text='Save', icon='fa:save', role='primary-button')
    save_button.add_event_handler('click', self.save)
    flow_panel = FlowPanel()
    flow_panel.add_component(save_button)
    panel.add_component(flow_panel)
    
    self.add_component(panel)
    self.refresh_data_bindings()
    #return self
  
  def show(self, title=''):
    #self.build_form()
    ret = alert(self, title=title, large=True, buttons=[('Cancel', False)])
    return ret
  
  def get_textbox(self, k, v, box_type='text', **params ):
    label = params.get('label', None)
    enabled = params.get('enabled', True)
    precision = params.get('precision', None)
    
    if label is None:
      label = Label(text=f"{k}:")
    else:
      label = Label(text=label)
      
    placeholder = f"Enter {k}"
    format_string = "{0}"

    if precision is not None:
      format_string += f":,.{precision}f"
    if v is not None:
      text = format_string.format(v) 
    else:
      text = None
      
    widget = TextBox(text=text, placeholder=placeholder, tag=k, type=box_type, enabled=enabled)
    
    def str_update_event(sender, **event_args):
      self.item[sender.tag] = sender.text

    widget.add_event_handler('lost_focus', str_update_event)
    fp = FlowPanel()
    fp.add_component(label)
    fp.add_component(widget)
    return fp


  def get_dropdown(self, k, v, items=None, label=None):
    if items is None:
      items = []

    if label is None:
      label = Label(text=f"{k}:")
    else:
      label = Label(text=label)
      
    placeholder = f"Enter {k}"
    selected_value = v
    widget = DropDown(items=items, selected_value=selected_value, placeholder=placeholder, include_placeholder=True)

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