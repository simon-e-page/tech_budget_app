from ._anvil_designer import VendorDetailTableTemplate
from anvil import *
import anvil.server
import anvil.users

import datetime as dt

from .... import Data
from ....Data import VendorsModel, TransactionsModel, FinancialNumber
#from ....Vendors.Vendors.Vendor import Vendor
#from ....Tickets.Transaction import Transaction

class VendorDetailTable(VendorDetailTableTemplate):
  def __init__(self, mode='Actual', **properties):
    # Set Form properties and Data Bindings.
    self.vendors = VendorsModel.VENDORS
    self.transactions = TransactionsModel.get_transactions()
    self.vendor = properties['vendor']
    self.year = properties.get('year', Data.CURRENT_YEAR)
    self.fin_years = [ (str(x), x) for x in Data.get_fin_years() ]
    self.transaction_ids_to_show = properties.get('transaction_ids', [])
    self.updated_entries = {}

    # Prepare to remove this concept
    mode = "Actual"
    if mode == 'Actual':
      mode_str = ' Actual, Forecast and Budget lines for '
    else:
      mode_str = ' Forecast and Budget lines for '
    self.mode = mode
    #self.title = f"FY{self.year} {mode_str} {self.vendor.get('vendor_name')}"
    
    options = {
      "index": "transaction_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      "pagination": False,
      #"paginationSize": 250,
      #"frozenRows": 0,
      "height": "20vh",
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
    
    self.loaded = False
    self.prepared = False
    self.actual_data = {}
    self.forecast_data = {}
    self.budget_data = {}
    self.actual_transaction_id = None
    self.year_months = []
    
    self.init_components(**properties)
    
    self.load_data()
    self.prepare_data()



  
  def load_data(self):
    d = Data.get_vendor_detail(year = self.year, vendor_id=self.vendor.vendor_id, mode='Actual')
    self.year_months = d["year_months"]
    self.transaction_types = d["transaction_types"]
    if len(self.transaction_ids_to_show)>0:
      self.data = [ x for x in d['data'] if x['transaction_id'] in self.transaction_ids_to_show ]
    else:
      self.data = d['data']
    self.loaded = True
    if self.year == 2024:
      print(self.data)
      print(self.year_months)
      print(self.transaction_types)

  
  def actual_details_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""      
    #if not self.loaded:
    #  self.load_data()
    #if not self.prepared:
    #  self.prepare_data()
    while not self.prepared:
      pass
      
    if len(self.actual_data) > 1:
      #print(self.actual_data)
      self.prepare_columns(self.actual_details_table, table_type='Actual')
      self.actual_details_table.data = self.actual_data
      self.create_actual_button.visible = False
    else:
      self.actual_panel.visible = False
      self.create_actual_button.visible = True



  
  def forecast_details_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    #if not self.loaded:
    #  self.load_data()
    #if not self.prepared:
    #  self.prepare_data()
    while not self.prepared:
      pass
      
    if len(self.forecast_data)>1:
      self.prepare_columns(self.forecast_details_table, table_type='Forecast')
      self.forecast_details_table.data = self.forecast_data
      self.create_forecast_button.visible = False
    else:
      self.forecast_panel.visible = False
      self.create_forecast_button.visible = True
      actual_transaction_rows = [ x for x in self.data if x['transaction_type']=='Actual' ]
      if len(actual_transaction_rows)>0:
        self.actual_transaction_id = actual_transaction_rows[0]['transaction_id']


  
  def budget_details_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    #if not self.loaded:
    #  self.load_data()
    #if not self.prepared:
    #  self.prepare_data()
    while not self.prepared:
      pass

    if len(self.budget_data) > 1:
      locked = Data.is_locked(self.year)    
      self.prepare_columns(self.budget_details_table, table_type='Budget', locked=locked)
      self.budget_details_table.data = self.budget_data
    else:
      self.budget_panel.visible = False




  
  def prepare_columns(self, table, table_type='Actual', locked=False):
    print(f"Preparing {table_type}")
    
    # Transacion Formatter
    def transaction_formatter(cell, **params):
      data = cell.getData()
      val = cell.get_value()
      
      if data['transaction_type']=='Total':
        color = self.colors['Total']['color']
        background_color = self.colors['Total']['backgroundColor']
        cell.getElement().style.backgroundColor = background_color
        cell.getElement().style.color = color
        val = f"<b>{val}</b>"
        return val   
        
      else:
        #transaction_id = data["transaction_id"]
        label = Label(text=val)
        return label
  
      

    # Entry formatter
    def format_entry(cell, **params):
      val = cell.getValue()
      data = cell.get_data()
      #print(data)
      trans_type = data['transaction_type']
      row_number = data.get('row_number', -1)
      transaction_id = data.get('transaction_id', 0)
      ym = params.get("year_month")
      locked = params.get("locked")
      column_type = params.get("column_type")
      table_type = params.get("table_type")
      #b_ym = f"{ym}B"
      #ly_ym = f"{ym}LY"

      if column_type == 'Actual' and table_type == 'Forecast':
        locked = True
        
      if trans_type == 'Actual':
        if params.get("backgroundColor", None):
          backgroundColor = params["backgroundColor"]
        if params.get("color", None):
          color = params["color"]
        #compare = data[ly_ym]
        #tooltip_prefix = "LY"
        bold = False
      elif trans_type == 'Total':
        backgroundColor = self.colors['Total']['backgroundColor']
        color = self.colors['Total']['color']
        #compare = val
        #tooltip_prefix = None
        bold = True
      elif column_type == 'Forecast':
        backgroundColor = self.colors['Editable']['backgroundColor']
        color = self.colors['Editable']['color']
        #compare = data[b_ym]          
        #tooltip_prefix = "Budget"
        bold = False        
      else:
        backgroundColor = self.colors['Forecast']['backgroundColor']
        color = self.colors['Forecast']['color']
        #compare = data[b_ym]          
        #tooltip_prefix = "Budget"
        bold = False
        
      cell.getElement().style.backgroundColor = backgroundColor
      cell.getElement().style.color = color

      #try:
      #  delta = (int(val) - int(compare)) / int(compare)
      #  delta = int(delta * 100)
      #except Exception:
      #  delta = "INF"

      #tooltip = f"{tooltip_prefix}: {FinancialNumber(compare):,.0f}" if tooltip_prefix is not None else None

      #if int(val) > int(compare):
      #  tooltip += f"\n+{delta}%"
      #  icon = 'fa:arrow-up'
      #elif int(val) < int(compare):              
      #  tooltip += f"\n{delta}%"
      #  icon = 'fa:arrow-down'
      #else:
      tooltip = None
      icon = None

      def tb_edited(sender, **params):
        self.revert_button.visible = True
        new_val = float(sender.text)
        row_number, transaction_id, entry_type, ym, old_val = sender.tag
        num_rows = len(table.data)
        old_total = float(table.data[num_rows-1][ym])
        old_row_total = float(table.data[row_number]['total'])
        new_total = old_total - old_val + new_val
        new_row_total = old_row_total - old_val + new_val
        table.data[row_number]['total'] = new_row_total
        table.data[num_rows -1][ym] = new_total
        table.data[row_number][ym] = new_val
        table.data[num_rows - 1]['total'] = sum(table.data[num_rows-1][ym_label] for ym_label in self.year_months)
        entry_index = f"{table_type}_{transaction_id}_{ym}"
        month = int(ym[4:])
        year = int(ym[0:4])
        fin_year = year + int(month>6)
        
        self.updated_entries[entry_index] = {
          'transaction_id': transaction_id,
          'transaction_type': table_type,
          'year_month': int(ym),
          'fin_year': fin_year,
          'timestamp': dt.date(year, month, 1),
          'amount': new_val
        }
        table.data = table.data
        #print(sender.tag, sender.text)
        
      if val is None:
        tb = None
      elif (trans_type == 'Total' or locked):
        tb = Label(
          #text = "{:,.0f}".format(FinancialNumber(val)),
          text = float(val),
          align='right',
          tooltip=tooltip,
          icon_align='right',
          icon=icon,
          foreground=color,
          background=backgroundColor,
          bold=bold,
        )
      else:
        tb = TextBox(
          text=float(val),
          type='number',
          align="right",
          #icon_align="left",
          tooltip = tooltip,
          #icon=icon,
          border=None,
          foreground=color,
          background=backgroundColor,
          bold=bold,
          tag=(row_number, transaction_id, table_type, ym, float(val))
        )
        tb.add_event_handler('lost_focus', tb_edited)
      return tb

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
        'formatter': transaction_formatter
      },
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
            "table_type": table_type,
            "column_type": transaction_type,
            "backgroundColor": self.colors[transaction_type]["backgroundColor"],
            "color": self.colors[transaction_type]["color"],
            "locked": locked
          },
          "width": 70,
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
    print(f"Table: {table_type}")
    print(f"Columns: {columns}")
    table.setColumns(columns)


  
  
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
    a_row_number = 0
    f_row_number = 0
    b_row_number = 0
    
    for row in self.data:
      if row['transaction_type']=='Budget':
        f_row = row.copy()
        f_row['row_number'] = f_row_number
        f_row_number += 1
        b_row = row.copy()
        b_row['row_number'] = b_row_number
        b_row_number += 1
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
        a_row = row.copy()
        a_row['row_number'] = a_row_number
        a_row_number += 1
        actual_rows.append(a_row)

    self.actual_data = actual_rows + [a_total_row]
    self.forecast_data = forecast_rows + [f_total_row]
    self.budget_data = budget_rows + [b_total_row]
    #self.actual_details_table.set_filter(zero_filter)
    #self.forecast_details_table.set_filter(zero_filter)
    #self.budget_details_table.set_filter(zero_filter)
    self.prepared = True
    #if self.year == 2024:
    #  print("2024 Actual Data")
    #  print(self.actual_data)
    #  print("2024 Forecast Data")
    #  print(self.forecast_data)
    #  print("2024 Budget Data")
    #  print(self.budget_data)


  
  def get_updated_entries(self):
    """ Returns all updated entries for submission to the backend """
    # Transform updated entries into a list per transaction_id
    new_entry_dict = {}
    for entry in self.updated_entries.values():
      transaction_entry_list = new_entry_dict.get(entry['transaction_id'], [])
      transaction_entry_list.append(entry)
      new_entry_dict[entry['transaction_id']] = transaction_entry_list
    return new_entry_dict


  
  def revert_changes(self):
    """ Reverts table to original state and discards any updated entries """
    self.updated_entries = {}
    self.actual_details_table_table_built()
    self.forecast_details_table_table_built()
    self.budget_details_table_table_built()


  
  def revert_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.revert_changes()
    self.revert_button.visible = False


  
  def create_actual_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.create_line(entry_type='Actual')


  
  def create_forecast_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.create_line(entry_type='Forecast')

  
  def create_line(self, entry_type='Forecast'):
    vendor_name = self.vendor.vendor_name
    if entry_type != 'Actual':
      transaction_type = 'Budget'
    else:
      transaction_type = entry_type
    
    tb = TextBox(placeholder='Enter Description')
    resp = alert(tb, title=f"Enter description for a new {entry_type} Line for {vendor_name}")
    if resp:
      description = tb.text
      actual_id = self.actual_transaction_id
      if actual_id is not None:
        actual = self.transactions.get(actual_id)
      else:
        actual = {
          'owner': None,
          'account_code': "Software Maintenance",
          'cost_centre': "IT",
          'lifecycle': "Existing",
          'category': "Operations",
          'service_change': "Organic growth",
          'billing_type': "Consumption",
        }
      new_trans = self.transactions.blank({
        'description': description,
        'vendor': self.vendor,
        'vendor_id': self.vendor.vendor_id,
        'transaction_type': transaction_type,
        'owner': actual['owner'],
        'account_code': actual['account_code'],
        'cost_centre': actual['cost_centre'],
        'lifecycle': actual['lifecycle'],
        'category': actual['category'],
        'service_change': actual['service_change'],
        'billing_type': actual['billing_type'],
        'source': 'manual'
      })
      self.transactions.new(transaction=new_trans)
      transaction_id = new_trans.transaction_id
      print(f"New Transaction ID = {transaction_id}")
      
      months = [7,8,9,10,11,12,1,2,3,4,5,6]
      new_entries = [
        {
          'transaction_id': transaction_id,
          'transaction_type': entry_type,
          'year_month': (self.year-(m>6))*100+m,
          'fin_year': self.year,
          'timestamp': dt.date(self.year-(m>7), m, 1),
          'amount': 0.0
        } for m in months
      ]
      new_trans.add_entries(new_entries)
      self.load_data()
      self.prepare_data()
      self.forecast_panel.visible = True
      self.actual_panel.visible = True
      self.revert_changes()

  def save_updated_entries(self, entries):
    vendor = self.vendor
    self.transactions.load(vendor_name=vendor.vendor_name)
    count = 0
    for transaction_id, trans_entries in entries.items():
      transaction = self.transactions.get(transaction_id)
      if transaction is None:
        print(f"Can't find transaction {transaction_id} associated with Vendor {vendor.name}")
      else:
        transaction.add_entries(trans_entries, overwrite=True)
        count += len(trans_entries)
    Notification(f"{count} entries updated!").show()

  def year_selector_change(self, **event_args):
    """This method is called when an item is selected"""
    print(f"Selected year: {self.year}")
    self.load_data()
    self.prepare_data()
    self.actual_details_table.clear()    
    self.forecast_details_table.clear()
    self.budget_details_table.clear()
    self.forecast_panel.visible = True
    self.actual_panel.visible = True
    self.revert_changes()
    

    
    