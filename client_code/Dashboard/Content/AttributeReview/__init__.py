from ._anvil_designer import AttributeReviewTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import Data

class AttributeReview(AttributeReviewTemplate):
  def __init__(self, **properties):
    self.review_set = {}
    self.vendor_list = []
    self.attribute_list = []
    self.value_list = []
    self.value_label_text = "Values:"
    self.value_label.visible = False
    self.attribute_label_text = "Attributes:"

    self.selected_vendor = None
    self.selected_attribute = None
    self.selected_value = None

    self.value_table.options = {
      "index": "value",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': False,
    }

    self.value_table.visible = False
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def show(self):
    self.review_set = Data.assign_actual_dimensions()
    self.vendor_list = sorted(list(self.review_set.keys()))
    self.refresh_data_bindings()
    ret = alert(self, large=True, title="Review: Multiple Attributes per Vendor:")

  
  def vendor_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.selected_vendor is not None:
      self.attribute_list = sorted(list(self.review_set[self.selected_vendor].keys()))
      self.attribute_label_text = f"Attributes for {self.selected_vendor}"
      self.refresh_data_bindings()
    else:
      self.value_list = []
      self.attribute_list = []
      self.attribute_label_text = "Attribtues:"
      self.value_label_text = "Values:"
      self.refresh_data_bindings()

  
  def apply_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.selected_value is not None:
      value_list = self.review_set[self.selected_vendor][self.selected_attribute]
      if len(value_list) == 0:
        title = f"Setting {self.selected_attribute} for {self.selected_vendor} to {self.selected_value} for all Actual and Forecast Lines!"
        set_forecast = True
      else:
        title = f"Setting {self.selected_attribute} for {self.selected_vendor} to {self.selected_value} for all Actual Lines!"
        set_forecast = False
        
      alert(title)

  
  
  def attribute_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.selected_attribute is not None:
      value_splits = self.review_set[self.selected_vendor][self.selected_attribute]
      value_list = { x: value_splits.get(x, 0.0) for x in Data.REFS[self.selected_attribute] }
      if len(value_splits) > 0:
        self.value_label_text = f"Forecast has {len(value_splits)} values for {self.selected_attribute}. Confirm or change splits:"
      else:
        self.value_label_text = f"Forecast has no values for {self.selected_attribute}. Select one or more splits:"

      self.value_label.visible = True
      self.render_value_table(value_list)
      self.refresh_data_bindings()
    else:
      self.value_table.visible = False
      self.value_label.visible = False
      self.refresh_data_bindings()
    

  def render_value_table(self, values):
    
    def percent_formatter(cell, **params):
      val = cell.get_value()
      val = "{:.1%}".format(val)
      return val
      
    columns = [
      {
        'title': "Value",
        'field': 'value',
        'width': 250
      },
      {
        'title': "Percentage",
        'field': "percent",
        'width': 150,
        'formatter': percent_formatter,
        'editor': 'number'
      }
    ]

    total = sum(values.values())
    self.data = [ { 
      'value': x,
      'amount': y,
      'percent': y / total if total != 0 else 0
    } for x,y in values.items() ]

    self.value_table.columns = columns
    self.value_table.data = self.data
    self.value_table.visible = True

  def value_table_cell_edited(self, cell, **event_args):
    """This method is called when a cell is edited"""
    data = cell.get_data()
    value = data['value']
    old_percent = None
    total = 0.0
    for row in self.data:
      total += row['percent']
      if row['value'] == value:
        percent = row['percent']
      

    percentage = cell.get_value()    
    print(f"Internal percent = {percent}. New value = {percentage}")

    
    
   