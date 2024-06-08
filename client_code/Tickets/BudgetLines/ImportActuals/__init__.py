from ._anvil_designer import ImportActualsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import Data
from ....Data import CURRENT_YEAR, ImporterModel, VendorsModel


class ImportActuals(ImportActualsTemplate):
  def __init__(self, **properties):
    self.next_month = Data.get_actuals_updated(CURRENT_YEAR)
    self.importer = ImporterModel.IMPORTER
    self.vendors = VendorsModel.VENDORS
    self.new_entries = None
    self.new_year_month = None
    self.month_total = None
    self.cost_centres = None
    
    if self.next_month is None or self.next_month == 0:
      self.next_month = (CURRENT_YEAR - 1) * 100 + 7
      
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
  
  def get_new_entries(self):
    return self.new_entries

  def file_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    if self.importer.check_brand(file.name):
      new_data = self.importer.parse(file)
      self.new_entries = new_data['entries']
      self.cost_centres = new_data['cost_centres']
      self.new_year_month = new_data['year_month']
      self.month_total = new_data['month_total']
      
      self.render_table()

  def render_table(self):

    def vendor_formatter(cell, **params):
      data = cell.get_data()
      vendor_id = data['vendor_id']
      vendor_name = cell.get_value()
      if vendor_id is None:
        vendor_name = f"<b>*{vendor_name}*</b>"
      return vendor_name
    
    columns = [
      { 
        'title': 'Vendor',
        'field': 'vendor_name',
        'formatter': vendor_formatter,
        'headerFilter': 'input',
        "headerFilterFunc": "starts"        
      },
      { 
        'title': 'New',
        'field': 'new_vendor',
        'formatter': 'tickCross',
        'headerFilter': 'tickCross',
        'width': 100
      },
      
    ]

    columns += [
      {
        'title': x,
        'field': x,
      } for x in self.cost_centres
    ]

    columns += [
      {
        'title': 'Total',
        'field': 'total'
      }
    ]

    self.imported_table.options.update(
      selectable="highlight",
      pagination=False,
      pagination_size=15,
      css_class=["table-striped", "table-bordered", "table-condensed"]
    )
    
    self.imported_table.columns = columns
    self.imported_table.data = self.new_entries
    self.label_panel.visible = True
    self.imported_table.visible = True
    self.refresh_data_bindings()
    
  
