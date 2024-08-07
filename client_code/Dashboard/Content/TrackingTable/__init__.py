from ._anvil_designer import TrackingTableTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import Data
from ....Data import VendorsModel, TransactionsModel, CURRENT_YEAR, FinancialNumber
#from ....Vendors.Vendors.Vendor import Vendor
from ..VendorDetailTable import VendorDetailTable

COL_WIDTH = 90

class TrackingTable(TrackingTableTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.vendors = VendorsModel.VENDORS
    self.transactions = TransactionsModel.get_transactions()
    self.year = properties.get('year', CURRENT_YEAR)
    self.task = None
    
    self.tracking_table.options = {
      "index": "vendor",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': True,
      'paginationSize': 250,
      'frozenRows': 0,
      'height': '50vh',
      #'autoResize': False,
      #"pagination_size": 10,
    }

    self.summary_table.options = {
      "index": "id",  # or set the index property here
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': False,
      'frozenRows': 8,
      'height': '40vh',
      
      #'autoResize': False,
      #"pagination_size": 10,
    }
    
    self.colors = {
      'Actual': {'backgroundColor': '#ffffcc', 'color': 'black' },
      'Forecast': {'backgroundColor': '#ccffcc', 'color': 'black' },
    }
    self.mode = 'absolute'
    self.data = None
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  
  def set_plot_layout(self):
    actuals = [ self.actuals_summary[x] for x in self.year_months if self.transaction_types[x]=='Actual' ]
    forecasts = [ self.actuals_summary[x] for x in self.year_months if self.transaction_types[x]!='Actual' ]
    budgets = [ self.budget_summary[x] for x in self.year_months ]
    actual_months = [ f"{x[0:4]}-{x[4:]}" for x in self.year_months if self.transaction_types[x]=='Actual']
    forecast_months = [ f"{x[0:4]}-{x[4:]}" for x in self.year_months if self.transaction_types[x]!='Actual']
    x_values = [ f"{x[0:4]}-{x[4:]}" for x in self.year_months]

    # Create the traces
    trace_actuals = go.Bar(
        x=actual_months,
        y=actuals,
        name='Actuals',
        #marker=dict(color='blue')
        marker=dict(color=self.colors['Actual']['backgroundColor'])
    )
    
    trace_forecast = go.Bar(
        x=forecast_months,
        y=forecasts,
        name='Forecast',
        marker=dict(color=self.colors['Forecast']['backgroundColor'])
    )
    
    trace_budget = go.Scatter(
        x=x_values,
        y=budgets,
        name='Budget',
        mode='lines+markers',
        line=dict(color='red')
    )
    
    # Create the layout
    layout = go.Layout(
        title='Actuals vs Forecast and Budget',
        xaxis=dict(title='Month'),
        yaxis=dict(title='$'),
        barmode='group'
    )

    self.tracking_plot.layout = layout
    self.tracking_plot.data = [trace_actuals, trace_forecast, trace_budget]

  
  def prepare_data(self, d):
    self.year_months = d['year_months']
    self.transaction_types = d['transaction_types']
    self.data = d['data']
    #self.loaded = True
    summary = self.summary_table_table_built()
    self.tracking_table_table_built()
    self.set_plot_layout()
    self.raise_event('x-data-loaded', actuals=summary['actuals'], forecasts=summary['forecasts'])


  def update_entries(self, vendor, entries):
    self.transactions.load(vendor_name=vendor.vendor_name)
    for transaction_id, trans_entries in entries.items():
      transaction = self.transactions.get(transaction_id)
      if transaction is None:
        print(f"Can't find transaction {transaction_id} associated with Vendor {vendor.name}")
      else:
        transaction.add_entries(trans_entries, overwrite=True)
      #alert(f"Error updating Entries for tranaction {transaction_id}!")
      
      
  def summary_table_table_built(self, **event_args):
    if self.data is None:
      return

    columns = [
      { 
        'title': 'Summary',
        'field': 'id',
        "hozAlign": "left",
        "width": 250,
        'headerSort': False
      },
    ]
    
    for c in self.year_months:
      transaction_type = self.transaction_types[c]
      columns.append({
        "title": c, 
        "field": c, 
        "formatter": self.format_summary, 
        "hozAlign": "right",
        "formatterParams": { 'year_month': c, 'backgroundColor': self.colors[transaction_type]['backgroundColor'], 'color': self.colors[transaction_type]['color']},
        "width": COL_WIDTH,
        'headerSort': False
      })

    columns.append({
        "title": "Total", 
        "field": 'total', 
        "formatter": self.format_summary, 
        "formatterParams": { 'year_month': 'total', 'backgroundColor': '#424140', 'color': 'white'},
        "width": 100,
        "hozAlign": 'right',
        'headerSort': False
      })

    self.summary_table.columns = columns
    a_data = { 'id': 'CY Actuals / Forecast', 'total': 0.0 } | { x: 0.0 for x in self.year_months }    
    b_data = { 'id': 'Budgets', 'total': 0.0 } | { x: 0.0 for x in self.year_months }
    ly_data = { 'id': 'LY Actuals', 'total': 0.0 } | { x: 0.0 for x in self.year_months }
    d_data = { 'id': 'Difference', 'total': 0.0 } | { x: 0.0 for x in self.year_months }
    p_data = { 'id': 'Percentage', 'total': 0.0 } | { x: 0.0 for x in self.year_months }
    ac_data = { 'id': 'CY Cumulative', 'total': 0.0 } | { x: 0.0 for x in self.year_months }
    lc_data = { 'id': 'LY Cumulative', 'total': 0.0 } | { x: 0.0 for x in self.year_months }
    dc_data = { 'id': 'Cumul Difference', 'total': 0.0 } | { x: 0.0 for x in self.year_months }
    pc_data = { 'id': 'Cumul Percentage', 'total': 0.0 } | { x: 0.0 for x in self.year_months }

    # Not used for table - just for headline cards
    f_data = { 'id': 'CY Forecast', 'total': 0.0 } | { x: 0.0 for x in self.year_months }    
    lf_data = { 'id': 'LY Forecast', 'total': 0.0 } | { x: 0.0 for x in self.year_months }    
    
    for row in self.data:
      for year_month in self.year_months:
        a_data[year_month] += row[year_month]
        ly_data[year_month] += row[f"{year_month}LY"]
        b_data[year_month] += row[f"{year_month}B"]
        f_data[year_month] += row[f"{year_month}F"]
        lf_data[year_month] += row[f"{year_month}LF"]
        
      a_data['total'] += row['total']
      ly_data['total'] += row['totalLY']
      b_data['total'] += row['totalB']
      f_data['total'] += row['totalF']
      lf_data['total'] += row['totalLF']


    for i, year_month in enumerate(self.year_months):
      d_data[year_month] += a_data[year_month] - ly_data[year_month]
      ac_data[year_month] = a_data[year_month] + ac_data[self.year_months[i-1]] if i>0 else a_data[year_month]
      lc_data[year_month] = ly_data[year_month] + lc_data[self.year_months[i-1]] if i>0 else ly_data[year_month]
      dc_data[year_month] = ac_data[year_month] - lc_data[year_month]

      try:
        p_data[year_month] = int(d_data[year_month] / ly_data[year_month] * 100)
        pc_data[year_month] = int(dc_data[year_month] / lc_data[year_month] * 100)
      except Exception:
        p_data[year_month] = 0
        pc_data[year_month] = 0

    d_data['total'] = a_data['total'] - ly_data['total']
    ac_data['total'] = a_data['total']
    lc_data['total'] = ly_data['total']
    dc_data['total'] = ac_data['total'] - lc_data['total']

    try:
      p_data['total'] = int(d_data['total'] / ly_data['total'] * 100)
      fp_total = int((f_data['total'] - lf_data['total']) / lf_data['total'] * 100)
    except Exception:
      p_data[year_month] = 0
      fp_total = 0
      
    pc_data['total'] = p_data['total']

    self.actuals_summary = a_data
    self.budget_summary = b_data
    self.ly_summary = ly_data
  
    self.summary_table.data = [ a_data, ly_data, d_data, p_data, ac_data, lc_data, dc_data, pc_data ]
    return { 
              'actuals':   { 'total': a_data['total'], 'delta': p_data['total'] }, 
              'forecasts': { 'total': f_data['total'], 'delta': fp_total }
           }    
  
  # Vendor Formatter
  def vendor_formatter(self, cell, **params):
    vendor_id = cell.getData()['vendor_id']
    vendor = self.vendors.get(vendor_id)

    def open_vendor(sender, **event_args):
      print("Opening vendor: {0}".format(sender.tag.vendor_name))
      vendor_form = VendorDetailTable(vendor=sender.tag, year=self.year)
      ret = alert(vendor_form, large=True, title="Vendor Details", buttons=[ ('Save Changes', True), ('Cancel', False) ])
      if ret:
        #try:
        entries = vendor_form.get_forecast_entries()
        self.update_entries(sender.tag, entries)
        #except Exception as e:
        #  print("Failed to update Vendor!")
      return

    link = Link(text=cell.get_value(), tag=vendor)
    link.set_event_handler("click", open_vendor)
    return link

  # Summary formatter
  def format_summary(self, cell, **params):
    val = cell.getValue()
    data = cell.get_data()
    col = params.get('year_month', 'total')
    
    if params.get('backgroundColor', None):
      cell.getElement().style.backgroundColor = params['backgroundColor']
    if params.get('color', None):
      cell.getElement().style.color = params['color']

    if "Cumul" in data['id'] and col=='total':
      lbl = Label(text='',
                  align='right',
                  bold=False,
                  foreground=params['color'], 
                  background=params['backgroundColor']
                 )
    elif "Percentage" in data['id']:
      if val > 0:
        text = "+{:,.0f}%".format(val)
      elif val < 0:
        text = "{:,.0f}%".format(val)
      else:
        text = '-'
      lbl = Label(text = text,
                  align='right',
                  bold=False,
                  foreground=params['color'], 
                  background=params['backgroundColor']
                  )
    else:
      icon = None
      if 'Difference' in data['id']:
        if val > 0:
          icon='fa:arrow-up'
        elif val < 0:
          icon='fa:arrow-down'
      lbl = Label(text = "{:,.0f}".format(FinancialNumber(val)),
                  icon=icon,
                  icon_align="left", 
                  align='right',
                  bold=False,
                  foreground=params['color'], 
                  background=params['backgroundColor']
                  )
    return lbl
  
  # Entry formatter
  def format_entry(self, cell, **params):
    val = cell.getValue()
    data = cell.get_data()
    ym = params.get('year_month')
    #b_ym = f"{ym}B"
    ly_ym = f"{ym}LY"
    
    if params.get('backgroundColor', None):
      cell.getElement().style.backgroundColor = params['backgroundColor']
    if params.get('color', None):
      cell.getElement().style.color = params['color']

    try:
      ly_delta = (int(val) - int(data[ly_ym]))/int(data[ly_ym])
      ly_delta = int(ly_delta * 100)
    except Exception:
      ly_delta = "INF"
      
    tooltip = f"LY: {FinancialNumber(data[ly_ym]):,.0f}"

    if int(val) < int(data[ly_ym]):
      icon = "fa:arrow-down"
      tooltip += f"\n{ly_delta}%"
    elif int(val) > int(data[ly_ym]):
      icon = "fa:arrow-up"
      tooltip += f"\n+{ly_delta}%"
    else:
      icon = None
      tooltip = None
      
    try:
      val = Label(text = "{:,.0f}".format(FinancialNumber(val)),
                  icon=icon, 
                  tooltip=tooltip, 
                  align='right',
                  icon_align="left", 
                  bold=False,
                  foreground=params['color'], 
                  background=params['backgroundColor']
                  )
      #val = "{:,.0f}".format(val)
    except Exception:
      print("Entry Exception!")
      pass
    return val
  
  
  # Total formatter
  def format_total(self, cell, **params):
    val = cell.get_value()
    ly_total = cell.get_data()['totalLY']

    try:
      ly_delta = (int(val) - int(ly_total))/int(ly_total)
      ly_delta = int(ly_delta * 100)
    except Exception:
      ly_delta = 'INF'
    
    cell.getElement().style.color = 'white'
    tooltip = f"LY: {FinancialNumber(ly_total):,.0f}"
    
    if int(val) < int(ly_total):
      background_color = '#043d1b'
      tooltip += f"\n{ly_delta}%"
    elif int(val) > int(ly_total):                  
      background_color = '#4d0404'
      tooltip += f"\n+{ly_delta}%"
    else:
      background_color = '#424140'

    cell.getElement().style.backgroundColor = background_color

    try:
      val = Label(text = "{:,.0f}".format(FinancialNumber(val)),
                  bold = True,
                  align='right',
                  icon_align="left", 
                  foreground='white', 
                  tooltip=tooltip,
                  background=background_color
                  )
      #val = "{:,.0f}".format(val)
    except Exception:
      print("Total Exception!")
      val = 'NA'
    return val

  # Change formatter
  def format_percent(self, cell, **params):
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
      print("Percent Exception!")
      val = 'NA'
    return val
  
  
  def tracking_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    if self.data is None:
      return
          
    columns = [{
        "title": "Vendor",
        "field": "vendor_name",
        'width': 250,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        'formatter': self.vendor_formatter      
    }]

    for c in self.year_months:
      transaction_type = self.transaction_types[c]
      columns.append({
        "title": c, 
        "field": c, 
        "formatter": self.format_entry, 
        "hozAlign": "right",
        "formatterParams": { 'year_month': c, 'backgroundColor': self.colors[transaction_type]['backgroundColor'], 'color': self.colors[transaction_type]['color']},
        "width": COL_WIDTH,
        "headerFilter": "number",
      })

    columns.append({
        "title": "Total", 
        "field": 'total', 
        "formatter": self.format_total, 
        "width": 100,
        "headerFilter": "number",
        "hozAlign": 'right',
    })

    change_col = {
          "title": "Change", 
          "field": 'change', 
          "formatter": self.format_percent, 
          "width": COL_WIDTH,
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
    #print(new_data)
    return new_data
  
  def no_compare(self, c_data):
    def zero_filter(data, **params):
      non_zero = [int(int(x)!=0) for i,x in dict(data).items() if i in self.year_months]
      #print(f"{data['vendor_name']}: {non_zero}")
      non_zero = sum(non_zero)
      return non_zero != 0
      
    self.tracking_table.set_filter(zero_filter)
    #print(self.data)
    return self.data
  
