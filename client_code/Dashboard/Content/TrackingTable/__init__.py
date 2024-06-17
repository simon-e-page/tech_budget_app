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
    self.vendors = VendorsModel.VENDORS
    
    self.tracking_table.options = {
      "index": "vendor",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': True,
      'paginationSize': 5,
      'frozenRows': 0,
      'height': '50vh',
      #'autoResize': False,
      #"pagination_size": 10,
    }

    self.colors = {
      'Actual': {'backgroundColor': '#ffffcc', 'color': 'black' },
      'Forecast': {'backgroundColor': '#ccffcc', 'color': 'black' },
    }
    self.mode = 'absolute'
    self.loaded = False
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def load_data(self, year):
    
    self.year_months = ['202307', '202308']
    self.transaction_types = {
      '202307': 'Actual',
      '202308': 'Forecast'
    }
    self.data = [
      {
        'vendor_name': 'Miro', 'vendor_id': 1001, '202307': 100, '202308': 90, 'total': 190
      },
      {
        'vendor_name': 'M2', 'vendor_id': 1002, '202307': 100, '202308': 90, 'total': 190
      },
      
    ]
    self.ly_data = [
      {
        'vendor_name': 'Miro', 'vendor_id': 1001, '202307': 80, '202308': 70, 'total': 150      
      },
      {
        'vendor_name': 'M2', 'vendor_id': 1002, '202307': 100, '202308': 90, 'total': 190
      },
    ]
    self.b_data = [
      {
        'vendor_name': 'Miro', 'vendor_id': 1001, '202307': 110, '202308': 100, 'total': 210      
      },
      {
        'vendor_name': 'M2', 'vendor_id': 1002, '202307': 100, '202308': 90, 'total': 190
      },
    ]

    d = Data.get_tracking_table(year)
    self.year_months = d['year_months']
    self.transaction_types = d['transaction_types']
    self.data = d['data']
    self.ly_data = d['ly_data']
    self.b_data =  d['b_data']
    self.loaded = True
    self.tracking_table_table_built()
    
  def tracking_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    if not self.loaded:
      return
      
    # Vendor Formatter
    def vendor_formatter(cell, **params):
      vendor_id = cell.getData()['vendor_id']
      vendor = self.vendors.get(vendor_id)

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
        print("Exception!")
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
        print("Exception!")
        val = 'NA'
      return val

    # Change formatter
    def format_percent(cell, **params):
      val = cell.get_value()
      
      cell.getElement().style.backgroundColor = '#0d6e12' if val <= 0 else '#6e0d15'
      cell.getElement().style.color = 'white'
      
      try:
        if val > 0:
          val = "+{:,.0f}%".format(val)
        elif val < 0:
          val = "-{:,.0f}%".format(val)
        else:
          val = ''
      except Exception:
        print("Exception!")
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
        "formatterParams": { 'backgroundColor': self.colors[transaction_type]['backgroundColor'], 'color': self.colors[transaction_type]['color']},
        "width": 130,
        "headerFilter": "number",
      })

    columns.append({
        "title": "Total", 
        "field": 'total', 
        "formatter": format_total, 
        "width": 130,
        "headerFilter": "number",
        "hozAlign": 'right',
    })

    change_col = {
          "title": "Change", 
          "field": 'change', 
          "formatter": format_percent, 
          "width": 130,
          "hozAlign": 'right',
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
    #self.tracking_table.data = self.data
    self.tracking_table.data = compare(c_data)

  def yes_compare(self, c_data):
    new_data = []
    for i, row in enumerate(self.data):
      new_row = { 'vendor_name': row['vendor_name'], 'vendor': row['vendor'] }
      new_row['total'] = row['total'] - c_data[i]['total']
      try:
        new_row['change'] = int((row['total'] - c_data[i]['total']) / c_data[i]['total']*100)
      except Exception as e:
        new_row['change'] = 0
        
      for year_month in self.year_months:
        new_row[year_month] = row[year_month] - c_data[i][year_month]
      new_data.append(new_row)
    print(new_data)
    return new_data
  
  def no_compare(self, c_data):
    print(self.data)
    return self.data
  
