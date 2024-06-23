from ._anvil_designer import ContentTemplate
from anvil import *
import plotly.graph_objects as go
##import anvil.google.auth, anvil.google.drive
##from anvil.google.drive import app_files
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
    
    self.fin_year = Data.CURRENT_YEAR
    
    self.account_data = None
    self.budget_data = None
    self.accounts = []  #Data.ACCOUNTS_D
    self.expense_accounts = [] #[ i for i, x in self.accounts.items() if self.accounts[i]['type']=='EXPENSE' ]

    #self.arrows = { True: 'fa:angle-down', False: 'fa:angle-right'}
    self.overview_visible = True
    self.details_visible = False
    self.details_loaded = False
    self.org_visible = False
    self.balance_visible = False
    self.balance_loaded = False

    self.balance_data = {} 
    
    self.end_date = self.fin_year
    #self.start_date = datetime(self.fin_year.year - 1, 7, 1, 0, 0, 0)    
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
    data = None #anvil.server.call('get_accounttype_by_month', end=self.fin_year, compare=self.compare, show=self.show)
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

      
    
  
  def initialise_resolution_chart(self, resolution_data):
    return
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
    self.overview_label_str = f"{self.fin_year}"
    return
        
  def initialise_account_grid(self):
    pass


    
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



  def show_expense_graph(self):
    return

  def account_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.show_expense_graph()

  def details_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.details_visible = not self.details_visible
    #self.details_link.icon = self.arrows[self.details_visible]
    if self.details_visible:
      self.tracking_table_1.load_data(self.fin_year)
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
    pass
    """This method is called when the link is clicked"""
    #self.balance_visible = not self.balance_visible
    #self.balance_link.icon = self.arrows[self.balance_visible]
    #if not self.balance_loaded:
    #  self.setup_balance_sheet()
    #self.refresh_data_bindings()


  