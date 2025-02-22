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
    self.orig_set = {}
    self.review_set = {}
    self.new_set = {}
    
    self.vendor_list = []
    self.attribute_list = []
    self.value_list = []
    self.value_label_text = "Values:"
    self.value_label.visible = False
    self.cost_centre_table.visible = False
    self.attribute_label_text = "Attributes:"

    self.selected_vendor = None
    self.selected_attribute = None
    self.selected_value = None

    self.vendor_changed = False
    
    self.value_table.options = {
      "index": "value",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': False,
    }

    self.cost_centre_table.options = {
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
    self.orig_set = Data.assign_actual_dimensions()
    self.vendor_list = sorted(list(self.orig_set.keys()))
    self.refresh_data_bindings()
    ret = alert(self, large=True, title="Review: Attribute discrepancies between Forecast and Actuals by Vendor")

  
  def vendor_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    if not self.vendor_changed or confirm("Changed will be lost?"):
      self.value_label_text = "Values:"
      self.value_table.visible = False
      self.vendor_changed = False
      
      if self.selected_vendor is not None:
        cc = self.orig_set[self.selected_vendor]['cost_centre']
        forecast_total = sum(x[0] for x in cc.values())
        actual_total = sum(x[1] for x in cc.values())

        cost_centre_list = { x: [ 
          round(y[0] / forecast_total, 2) if forecast_total != 0 else 0,
          round(y[1] / actual_total, 2) if actual_total != 0 else 0,
        ] for x,y in  cc.items() }
         
        self.attribute_list = sorted(x for x in self.orig_set[self.selected_vendor].keys() if x not in ['cost_centre', 'forecast_ids', 'actual_ids'])
        self.review_set[self.selected_vendor] = self.review_set.get(self.selected_vendor, {}) 
        self.new_set[self.selected_vendor] = self.new_set.get(self.selected_vendor, {}) 

        for attribute in self.attribute_list:
          value_splits = self.orig_set[self.selected_vendor][attribute]        
          temp_list = { x: value_splits.get(x, [0.0, 0.0]) for x in Data.REFS[attribute] }
          forecast_total = sum(x[0] for x in temp_list.values())
          actual_total = sum(x[1] for x in temp_list.values())
  
          value_list = { x: [
            round(y[0] / forecast_total, 2) if forecast_total != 0 else 0,
            round(y[1] / actual_total, 2) if actual_total != 0 else 0,
          ] for x,y in temp_list.items() }
  
          review_list = value_list.copy()
          
          self.review_set[self.selected_vendor][attribute] = review_list
          self.new_set[self.selected_vendor][attribute] = value_list
        
        self.render_value_table(self.cost_centre_table, cost_centre_list, edit=False)
        self.attribute_label_text = f"Attributes for {self.selected_vendor}"
        self.refresh_data_bindings()
        
      else:
        self.value_list = []
        self.attribute_list = []
        self.attribute_label_text = "Attributes:"
        self.cost_centre_table.visible = False
        self.refresh_data_bindings()


  

  
  
  def attribute_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.selected_attribute is not None:
      review_list = self.review_set[self.selected_vendor][self.selected_attribute]
      value_list = self.new_set[self.selected_vendor][self.selected_attribute]
      value_splits = self.orig_set[self.selected_vendor][self.selected_attribute]
      
      if len(value_splits) > 0:
        self.value_label_text = f"Forecast has {len(value_splits)} values for {self.selected_attribute}. Confirm or change splits:"
      else:
        self.value_label_text = f"Forecast has no values for {self.selected_attribute}. Select one or more splits:"

      self.value_label.visible = True
      self.render_value_table(self.value_table, value_list, old_values=review_list)
      self.review_changed()
      self.refresh_data_bindings()
    else:
      self.value_table.visible = False
      self.value_label.visible = False
      self.refresh_data_bindings()
    

  
  def render_value_table(self, table, values, old_values={}, edit=True):
    
    def percent_formatter(cell, **params):
      val = cell.get_value()
      field = cell.get_field()
      formatted_value = "{:.1%}".format(val)
      return formatted_value

    
    columns = [
      {
        'title': "Value",
        'field': 'value',
        'width': 250
      },
      {
        'title': "Forecast Split",
        'field': "forecast_percent",
        'width': 150,
        'formatter': percent_formatter,
        'editor': 'range' if edit else None,
        'editorParams': { 'min': 0, 'max': 1, 'step': 1 }
      },
      {
        'title': "Actual Split",
        'field': "actual_percent",
        'width': 150,
        'formatter': percent_formatter,
        'editor': 'range' if edit else None,
        'editorParams': { 'min': 0, 'max': 1, 'step': 1 }
      }
    ]

    
    data = [ { 
      'value': x,
      'forecast_percent': y[0],
      'actual_percent': y[1],
      'old_forecast_percent': old_values.get(x, [None, None])[0],
      'old_actual_percent': old_values.get(x, [None, None])[1],
    } for x,y in values.items() ]

    forecast_percent_total = sum(x['forecast_percent'] for x in data)
    actual_percent_total = sum(x['actual_percent'] for x in data)
    self.error_label.visible = (forecast_percent_total != 1) or (actual_percent_total != 1)

    
    def table_cell_edited(cell, **event_args):
      """This method is called when a cell is edited"""
      this_row = cell.get_data()
      field = cell.getField()
      value = this_row['value']
      percent = cell.get_value()
      new_percents = [ float(this_row['forecast_percent']), float(this_row['actual_percent']) ]      
      self.new_set[self.selected_vendor][self.selected_attribute][value] = new_percents
      
      old_percent = this_row[f"old_{field}"]
      #print(f"{percent} compared to {old_percent}")
      if (old_percent is not None) and (old_percent != percent):
        cell.getElement().style.backgroundColor = "yellow"

      index = 0 if field == 'forecast_percent' else 1
      total = sum(x[index] for x in self.new_set[self.selected_vendor][self.selected_attribute].values())
      self.error_label.visible = (total != 1.00)
      self.review_changed()
      self.refresh_data_bindings()

    
    table.columns = columns
    table.data = data
    table.add_event_handler("cell_edited", table_cell_edited)
    table.visible = True
    self.review_changed()
    self.refresh_data_bindings()

              
  
  def review_changed(self):
    review_list = self.review_set[self.selected_vendor]
    new_list = self.new_set[self.selected_vendor]
    changed = False
    wrong_totals = False
    
    for attribute, values in new_list.items():
      diffs = any(y[i] - review_list[attribute][x][i] for x, y in values.items() for i in [0,1])
      try:
        changed = changed or diffs
      except Exception as e:
        changed = True
      total = sum(y[i] for x,y in values.items() for i in [0,1])
      wrong_totals = wrong_totals or (total != 2.0)

    self.vendor_changed = changed
    self.error_label.visible = wrong_totals

        

  def apply_actuals_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    splits = self.new_set[self.selected_vendor]
    forecast_ids = self.orig_set[self.selected_vendor]['forecast_ids']
    actual_ids = self.orig_set[self.selected_vendor]['actual_ids']
    
    message = f"Updated attributes ({', '.join(splits.keys())}) for {self.selected_vendor} for all Forecast and Actual Lines"    
    
    if self.update(self.selected_vendor, forecast_ids, actual_ids, splits):
      Notification(message=message, title="Update successful!").show()
      update_set = Data.assign_actual_dimensions(selected_vendor_name=self.selected_vendor)
      if self.selected_vendor in update_set:
        self.orig_set[self.selected_vendor] = update_set[self.selected_vendor]
      else:
        self.orig_set.pop(self.selected_vendor, None)

      # TODO: move into a initial setup routine!
      self.selected_vendor = None
      self.selected_attribute = None
      self.value_table.visible = False
      self.cost_centre_table.visible = False
      self.value_label_text = ""
      self.attribute_label_text = "Attributes:"
      self.attribute_list = []        
      self.vendor_list = sorted(list(self.orig_set.keys()))
      self.vendor_changed = False
      self.refresh_data_bindings()
    else:
      alert("Update failed - check logs!")
      

  def update(self, vendor_name, forecast_ids, actual_ids, splits):
    return Data.apply_attribute_splits(vendor_name, forecast_ids, actual_ids, splits)
  
    
    
   