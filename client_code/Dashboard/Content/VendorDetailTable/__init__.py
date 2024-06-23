from ._anvil_designer import VendorDetailTableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import Data
from ....Data import VendorsModel, TransactionsModel, FinancialNumber, CURRENT_YEAR
from ....Vendors.Vendors.Vendor import Vendor


class VendorDetailTable(VendorDetailTableTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.vendors = VendorsModel.VENDORS
    self.vendor = properties['vendor']
    self.year = properties.get('year', CURRENT_YEAR)

    self.details_table.options = {
      "index": "transaction_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      "pagination": False,
      #"paginationSize": 250,
      #"frozenRows": 0,
      "height": "50vh",
      #'autoResize': False,
      # "pagination_size": 10,
    }

    self.colors = {
      "Actual": {"backgroundColor": "#ffffcc", "color": "black"},
      "Forecast": {"backgroundColor": "#ccffcc", "color": "black"},
      'Budget': {"backgroundColor": "#ccffff", "color": "black"},
      'Total': {"backgroundColor": "#ccffff", "color": "white"},
    }
    self.loaded = False
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def load_data(self):
    d = Data.get_vendor_detail(year = self.year, vendor_id=self.vendor.vendor_id)
    self.year_months = d["year_months"]
    self.transaction_types = d["transaction_types"]
    self.data = d["data"]
    #print(self.data)
    # self.ly_data = d['ly_data']
    # self.b_data =  d['b_data']
    self.loaded = True
    #self.details_table_table_built()

  def details_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    if not self.loaded:
      self.load_data()

    # Vendor Formatter
    def vendor_formatter(cell, **params):
      vendor_id = cell.getData()["vendor_id"]
      vendor = self.vendors.get(vendor_id)

      def open_vendor(sender, **event_args):
        print("Opening vendor: {0}".format(sender.tag.vendor_name))
        ret = alert(
          Vendor(item=sender.tag, show_save=False),
          large=True,
          title="Vendor Details",
          buttons=[("Save Changes", True), ("Cancel", False)],
        )
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
      data = cell.get_data()
      trans_type = data['transaction_type']
      ym = params.get("year_month")
      b_ym = f"{ym}B"
      f_ym = f"{ym}F"
      ly_ym = f"{ym}LY"

      if trans_type == 'Actual':
        if params.get("backgroundColor", None):
          backgroundColor = params["backgroundColor"]
        if params.get("color", None):
          color = params["color"]
        compare = data[ly_ym]
        tooltip_prefix = "LY"
      elif trans_type == 'Total':
        backgroundColor = self.colors['Total']['backgroundColor']
        color = self.colors['Total']['color']
        compare = val
        tooltip_prefix = None
      else:
        backgroundColor = self.colors['Forecast']['backgroundColor']
        color = self.colors['Forecast']['color']
        compare = data[b_ym]          
        tooltip_prefix = "Budget"
        
      cell.getElement().style.backgroundColor = backgroundColor
      cell.getElement().style.color = color

      try:
        delta = (int(val) - int(compare)) / int(compare)
        delta = int(delta * 100)
      except Exception:
        delta = "INF"

      tooltip = f"{tooltip_prefix}: {FinancialNumber(compare):,.0f}" if tooltip_prefix is not None else None

      if int(val) > int(compare):
        tooltip += f"\n+{delta}%"
        icon = 'fa:arrow-up'
      elif int(val) < int(compare):              
        tooltip += f"\n{delta}%"
        icon = 'fa:arrow-down'
      else:
        icon = None
      
      try:
        val = Label(
          text="{:,.0f}".format(FinancialNumber(val)),
          align="right",
          icon_align="left",
          tooltip = tooltip,
          icon=icon,
          foreground=color,
          background=backgroundColor,
        )
        # val = "{:,.0f}".format(val)
      except Exception:
        print("Entry Exception!")
        pass
      return val

    # Text formatter
    def format_text(cell, **parans):
      val = cell.get_value()
      data = cell.get_data()
      color = self.colors['Total']['color']
      background_color = self.colors['Total']['backgroundColor']
      if data['transaction_type']=='Total':
        cell.getElement().style.backgroundColor = background_color
        cell.getElement().style.color = color
      return val        

    
    # Total formatter
    def format_total(cell, **params):
      val = cell.get_value()
      color = self.colors['Total']['color']
      background_color = self.colors['Total']['backgroundColor']

      cell.getElement().style.backgroundColor = background_color
      cell.getElement().style.color = color

      try:
        val = Label(
          text="{:,.0f}".format(FinancialNumber(val)),
          bold=True,
          align="right",
          icon_align="left",
          foreground=color,
          #tooltip=tooltip,
          background=background_color,
        )
        # val = "{:,.0f}".format(val)
      except Exception:
        print("Total Exception!")
        val = "NA"
      return val


    columns = [
      {
        "title": "Description",
        "field": "description",
        "width": 250,
        "headerSort": False,
        'formatter': format_text
      },
      {
        "title": "Owner",
        "field": "owner",
        "width": 100,
        "headerSort": False,        
        'formatter': format_text
      },
      {
        "title": "Cost centre",
        "field": "cost_centre",
        "width": 150,
        "formatter": format_text,     
        "headerSort": False
      }
      
    ]

    for c in self.year_months:
      transaction_type = self.transaction_types[c]
      columns.append(
        {
          "title": c,
          "field": c,
          "formatter": format_entry,
          "hozAlign": "right",
          "formatterParams": {
            "year_month": c,
            "backgroundColor": self.colors[transaction_type]["backgroundColor"],
            "color": self.colors[transaction_type]["color"],
          },
          "width": 85,
          #"headerFilter": "number",
          'headerSort': False
        }
      )

    columns.append(
      {
        "title": "Total",
        "field": "total",
        "formatter": format_total,
        "width": 100,
        #"headerFilter": "number",
        'headerSort': False,
        "hozAlign": "right",
      }
    )

    def zero_filter(data, **params):
      non_zero = [int(int(x)!=0) for i,x in dict(data).items() if i in self.year_months]
      #print(f"{data['vendor_name']}: {non_zero}")
      non_zero = sum(non_zero)
      return non_zero != 0
    
    self.details_table.columns = columns

    # Insert subtotal rows
    data = {}
    a_total_row = { 'transaction_type': 'Total', 
                    'owner': '', 
                    'description': "Total for Actuals", 
                    'cost_centre': '',  
                    'total': 0.0, 
                    'totalB': 0.0, 
                    'totalF': 0.0, 
                    'totalLY': 0.0 
                  }
    a_total_row.update({ x: 0.0 for x in self.year_months })
    a_total_row.update({ f"{x}B": 0.0 for x in self.year_months })
    a_total_row.update({ f"{x}F": 0.0 for x in self.year_months })
    a_total_row.update({ f"{x}LY": 0.0 for x in self.year_months })
    f_total_row = a_total_row.copy()
    f_total_row.update({ 'description': "Total for Forecasts" })

    actual_rows = []
    forecast_rows = []
    
    for row in self.data:
      print(row)
      if row['transaction_type']=='Budget':
        for ym in self.year_months:
          row[ym] = row[f"{ym}F"]
          f_total_row[ym] += row[ym]
          f_total_row[f"{ym}B"] += row[f"{ym}B"]
        row['total'] = row['totalF']
        f_total_row['total'] += row['total']
        f_total_row['totalB'] += row['totalB']
        forecast_rows.append(row)
      else:
        for ym in self.year_months:
          a_total_row[ym] += row[ym]
          a_total_row[f"{ym}LY"] += row[f"{ym}LY"]
        a_total_row['total'] += row['total']
        a_total_row['totalLY'] += row['totalLY']
        actual_rows.append(row)

    data = actual_rows + [a_total_row] + forecast_rows + [f_total_row]
    self.details_table.data = data
    self.details_table.set_filter(zero_filter)