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

    self.colors = {
      'Actual': {'backgroundColor': '#ffffcc', 'color': 'black' },
      'Forecast': {'backgroundColor': '#ccffcc', 'color': 'black' },
    }
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def load_data(self):
    self.year_months = ['202307', '202308']
    self.transaction_types = {
      '202307': 'Actual',
      '202308': 'Forecast'
    }
    self.data = [
      {
        'vendor_name': 'Miro', 'vendor': None, '202307': 100, '202308': 90
      }
    ]
    self.ly_data = {
        'vendor_name': 'Miro', 'vendor': None, '202307': 80, '202308': 70      
    }
    self.b_data = {
        'vendor_name': 'Miro', 'vendor': None, '202307': 110, '202308': 100      
    }

    pass
    
  def tracking_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""

    # Vendor Formatter
    def vendor_formatter(cell, **params):
      vendor = cell.getData()['vendor']

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

    # Entry formatter
    def format_entry(cell, **params):
      val = cell.getValue()
      if params.get('backgroundColor', None):
        cell.getElement().style.backgroundColor = params['backgroundColor']
      if params.get('color', None):
        cell.getElement().style.color = params['color']
      try:
        val = "{:,.0f}".format(val)
      except Exception:
        pass
      return val

    # Total formatter
    def format_total(cell, **params):
      val = cell.get_value()
      cell.getElement().style.backgroundColor = '#424140'
      cell.getElement().style.color = 'white'
      try:
        val = "{:,.0f}".format(val)
      except Exception:
        val = 'NA'
      return val

    # Change formatter
    def format_percent(cell, **params):
      val = cell.get_value()
      
      cell.getElement().style.backgroundColor = '#0d6e12' if val > 0 else '#6e0d15'
      cell.getElement().style.color = 'white'
      
      try:
        val = "{:,.0f}%".format(val)
      except Exception:
        val = 'NA'
      return val

    
    columns = [{
        "title": "Vendor",
        "field": "vendor_name",
        'width': 200,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        'formatter': vendor_formatter      
    }]

    for c in self.year_months:
      transaction_type = self.transaction_types[c]
      columns.append({
        "title": c, 
        "field": c, 
        "formatter": format_entry, 
        "hozAlign": "right",
        "formatterParams": { 'backgroundColor': self.colors[transaction_type]['backgroundColor'], 'color': self.params[transaction_type]['color']},
        "width": 130,
        "headerFilter": "number",
        'editor': self.params[self.mode]['editor']
      })

    columns.append({
        "title": "Total", 
        "field": 'total', 
        "formatter": format_total, 
        "width": 130,
        "headerFilter": "number",
        "hozAlign": 'right',
        'editor': None   
    })

    change_col = {
          "title": "Change", 
          "field": 'change', 
          "formatter": format_percent, 
          "width": 130,
          "hozAlign": 'right',
          'editor': None         
    }

    if self.mode == "last_year":
      columns.append(change_col)
      compare = self.yes_compare
      c_data = self.ly_data
    elif self.mode == 'budget':      
      columns.append(change_col)
      compare = self.b_compare
      c_data = self.b_data
    else:
      compare = self.no_compare
      c_data = None
      
    self.tracking_table.columns = columns
    self.tracking_table.data = compare(c_data)

def yes_compare(self, c_data):
  new_data = []
  for i, row in enumerate(self.data):
    new_row = { 'vendor_name': row['vendor_name'], 'vendor': row['vendor'] }
    new_row['total'] = row['total'] - c_data[i]['total']
    try:
      new_row['change'] = int(row['total'] / c_data[i]['total']*100)
    except Exception as e:
      new_row['change'] = 0
      
    for year_month in self.year_months:
      new_row[year_month] = row[year_month] - c_data[i][year_month]
    new_data.append(new_row)
    

def no_compare(self):
  return self.data

def b_compare(self):
  pass
