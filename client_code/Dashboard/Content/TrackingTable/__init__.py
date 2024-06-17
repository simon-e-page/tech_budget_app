from ._anvil_designer import TrackingTableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import Data
from ....Data import VendorsModel, TransactionsModel
from ....Vendors.Vendors.Vendor import Vendor

class TrackingTable(TrackingTableTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.tracking_table.options = {
      "index": "transaction_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': True,
      'paginationSize': None,
      'frozenRows': 0,
      'height': '70vh',
      #'autoResize': False,
      #"pagination_size": 10,
    }
    
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def load_data(self):
    self.columns = [ 'vendor_name', '202307', '202308']
    self.actuals = {
      '202307': True,
      '202308': False
    }
    self.data = [
      {
        'vendor_name': 'Miro', 'vendor': None, '202307': 100, '202308': 90
      }
    ]
    self.last_year = {
        'vendor_name': 'Miro', '202307': 80, '202308': 70      
    }

    pass
    
  def tracking_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    def vendor_formatter(cell, **params):
      vendor = cell.getData()['vendor']

      # Vendor Formatter
      def open_vendor(sender, **event_args):
        print("Opening vendor: {0}".format(sender.tag.vendor_name))
        ret = alert(Vendor(item=sender.tag, show_save=False), large=True, title="Vendor Details", buttons=[ ('Save Changes', True), ('Cancel', False) ])
        if ret:
          try:
            vendor.update()
          except Exception as e:
            print("Failed to update Vendor!")
        return

      link = Link(text=cell.get_value(), tag=vendor)
      link.set_event_handler("click", open_vendor)
      return link

    
    
    columns = [{
        "title": "Vendor",
        "field": "vendor_name",
        'width': 200,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        'formatter': vendor_formatter      
    }]
    
    
