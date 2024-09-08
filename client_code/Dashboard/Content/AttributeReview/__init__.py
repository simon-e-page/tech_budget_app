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
    self.attribute_label_text = "Attributes:"

    self.selected_vendor = None
    self.selected_attribute = None
    self.selected_value = None
    
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

  
  def value_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  
  def attribute_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.selected_attribute is not None:
      self.value_label_text = f"Values for {self.selected_attribute}"
      value_list = self.review_set[self.selected_vendor][self.selected_attribute]
      if len(value_list) == 0:
        value_list = Data.REFS[self.selected_attribute]
        self.value_label_text = f"Forecast has no value for {self.selected_attribute}. Please select one:"

      self.value_list = value_list
      self.refresh_data_bindings()
    else:
      self.value_list = []
      self.value_label_text = "Values"
      self.refresh_data_bindings()
    
