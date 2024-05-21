from ._anvil_designer import ContentTemplate
from anvil import *
import plotly.graph_objects as go
##import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .HeadlineStats import HeadlineStats
from ... import Data
from datetime import datetime

class Content(ContentTemplate):
  """This Form populates all the data and charts on the Dashboard.
  
  The data is displayed using the following Custom Components:
      1) HeadlineStats x3
      2) ProgressGraph x2 
      3) ResolutionGraph
    
    The charts are all custom JavaScript components that accept certain arguments.
    They take care of their own display.
    """
  
  def __init__(self, fin_year_date=None, **properties):
    # Set Form properties and Data Bindings.
    self.compare = properties.get('compare', 'budget')
    self.show = properties.get('show', 'absolute' )
    self.account_filter = properties.get('account_filter', 'all')
    
    self.fin_year = fin_year_date or self.calc_fin_year(datetime.now())
    self.account_data = None
    self.budget_data = None
    self.accounts = Data.ACCOUNTS_D
    self.expense_accounts = [ i for i, x in self.accounts.items() if self.accounts[i]['type']=='EXPENSE' ]

    #self.arrows = { True: 'fa:angle-down', False: 'fa:angle-right'}
    self.overview_visible = True
    self.details_visible = False
    self.details_loaded = False
    self.org_visible = False
    self.balance_visible = False
    self.balance_loaded = False

    self.balance_data = {} 
    
    self.end_date = self.fin_year
    self.start_date = datetime(self.fin_year.year - 1, 7, 1, 0, 0, 0)    
    self.set_overview_label_str()
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    # This event is called from the HeadlineStats Form
    self.flow_panel_headline_stats.set_event_handler('x-open-transactions', self.open_transactions)
    #self.initialise_account_grid()
    #self.setup_balance_sheet()
    anvil.js.get_dom_node(self.next_button).style.cursor = 'pointer'
    anvil.js.get_dom_node(self.prev_button).style.cursor = 'pointer'
    #self.show_expense_graph()

    
  def set_compare_show(self, name, value):
    if name=='compare':
      self.compare = value
    elif name=='show':
      self.show = value
    elif name == 'account_filter':
      self.account_filter = value
      
    self.set_overview_label_str()
    self.refresh_data_bindings()

  def calc_fin_year(self, date):
    return datetime(date.year + (date.month > 7), 6, 30, 0, 0, 0)
    
  def initialise_headline_cards(self, headline_stats, period):
    """Add three HeadlineStats components to the Dashboard.
    
    Arguments:
      headline_stats: dict of data for each of the HeadlineStats components in this form:
                      {
                      'unknown': {'delta':delta, 'number':number},
                      'income':{'delta':delta, 'number':number},
                      'expense':{'delta':delta, 'number':number}
                      }
      period (string): number of days of data being displayed            
    """
    self.flow_panel_headline_stats.clear()
    # Add three HeadlineStats components to the Dashboard
    if self.compare == 'budget':
      comment = ' YTD vs Budget'
    else:
      comment = ' YTD vs LY'
      
    # Net Worth    
    self.flow_panel_headline_stats.add_component(HeadlineStats(
      title="Net Worth", 
      value="${0:,.0f}".format(headline_stats['net_worth']['number']), 
      delta=headline_stats['net_worth']['delta'], 
      time_period=" YTD vs LY", 
      good=(headline_stats['net_worth']['delta']>0) and 'positive' or 'negative'
    ))
    # Income total
    self.flow_panel_headline_stats.add_component(HeadlineStats(
      title="Income", 
      delta=headline_stats['income']['number'], 
      value="+${0:,.0f}".format(round(headline_stats['income']['delta'],0)).replace('+$-', '-$'), 
      time_period=comment, 
      good=(headline_stats['income']['delta']>0) and 'positive' or 'negative'
    ))
    # Expenses total
    self.flow_panel_headline_stats.add_component(HeadlineStats(
      title="Expense", 
      delta=headline_stats['expense']['number'], 
      value="+${0:,.0f}".format(round(headline_stats['expense']['delta'],0)).replace('+$-', '-$'), 
      time_period=comment, 
      good=(headline_stats['expense']['delta']<0) and 'positive' or 'negative'
    ))

  # This is called initially in the form_show event of the Dashboard Form
  def initialise_progress_charts(self, progress_dash_stats):
    """Collect data and populate the two ProgressGraph charts, and the text for the accompanying labels.
    
    Arguments:
      progress_dash_stats: dict of data in this form:
                          {
                            'resolved': {
                              'total_resolved': len(resolved_tickets), 'closed_on_first':len(closed_on_first)
                            }, 
                            'customers':{
                              'new_customers':len(new_customers), 'returning_customers':len(returning_customers)
                            }
                          }  
    """
    self.header_column_panel.visible = True
    self.content_column_panel.visible = True

  def setup_summary_chart(self): 
    data = anvil.server.call('get_accounttype_by_month', end=self.fin_year, compare=self.compare, show=self.show)
    if data is not None:
      (labels, income, expense) = data
      resolution_data = {
        'dates': labels,
        'data': {'income': income, 'expense': expense}
      }
      #print(resolution_data)
      return resolution_data
    else:    
      return None

  def setup_balance_sheet(self):
    if not self.balance_loaded:
      self.balance_data = anvil.server.call('get_balance_sheet', self.fin_year)
      self.balance_loaded = True
      
    grid = self.balance_grid
    grid.clear()
    entries = None
    
    prev_year = datetime(self.fin_year.year - 1, 6, 30, 0, 0, 0)

    py_str = prev_year.strftime('FY%y')
    cy_str = self.fin_year.strftime('FY%y')

    grid.columns = [
      { "id": "A", "title": "", "data_key": "type", "width": 250 },
      { "id": cy_str, "title": "{0} YTD".format(cy_str), "data_key": cy_str, "width": 200 },
      { "id": py_str, "title": py_str, "data_key": py_str, "width": 200 },
      { "id": "D", "title": "Change", "data_key": "change", "width": 200 },
    ]
    
    grid.columns = grid.columns

    subtypes = {}
    for s in self.balance_data['subtype']:
      t_level = subtypes.get(s['type'], {})
      s_level = t_level.get(s['subtype'], {})
      s_level[s['year']] = s['balance']
      t_level[s['subtype']] = s_level
      subtypes[s['type']] = t_level

    types = {}
    for t in self.balance_data['type']:
      t_level = types.get(t['type'], {})
      t_level[t['year']] = t['balance']
      types[t['type']] = t_level
    
    totals = { x['year'] : x['balance'] for x in self.balance_data['net_worth'] }
    
    years =   { 
                self.fin_year.year: { 'label': cy_str, 'sign': 1 }, 
                prev_year.year: { 'label': py_str, 'sign': -1 }
              }
        
    for t, label in { 'ASSET': 'Assets', 'LIABILITY': 'Liabilities'}.items():
      row = DataRowPanel()
      #row.background = '#969A9C'
      row.spacing_above = 'none'
      row.spacing_below = 'none'
      row.row_spacing = 20
  
      text = '{0}'.format(label)
      textbox = Label(text=text, bold=True, foreground='black', underline=True, font_size=14)
      row.add_component(textbox, column='A')
      grid.add_component(row)

      for s, v in subtypes[t].items():
        row = DataRowPanel()
        #row.background = '#969A9C'
        row.spacing_above = 'none'
        row.spacing_below = 'none'
        row.row_spacing = 20

        text = '{0}'.format(s)
        textbox = Label(text=text, bold=False, foreground='black', underline=False, font_size=14)
        row.add_component(textbox, column='A')

        delta = 0
        for y, y_data in years.items():
          b = v.get(y, 0)
          #b = get_balance(subtype_data, 'subtype', s, y['year'])
          text = '{:,.0f}'.format(b)
          textbox = Label(text=text, bold=False, foreground='black', underline=False, font_size=14)
          row.add_component(textbox, column=y_data['label'])
          delta += b * y_data['sign']

        text = '+{:,.0f}'.format(delta).replace('+-', '-')
        foreground = 'green' if delta >= 0 else 'red'
        textbox = Label(text=text, bold=False, foreground=foreground, underline=False, font_size=14)
        row.add_component(textbox, column='D')
          
        grid.add_component(row)

      row = DataRowPanel()
      #row.background = '#969A9C'
      row.spacing_above = 'none'
      row.spacing_below = 'none'
      row.row_spacing = 20

      text = 'Total {0}'.format(label)
      textbox = Label(text=text, bold=True, foreground='black', underline=True, font_size=14)
      row.add_component(textbox, column='A')
      
      delta = 0
      for y, y_data in years.items():
        b = types[t].get(y, 0)
        #b = get_balance(types, 'type', t, y['year'])
        text = '{:,.0f}'.format(b)
        textbox = Label(text=text, bold=True, foreground='black', underline=False, font_size=14)
        row.add_component(textbox, column=y_data['label'])
        delta += b * y_data['sign']

      text = '+{:,.0f}'.format(delta).replace('+-', '-')
      foreground = 'green' if delta >= 0 else 'red'
      textbox = Label(text=text, bold=True, foreground=foreground, underline=False, font_size=14)
      row.add_component(textbox, column='D')
      
      grid.add_component(row)

    row = DataRowPanel()
    #row.background = '#969A9C'
    row.spacing_above = 'none'
    row.spacing_below = 'none'
    row.row_spacing = 20

    text = 'Net Worth'
    textbox = Label(text=text, bold=True, foreground='black', underline=True, font_size=14)
    row.add_component(textbox, column='A')
    
    delta = 0
    for y, y_data in years.items():
      b = totals.get(y, 0)
      text = '{:,.0f}'.format(b)
      textbox = Label(text=text, bold=True, foreground='black', underline=False, font_size=14)
      row.add_component(textbox, column=y_data['label'])
      delta += b * y_data['sign']

    text = '+{:,.0f}'.format(delta).replace('+-', '-')
    foreground = 'green' if delta >= 0 else 'red'
    textbox = Label(text=text, bold=True, foreground=foreground, underline=False, font_size=14)
    row.add_component(textbox, column='D')

    grid.add_component(row)
      
    
  
  def initialise_resolution_chart(self, resolution_data):
    """Collect data and populate the ResolutionGraph custom component. 
    
    Arguments:
      resolution_data: dict of data in this form:
                      {'dates':dates, 'data':
                          {'resolved':resolved, 
                          'unresolved':unresolved}
                      }
    Dates is a list of dates in the form '%A, %d' 
    e.g. ['Friday, 07', 'Saturday, 08', 'Sunday, 09', 'Monday, 10', 'Tuesday, 11', 'Wednesday, 12', 'Thursday, 13']
    Resolved and unresolved are lists of numbers of tickets created on the days in the dates list 
    e.g [1,0,1,2,3,4,5]
    """
    labels = resolution_data['dates']
    data = resolution_data['data']
    self.resolution_graph.labels = labels
    self.resolution_graph.datasets = [{
            'label': 'Income',
            'backgroundColor': '#9389DF',
            'borderColor': '#7D71D8',
            'data': data['income']
        },{
            'label': 'Expense',
            'backgroundColor': '#00FFAF',
            'borderColor': '#00FFAF',
            'data': data['expense']
        }]
   
  def open_transactions(self, account, **event_args):
    # This event is raised from the 'HeadlineStats' Form
    # Raise an event on the parent 'Dashboard' Form
    self.parent.raise_event('x-open-transactions', account=account)

  def set_overview_label_str(self):
    year = self.fin_year.year
    if self.compare == 'budget':
      if self.show == 'absolute':
        self.overview_label_str = '{0} vs Budget'.format(year % 100)
      else:
        self.overview_label_str = '{0} minus Budget'.format(year % 100)
    else:
      if self.show == 'absolute':
        self.overview_label_str = '{0} vs FY{1}'.format(year % 100, (year - 1) % 100)
      else:
        self.overview_label_str = '{0} minus FY{1}'.format(year % 100, (year - 1) % 100)
    if self.account_filter == 'budget':
      self.overview_label_str += ' (budgeted accounts only)'
    elif self.account_filter == 'discretionary':
      self.overview_label_str += ' (discretionary accounts only)'
    
  def initialise_account_grid(self):
    if not self.details_loaded:
      self.account_data = anvil.server.call('get_accounts_by_month', end=self.fin_year, compare=self.compare)
      self.budget_data = anvil.server.call('get_budget_entries', self.fin_year.strftime('FY%y'))
      self.details_loaded = True
    self.display_account_grid()

  def display_account_grid(self):
    account_data = self.account_data
    budget_data = self.budget_data
    accounts = self.accounts

    income = account_data['income']
    expense = account_data['expense']
    c_data = { c['account']: c for c in account_data['compare'] }
        
    def format_total(cell, **kwargs):
      return "<b>{0}</b>".format(cell.getValue())

    keys = income[0].copy()
    keys.pop('account', None)
    keys = list(keys.keys())
    keys.sort()
    self.date_keys = keys
    compare_title = (self.compare == "budget") and "Budget" or "LY"
    
    columns =  [ { "field": "account", "title": "Account", "width": 200, 'formatter': self.account_formatter, 'headerSort': False } ]
    columns += [ { "field": i, "title": i, "width": 80, "hozAlign": 'right', "headerSort": False, "formatter": "plaintext" } for i in keys ]
    columns += [ { "field": 'total', "title": 'Total', "width": 80, "hozAlign": 'right', "headerSort": False, "formatter": format_total } ]
    columns += [ { "field": 'compare', "title": compare_title, "width": 80, "hozAlign": 'right', "headerSort": False, "formatter": format_total } ]

    # Expense Table
    tab = self.tabulator_1
    tab.columns = columns.copy()
    tab.data = self.build_table_data(expense, c_data, account_type='Expense', background_color='#01ffae')

    # Income Table
    tab = self.tabulator_2
    tab.columns = columns.copy()
    tab.data = self.build_table_data(income, c_data, account_type='Income', background_color='#9588df' )
    

  def build_table_data(self, accounts, c_data, account_type='Expense', background_color='#01ffae'):
    t_data = []
    totals = { 'actuals': { 'months': {}, 'accounts': {} }, 'compare': { 'months': {}, 'accounts': {} } }
    
    budget_only = (self.account_filter == 'budget')
    discretionary = (self.account_filter == 'discretionary')
  
    for r in accounts:
      if budget_only and (r['account'] not in budget_data):
        print("Ignoring account not in Budget: {0}".format(r['account']))
        
      elif discretionary and not accounts[r['account']]['discretionary']:
        print("Ignoring non-disctretionary account: {0}".format(r['account']))
      else:
        account_name = r['account']
        print("Including account: {0}".format(account_name))
        t_row = self.prepare_t_row(r, type='EXPENSE', link_color='black', back_color=background_color, totals=totals, c_data_raw=c_data.get(account_name, None))
        t_data.append(t_row)

    # Monthly totals for Expense
    if len(totals['actuals']['months'])>0:
      totals['actuals']['months']['account'] = '{0} Total'.format(account_type) 
      t_row = self.prepare_t_row(totals['actuals']['months'], type=account_type.upper(), link_color='black', back_color=background_color, totals=None, c_data_raw=totals['compare']['months'])
      t_data.append(t_row)
    return t_data

  
  def prepare_t_row(self, r_raw, link_color='blue', back_color='white', type='EXPENSE', c_data_raw=None, totals=None):  
    # Copy these two objects as we 'pop' keys out of them
    r = r_raw.copy()
    if c_data_raw is not None:
      c_data = c_data_raw.copy()
    else:
      c_data = None
      
    row = {}

    total = 0
    c_total = 0
    account = r.pop('account')
    
    if (c_data is not None):
      c_data.pop('account', None)
      budget = sum(list(c_data.values()))
      text = account
    else:
      text = account
      budget = 0
      
    row['account'] = text
    if self.show == 'deltas':
      row['compare'] = "{:,.0f}".format(0)
    else:
      row['compare'] = "{:,.0f}".format(budget)
    
    for i, v in r.items():
      if v>0:
        print("{0} : {1}".format(account, v))
      # Get the comparison value for this account/month combination
      if c_data is not None:
        c_value = c_data[i]
      else:
        c_value = 0

      if self.show == 'deltas':
        show_value = v - c_value        
      else:
        show_value = v
        
      text = '{:,.0f}'.format(show_value).replace('$-', '-$')

      # Update totals for this Account
      c_total = c_total + c_value
      total = total + v

      # Update the total for the Month
      if totals is not None:
        totals['actuals']['months'][i] = totals['actuals']['months'].get(i, 0) + v
        totals['compare']['months'][i] = totals['compare']['months'].get(i, 0) + c_value
        bold = False
      else:
        bold = True
                    
      row[i] = text

    # All months are now complete - update Account totals unless this is a Income/Expense total row
    if totals is not None:
      totals['actuals']['accounts'][account] = total
      totals['compare']['accounts'][account] = c_total
  
    # Last column is the total for the Account over all Months
    if self.show == 'deltas':
      show_value = total - c_total
    else:
      show_value = total
      
    text = '{:,.0f}'.format(show_value).replace('$-', '-$')
      
    row['total'] = text
    return row


  def account_formatter(self, **params):
    cell_value = params['cell'].getValue()
    
    def open_account(**event_args):
      sender = event_args['sender']
      account_name = sender.text
      print("Opening account: {0}".format(account_name))
      account = anvil.server.call('get_account', account_name)
      homepage = get_open_form()
      homepage.open_account_transactions(account)
      return

    if "Total" in cell_value:
      link = cell_value
    else:
      link = Link(text=cell_value)
      link.set_event_handler('click', open_account)
    return link

    
  def next_button_mouse_up(self, x, y, button, **event_args):
    """This method is called when a mouse button is released on this component"""
    old_year = self.fin_year
    self.fin_year = datetime(self.fin_year.year + 1, 6, 30, 0, 0, 0)
    data = self.setup_summary_chart()
    if data is None:
      # No data in this direction - adandon!
      self.fin_year = old_year
      Notification("No data in the next Financial Year!").show()
    else:
      self.details_loaded = False
      self.details_visible = False
      self.org_visible = False
      self.balance_loaded = False
      self.balance_visible = False
      #self.initialise_account_grid()
      self.initialise_resolution_chart(data)
      self.end_date = self.fin_year
      self.start_date = datetime(self.fin_year.year - 1, 7, 1, 0, 0, 0)
      
      filters = {}
      date_filters = { 'fin_year': self.fin_year.date(),
                       'end':      self.end_date.date(),
                       'start':    self.start_date.date()
                     } 
      
      date_filters['time_period'] = (date_filters['fin_year'] - date_filters['start']).days + 1
      # Get all the data to populate the dashboard from the server
      headline_stats, progress_dash_stats, resolution_data = anvil.server.call('get_dashboard_data', date_filters, filters)
      self.initialise_headline_cards(headline_stats, date_filters['time_period'])

      self.refresh_data_bindings()

  
  def prev_button_mouse_up(self, x, y, button, **event_args):
    """This method is called when a mouse button is released on this component"""
    old_year = self.fin_year
    self.fin_year = datetime(self.fin_year.year - 1, 6, 30, 0, 0, 0)
    data = self.setup_summary_chart()
    if data is None:
      # No data in this direction - adandon!
      self.fin_year = old_year
      Notification("No data in the previous Financial Year!").show()
    else:  
      self.details_loaded = False
      self.details_visible = False
      self.org_visible = False
      self.balance_loaded = False
      self.balance_visible = False
      #self.initialise_account_grid()
      self.initialise_resolution_chart(data)
      self.end_date = self.fin_year
      self.start_date = datetime(self.fin_year.year - 1, 7, 1, 0, 0, 0)
      
      filters = {}
      date_filters = { 'fin_year': self.fin_year.date(),
                       'end':      self.end_date.date(),
                       'start':    self.start_date.date()
                     } 
      
      date_filters['time_period'] = (date_filters['fin_year'] - date_filters['start']).days + 1
      # Get all the data to populate the dashboard from the server
      headline_stats, progress_dash_stats, resolution_data = anvil.server.call('get_dashboard_data', date_filters, filters)
      self.initialise_headline_cards(headline_stats, date_filters['time_period'])

      self.refresh_data_bindings()

  def tabulator_1_row_formatter(self, row, **event_args):
    """This method is called when the row is rendered - manipulate the tabulator row object"""
    data = row.getData()
    if "Expense Total" in data.account:
      row.getElement().style.backgroundColor = "#01ffae"
      row.getElement().style.fontWeight = "bold"
    if int(data.total.replace(',','')) > int(data.compare.replace(',','')):
      row.getCell('total').getElement().style.color = "red"
    if self.show =='deltas':
      for i in self.date_keys:
        if int(data[i].replace(',', ''))>0:
          row.getCell(i).getElement().style.color = "red"

  def tabulator_2_row_formatter(self, row, **event_args):
    """This method is called when the row is rendered - manipulate the tabulator row object"""
    data = row.getData()
    if "Income Total" in data.account:
      row.getElement().style.backgroundColor = "#9588df"
      row.getElement().style.fontWeight = "bold"
    if int(data.total.replace(',','')) < int(data.compare.replace(',','')):
      row.getCell('total').getElement().style.color = "red"
    if self.show =='deltas':
      for i in self.date_keys:
        if int(data[i].replace(',', ''))<0:
          row.getCell(i).getElement().style.color = "red"


  def show_expense_graph(self):
    """ Build and render a pie chart that breaks down expenses by organisation """
    if self.account_dropdown.selected_value == 'All' or self.account_dropdown.selected_value is None:
      account_names = self.expense_accounts
    else:
      account_names = [self.account_dropdown.selected_value]
      
    self.org_data = { 'organisations': [], 'values': [] }
    #anvil.server.call('get_expenses_by_organisation', fin_year=self.fin_year, account_names=account_names, threshold=0.005)
      
    # expect data in the form of:
    #   organisation
    #   amount
    data = self.org_data
    
    labels = data['organisations']
    values = data['values']
    total = sum(values)
    
    #pie_plot = go.Pie(labels=labels, values=values)
    layout = {
      'title': "Total amount: ${:,.0f}".format(total)
        }

    # Make the multi-bar plot
    #self.org_plot.data = pie_plot
    #self.org_plot.layout = layout

  def account_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.show_expense_graph()

  def details_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.details_visible = not self.details_visible
    #self.details_link.icon = self.arrows[self.details_visible]
    if not self.details_loaded:
      self.initialise_account_grid()
    self.refresh_data_bindings()

  def overview_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.overview_visible = not self.overview_visible
    #self.overview_link.icon = self.arrows[self.overview_visible]
    self.refresh_data_bindings()

  def org_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.org_visible = not self.org_visible
    #self.org_link.icon = self.arrows[self.org_visible]
    if self.org_visible:
      self.show_expense_graph()
    self.refresh_data_bindings()

  def balance_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.balance_visible = not self.balance_visible
    #self.balance_link.icon = self.arrows[self.balance_visible]
    if not self.balance_loaded:
      self.setup_balance_sheet()
    self.refresh_data_bindings()


  