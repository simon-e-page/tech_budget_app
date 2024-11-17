from ._anvil_designer import ImportBudgetTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import Data
from ....Data import ImporterModel

# TODO: add a create from Forecast option

class ImportBudget(ImportBudgetTemplate):
  def __init__(self, **properties):
    self.importer = ImporterModel.IMPORTER
    self.brand = Data.CURRENT_BRAND
    self.show_forecast = True
    self.show_import = True
    self.item = None
    self.year = None
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def show(self, year, show_forecast=True, show_import=True):
    self.year = year
    self.show_forecast = show_forecast
    self.show_import = show_import
    self.refresh_data_bindings()
    result = alert(self, buttons=[('Cancel', False)])
    if result:
      pass
      
  def budget_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""    
    
    result = self.importer.brand_import_data(
      self.brand, 
      self.year, 
      excel_file=self.budget_loader.file
    )
    
    if result is not None:
      self.item['new_vendors'], self.item['import_data'] = result
    else:
      alert("Could not parse file!")
      return
      
    self.vendor_table.build_vendor_table(self.item['new_vendors'])
    self.vendor_panel.visible = True
    self.refresh_data_bindings()

  def render_transaction_review_table(self, vendor_map=None):
    #fin_year = self.year

    # TODO: add 'new' attribute to each row if the Vendor is to be created
    def sub(row):
      """ Replaced the vendor_name in an import row with either the automated or manual mapping replacements """
      import_vendor_name = row['vendor_name']
      import_vendor_id = row['vendor_id']
      new_row = row.copy()
      if import_vendor_id != 0:
        new_row['vendor_name'] = self.vendors.get(import_vendor_id)['vendor_name']
      else:
        new_row['vendor_name'] = vendor_map.get(import_vendor_name, import_vendor_name)
      return new_row
      
    self.item['final_import_data'] = [ sub(x) for x in self.item['import_data']]
          
    self.budget_line_table.import_data = self.item['final_import_data']
    self.import_total, num_of_lines = self.budget_line_table.build_entry_table(vendor_map)
    self.import_panel.visible = True
    self.refresh_data_bindings()
  

  def to_line_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.item['new_vendors'] = self.vendor_table.get_data()
    result, new_vendor_names, vendor_map, vendor_aliases = self.vendor_table.check_vendor_table()

    # These are ready to submit to the final import
    self.new_vendor_names = new_vendor_names
    self.vendor_aliases = vendor_aliases

    if result:
      self.vendor_panel.visible = False
      #self.new_data['new_vendors'] = self.new_vendors
      self.render_transaction_review_table(vendor_map=None)
    pass

  def to_vendor_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.import_panel.visible = False
    self.vendor_panel.visible = True

  def import_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.run_import()
    self.raise_event("x-close-alert", value=True)

  def run_import(self):
    new_vendor_names = self.new_vendor_names
    vendor_aliases = self.vendor_aliases
    transactions_with_entries = self.item['final_import_data']

    #print("New vendors to create:")
    #print(new_vendor_names)
    #print("Existing vendors to modify:")
    #print(vendor_aliases)
    #print("Transaction Lines to create:")
    #print(transactions_with_entries)
    #result = False
    result = self.importer.import_first_budget(
                                               fin_year=self.year,
                                               new_vendor_names=new_vendor_names, 
                                               vendor_aliases=vendor_aliases, 
                                               transactions_with_entries=transactions_with_entries
                                              )
    if not result:
        alert(f"Failed to create first Budget for Brand: {self.item['code']}")          
        return False
    else:
      print(f"{result} entries created")
    pass

  def generate_radio_change(self, **event_args):
    """This method is called when this radio button is selected (but not deselected)"""
    result = Data.create_new_budget(year=self.year)
    if result:
      self.raise_event('x-close-alert', value=result)
    else:
      alert("Operation failed! Check Logs!")
      
    
  def import_radio_change(self, **event_args):
    """This method is called when this radio button is selected (but not deselected)"""
    self.budget_loader.open_file_selector()

  def template_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass

  def to_choice_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.budget_loader.clear()
    self.generate_radio.selected = False
    self.import_radio.selected = False
    self.vendor_panel.visible = False
