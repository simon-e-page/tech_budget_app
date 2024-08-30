from ._anvil_designer import ReferenceTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ... import Data

class Reference(ReferenceTemplate):
  def __init__(self, **properties):
    self.attribute_name = None
    self.attribute_data = None
    self.attribute_names = Data.get_attribute_names()
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def attribute_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.attribute is not None:
      self.build_table()
    self.refresh_data_bindings()

  
  def build_table(self):
    
    def delete_formatter(cell, **params):
      tag = cell.getData()[self.attribute_name]
      count = cell.getData()['used']
      
      def delete_tag(sender, **event_args):
        id_value = sender.tag
        if confirm(f"About to delete {id_value} from {self.attribute_name}! Are you sure?"):
          print(f"Deleting {id_value} from {self.attribute_name}")
          Data.remove_attribute(self.attribute_name, id_value)
          #TODO: rebuild table          

      if not count:
        link = Link(icon='fa:trash', tag=tag)
        link.set_event_handler('click', delete_tag)
      else:
        link = Label(text='')
      return link
      
    columns = [
      {
        "title": "",
        "field": "delete",
        "formatter": delete_formatter, 
        "width": 50,
      },
      {
        "title": "Value",
        "field": "value",
        'width': 300,
        #"headerFilter": "input",
        #"headerFilterFunc": "starts",
      },      
      {
        "title": "Currently Used?",
        "field": "used",
        "formatter": "tickCross",
        'width': 50,
      }
        ]

    self.attribute_data = Data.get_attributes(self.attribute_name, with_count=True)
    self.attribute_table.columns = columns
    self.attribute_table.data = self.attribute_data

  def add_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    attribute_values = [ x['value'] for x in self.attribute_data ]
    new_value = self.attribute_value.text
    if new_value in attribute_values:
      alert("Already have this value!")
    elif confirm(f"About to add {new_value} as a value for {self.attribute_name}. Are you sure?"):
      Data.add_attribute(self.attribute_name, new_value)

  
  def attribute_value_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.refresh_data_bindings()
