from ._anvil_designer import NewBrandTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...import Data
from ...Data.ImporterModel import IMPORTER

class NewBrand(NewBrandTemplate):
  def __init__(self, **properties):
    #self.item = properties['item']
    self.importer = IMPORTER
    self.import_loader.enabled = False
    self.import_year = None
    self.import_lines = 0
    self.import_total = 0.0
    self.import_years = [ str(x) for x in range(2023, 2030)]
    self.import_panel.visible = False
    # Set Form properties and Data Bindings.

    self.import_table.options = {
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
    self.item['import_data'] = self.importer.brand_import_data(year=self.import_year, excel_file=self.icon_loader.file)
    self.import_total, self.import_lines = self.build_import_table()
    self.import_panel.visible = True
    self.refresh_data_bindings()

  
  def build_import_table(self):

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
        'width': 100
      },
    ]

    total = sum( x['total'] for x in self.item['import_data'])
    num_lines = len(self.item['import_data'])

    self.import_table.columns = columns
    self.import_table.data = self.item['import_data']
    
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
      next_step = result
    except Exception as e:
      alert(f"Failed to create Brand with code {self.item['code']}")
      print(e)

    if not next_step:
      alert(f"Failed to create Brand with code {self.item['code']}")
      return False

    next_step = False
    
    if self.item.get('icon_file', None) is not None:
      try:
        result = Data.add_brand_icon(code=self.item['code'], content=self.item['icon_file'])
        next_step = result
        if not result:
          alert(f"Failed to upload icon to Brand: {self.item['code']}")          
      except Exception as e:
        print(e)
        alert(f"Failed to upload icon to Brand: {self.item['code']}")          

    if not next_step:
      return False

    next_step = False

    result = self.importer.load_first_budget(import_data=self.item['import_data'])
    if not result:
        alert(f"Failed to create first Budget for Brand: {self.item['code']}")          
        return False

    return self.item['code']

  def year_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.import_loader.enabled = True
