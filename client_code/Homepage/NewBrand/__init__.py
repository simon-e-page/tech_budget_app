from ._anvil_designer import NewBrandTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from tabulator.Tabulator import row_selection_column

from ...import Data
from ...Data.ImporterModel import IMPORTER
from ...Data.VendorsModel import VENDORS

class NewBrand(NewBrandTemplate):
  def __init__(self, **properties):
    #self.item = properties['item']
    self.importer = IMPORTER
    self.vendors = VENDORS
    self.import_loader.enabled = False
    self.import_year = None
    self.import_lines = 0
    self.import_total = 0.0
    self.import_years = [ (str(x), x) for x in range(2023, 2030)]
    self.import_panel.visible = False
    self.vendor_panel.visible = False
    # Set Form properties and Data Bindings.

    self.import_table.options = {
      'selectable': "highlight",
      'pagination': True,
      'pagination_size': 10,
      'css_class': ["table-striped", "table-bordered", "table-condensed"]
    }

    self.vendor_table.options = {
      'selectable': "highlight",
      'pagination': True,
      'pagination_size': 10,
      'css_class': ["table-striped", "table-bordered", "table-condensed"]
    }
    
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def icon_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    self.item['icon_file'] = self.icon_loader.file
    self.refresh_data_bindings()



  
  def import_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""    
    
    result = self.importer.brand_import_data(
      self.item['code'], 
      self.import_year, 
      excel_file=self.import_loader.file
    )
    
    if result is not None:
      self.item['new_vendors'], self.item['import_data'] = result
    else:
      alert("Could not parse file!")
      
    self.vendor_table.build_vendor_table(self.item['new_vendors'])
    self.vendor_panel.visible = True
    self.refresh_data_bindings()


  
    
  
  def build_import_table(self, vendor_map):
    """ vendor_map should be a dictionary of replacement vendor_name for any vendors that are replaced on import """
    
    def total_formatter(cell, **params):
      val = cell.get_value()
      return f"{val:,.0f}"
      
    columns = [
      {
        'title': 'Description',
        'field': 'description',
        'width': 200,
      },
      {
        'title': 'Vendor',
        'field': 'vendor_name',
        'width': 200,
      },
      {
        'title': 'Total',
        'field': 'total',
        'width': 100,
        'formatter': total_formatter
        
      },
    ]

    total = sum( x['total'] for x in self.item['import_data'])
    num_lines = len(self.item['import_data'])

    self.import_table.columns = columns
    
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
    self.import_table.data = self.item['final_import_data']
    
    return total, num_lines


  
  def create_brand(self):
    validation = True
    validation = validation and self.item.get('code', None)
    validation = validation and self.item.get('name', None)
    validation = validation and self.item.get('import_data', None)

    if not validation:
      alert("Cannot create Brand - missing valid code, name or import data!")
      return False
      
    next_step = False
    try:
      result = Data.create_brand(code=self.item['code'], name=self.item['name'])
      #result = True
      next_step = result
    except Exception as e:
      alert(f"Failed to create Brand with code {self.item['code']}: {e}")
      print(e)

    if not next_step:
      alert(f"Failed to create Brand with code {self.item['code']}")
      return False

    next_step = False
    
    if self.item.get('icon_file', None) is not None:
      try:
        result = Data.add_brand_icon(code=self.item['code'], content=self.item['icon_file'])
        #result = True
        next_step = result
        if not result:
          alert(f"Failed to upload icon to Brand: {self.item['code']}")          
      except Exception as e:
        print(e)
        alert(f"Failed to upload icon to Brand: {self.item['code']}")          
    else:
      next_step = True
      
    if not next_step:
      return False

    next_step = False
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
                                               fin_year=self.import_year,
                                               new_vendor_names=new_vendor_names, 
                                               vendor_aliases=vendor_aliases, 
                                               transactions_with_entries=transactions_with_entries,
                                               defaults = {}
                                              )
    if not result:
        alert(f"Failed to create first Budget for Brand: {self.item['code']}")          
        return False
    else:
      print(f"{result} entries created")

    return self.item['code']

  def year_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.import_loader.enabled = True


  

  
  def goto_import_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    ret, new_vendor_names, reverse_map, vendor_aliases = self.vendor_table.check_vendor_table()
    
    # These objects are ready to submit to the final import
    self.new_vendor_names = new_vendor_names
    self.vendor_aliases = vendor_aliases
    
    if ret:
      self.import_total, self.import_lines = self.build_import_table(reverse_map)
      self.import_panel.visible = True
      self.vendor_panel.visible = False
      self.refresh_data_bindings()
    else:
      alert("Every Vendor needs to be mapped or selected to create!")

  