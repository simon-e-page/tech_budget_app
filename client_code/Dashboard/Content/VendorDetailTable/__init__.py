from ._anvil_designer import VendorDetailTableTemplate
from anvil import *
import anvil.server
import anvil.users

import datetime as dt

from .... import Data
from ....Data import VendorsModel, TransactionsModel, FinancialNumber, CURRENT_YEAR
from ....Vendors.Vendors.Vendor import Vendor


class VendorDetailTable(VendorDetailTableTemplate):
  def __init__(self, mode='Actual', **properties):
    # Set Form properties and Data Bindings.
    self.vendors = VendorsModel.VENDORS
    self.vendor = properties['vendor']
    self.year = properties.get('year', CURRENT_YEAR)
    
    if mode == 'Actual':
      mode_str = ' Actual and Forecast lines for '
    else:
      mode_str = ' Forecast and Budget lines for '
    self.mode = mode
    self.title = f"FY{self.year} {mode_str} {self.vendor.get('vendor_name')}"
    
    options = {
      "index": "transaction_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      "pagination": False,
      #"paginationSize": 250,
      #"frozenRows": 0,
      "height": "30vh",
      #'autoResize': False,
      # "pagination_size": 10,
    }

    self.forecast_details_table.options = options
    self.actual_details_table.options = options
    self.budget_details_table.options = options
    
    #TODO: alter Actual colors in Forecast months.. (grey out)
    self.colors = {
      "Actual": {"backgroundColor": "#ffffcc", "color": "black"},
      "Forecast": {"backgroundColor": "#ccffcc", "color": "black"},
      'Budget': {"backgroundColor": "#ccffff", "color": "black"},
      'Total': {"backgroundColor": '#424140', "color": "white"},
      'Editable': {"backgroundColor": "#f5e3bf", "color": "black"}
    }

    self.editors = {
      'Actual': None,
      'Forecast': 'number',
      'Budget': 'number'
    }
    
    self.loaded = False
    self.prepared = False
    self.actual_data = {}
    self.forecast_data = {}
    self.budget_data = {}
    self.init_components(**properties)

    self.actual_panel.visible = (mode == 'Actual')
    self.budget_panel.visible = (mode == 'Budget')
    # Any code you write here will run before the form opens.

  def load_data(self):
    d = Data.get_vendor_detail(year = self.year, vendor_id=self.vendor.vendor_id, mode='Actual')
    self.year_months = d["year_months"]
    self.transaction_types = d["transaction_types"]
    self.data = d["data"]
    #print(self.data)
    # self.ly_data = d['ly_data']
    # self.b_data =  d['b_data']
    self.loaded = True
    #self.details_table_table_built()

  
  def actual_details_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    if self.mode != 'Actual':
      return
      
    if not self.loaded:
      self.load_data()
    if not self.prepared:
      self.prepare_data()
    self.prepare_columns(self.actual_details_table)
    self.actual_details_table.data = self.actual_data

  def forecast_details_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    if not self.loaded:
      self.load_data()
    if not self.prepared:
      self.prepare_data()
    self.prepare_columns(self.forecast_details_table)
    self.forecast_details_table.data = self.forecast_data
  
  def budget_details_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    if self.mode != 'Budget':
      return
      
    if not self.loaded:
      self.load_data()
    if not self.prepared:
      self.prepare_data()
    self.prepare_columns(self.budget_details_table)
    self.budget_details_table.data = self.budget_data

  
  def prepare_columns(self, table):
    # Vendor Formatter
    def transaction_formatter(cell, **params):
      transaction_id = cell.getData()["transaction_id"]
      transaction = self.vendors.get(transaction_id)

      def open_transaction(sender, **event_args):
        print("Opening tranaction: {0}".format(sender.tag.description))
        ret = alert(
          Transaction(item=sender.tag, show_save=False),
          large=True,
          title="Transaction Details",
          buttons=[("Save Changes", True), ("Cancel", False)],
        )
        if ret:
          try:
            transaction.update()
          except Exception as e:
            print("Failed to update Transaction!")
        return

      link = Link(text=cell.get_value(), tag=transaction)
      link.set_event_handler("click", open_transaction)
      return link

    # Entry formatter
    def format_entry(cell, **params):
      val = cell.getValue()
      data = cell.get_data()
      trans_type = data['transaction_type']
      ym = params.get("year_month")
      column_type = self.transaction_types[ym]
      b_ym = f"{ym}B"
      ly_ym = f"{ym}LY"

      if trans_type == 'Actual':
        if params.get("backgroundColor", None):
          backgroundColor = params["backgroundColor"]
        if params.get("color", None):
          color = params["color"]
        compare = data[ly_ym]
        tooltip_prefix = "LY"
        bold = False
      elif trans_type == 'Total':
        backgroundColor = self.colors['Total']['backgroundColor']
        color = self.colors['Total']['color']
        compare = val
        tooltip_prefix = None
        bold = True
      elif column_type == 'Forecast':
        backgroundColor = self.colors['Editable']['backgroundColor']
        color = self.colors['Editable']['color']
        compare = data[b_ym]          
        tooltip_prefix = "Budget"
        bold = False        
      else:
        backgroundColor = self.colors['Forecast']['backgroundColor']
        color = self.colors['Forecast']['color']
        compare = data[b_ym]          
        tooltip_prefix = "Budget"
        bold = False
        
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
          bold=bold
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
        val = f"<b>{val}</b>"
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
          'headerSort': False,
          #'editor': self.editors[transaction_type]
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

    table.columns = columns

  
  def prepare_data(self):

    def zero_filter(data, **params):
      non_zero = [int(int(x)!=0) for i,x in dict(data).items() if i in self.year_months]
      #print(f"{data['vendor_name']}: {non_zero}")
      non_zero = sum(non_zero)
      return non_zero != 0
    

    # Insert subtotal rows
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
    b_total_row = a_total_row.copy()
    b_total_row.update({ 'description': "Total for Budgets" })
    
    actual_rows = []
    forecast_rows = []
    budget_rows = []
    
    for row in self.data:
      #print(row)
      if row['transaction_type']=='Budget':
        f_row = row.copy()
        b_row = row.copy()
        for ym in self.year_months:
          f_row[ym] = row[f"{ym}F"]
          b_row[ym] = row[f"{ym}B"]
          f_total_row[ym] += f_row[ym]
          f_total_row[f"{ym}B"] += row[f"{ym}B"]
          b_total_row[ym] += b_row[ym] 
        f_row['total'] = row['totalF']
        b_row['total'] = row['totalB']
        f_total_row['total'] += f_row['total']
        f_total_row['totalB'] += row['totalB']
        b_total_row['total'] += b_row['total']
        forecast_rows.append(f_row)
        budget_rows.append(b_row)
      else:
        for ym in self.year_months:
          a_total_row[ym] += row[ym]
          a_total_row[f"{ym}LY"] += row[f"{ym}LY"]
        a_total_row['total'] += row['total']
        a_total_row['totalLY'] += row['totalLY']
        actual_rows.append(row)

    self.actual_data = actual_rows + [a_total_row]
    self.forecast_data = forecast_rows + [f_total_row]
    self.budget_data = budget_rows + [b_total_row]
    self.actual_details_table.set_filter(zero_filter)
    self.forecast_details_table.set_filter(zero_filter)
    self.budget_details_table.set_filter(zero_filter)
    self.prepared = True


  def forecast_details_table_cell_click(self, cell, **event_args):
    """This method is called when a cell is clicked"""
    data = cell.get_data()
    val = cell.get_value()
    ym = cell.getField()
    desc = data['description']
    if data['transaction_type'] in ['Total', 'Actual']:
      pass
      #print("Clicked on an Actual or a Total - ignore!")
      #print(event_args)
    elif self.transaction_types[ym] != 'Forecast':
      pass
      #print("Clicked on a prior month - ignore!")
      #print(event_args)      
    else:
      if self.mode == "Budget":
        tt = "budget"
        suf = "B"
      else:
        tt = "forecast"
        suf = "F"
      
      textbox = TextBox(text=val, type='number')
      ret = alert(textbox, title=f"Enter new {tt} value for {desc} in {ym}", buttons=[ ('OK', True), ('Cancel', False) ])
      if ret:
        cell.set_value(textbox.text)
        for row in self.data:
          if row['transaction_type']=='Budget' and row['transaction_id'] == data['transaction_id']:
            row[f"{ym}{B}"] = float(textbox.text)
            row['edited'] = True
            break
        self.prepare_data()
        self.forecast_details_table.data = self.forecast_data
        
  def get_forecast_entries(self, entry_type='Forecast'):
    """ Returns all forecast entries for updating """
    entries = {}
    if entry_type == 'Forecast':
      forecast_months = [ x for x, t in self.transaction_types.items() if t=='Forecast' ]
      suf = 'F'
    else:
      forecast_months = [ x for x in self.year_months ]
      suf = 'B'
      
    for row in self.data:
      transaction_id = row['transaction_id']
      if row['transaction_type']=='Budget':
        for ym in forecast_months:
          month = int(ym[4:])
          year = int(ym[0:4])
          fin_year = year + int(month>6)
          trans_entries = entries.get(transaction_id, [])
          trans_entries.append({ 
                    'transaction_id': transaction_id,
                    'transaction_type': entry_type,
                    'year_month': int(ym),
                    'timestamp': dt.date(year, month, 1),
                    'fin_year': fin_year,
                    'amount': float(row[f"{ym}{suf}"])
                  })
          entries[transaction_id] = trans_entries
    return entries

          