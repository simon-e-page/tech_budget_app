from ._anvil_designer import DashboardTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server
from datetime import datetime, timedelta, date
from .. import Data


class Dashboard(DashboardTemplate):
  """This Form fetches the information required to populate the Dashboard from the server.
  
  It send this information to the 'Content' Form to populate the charts and cards.
  """
  
  def __init__(self, use_dashboard_cache=True, **properties):
    # Initialise a dict of empty filters when the dashboard loads
    self.filters = {}
    # Initialise a dict of empty date filters when the dashboard loads
    self.date_filters = {}
    self.use_cache = use_dashboard_cache
    self.initialise_start_dates()
    # This returns a list of tuples to form the items of the category_dropdown. 
    # category_dropdown is data bound to self.categories
    self.accounts = Data.ACCOUNTS_D.get_dropdown()
    #self.categories = Data.CATEGORIES
    # This returns a list of tuples to form the items of the priority_dropdown. 
    # priority_dropdown is data bound to self.priorities
    #self.priorities = Data.PRIORITIES
    # Set Form properties and Data Bindings.
    properties['compare'] = "budget"
    properties['show'] = "absolute"
    properties['account_filter'] = 'all'
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.set_event_handler('x-open-transactions', self.open_transactions)
    
  #def set_dashboard_cache(self, use_cache=True):
  #  self.use_cache = use_cache
    
  def initialise_start_dates(self):
    """Initialise the DatePickers so that Dashboard auto-displays data for the previous week"""
    self.date_filters['start'] = (date.today() - timedelta(days=6))
    self.date_filters['end'] = date.today()
    # Work out the time period for the dashboard data
    self.date_filters['time_period'] = (self.date_filters['end'] - self.date_filters['start']).days
    
  def load_dash_data(self, sender, **event_args):
    # If a filter has been removed (value set to None), remove it from self.filters
    if sender.selected_value is None:
      self.filters = {k: v for k, v in self.filters.items() if v is not None}
    # Fetch dashboard data for the new filters
    self.initialise_dashboard_data()
      
  def initialise_dashboard_data(self):
    """Fetch the data required to populate the 'Dashboard' from the server.
    
    Send it to the 'Content' Form to populate the appropriate labels and charts
    """
    
    month = datetime.now().month
    year = datetime.now().year
    self.date_filters['fin_year'] = datetime(year + (month > 7), 6, 30, 0, 0, 0).date()
    self.date_filters['start'] = self.date_filters['fin_year']

    # Ensure timeperiod runs from start date to *end* of end date, by adding a day to end date
    self.date_filters['end'] =datetime.now().date() + timedelta(days=1)
    # Work out the time period for the dashboard data
    self.date_filters['time_period'] = (self.date_filters['end'] - self.date_filters['start']).days
    # Get all the data to populate the dashboard from the server
    headline_stats, progress_dash_stats, resolution_data = anvil.server.call('get_dashboard_data', 
                                                                             date_filters=self.date_filters, 
                                                                             dash_filters=self.filters, 
                                                                             compare=self.dash_content.compare,
                                                                             use_cache=self.use_cache
                                                                            )

    resolution_data = self.dash_content.setup_summary_chart()
    
    # Send the data to the 'Content' Form to populate the charts and data
    self.dash_content.initialise_headline_cards(headline_stats, str(self.date_filters['time_period']))
    self.dash_content.initialise_resolution_chart(resolution_data)
    self.dash_content.initialise_progress_charts(progress_dash_stats)
    self.use_cache = True
    
  def open_transactions(self, account, **event_args):
    # This receieves a 'account' from the 'HeadlineStats' Form, 
    if account == "Unknown":
      # If the "Unassigned" card is clicked, set self.filters['owner'] to the NO_AGENTS_SELECTED variable
      #unknown_account =  app_tables.accounts.get(name=account)
      self.filters['account'] = account
      
    homepage = get_open_form()
    homepage.open_transactions(initial_filters=self.filters)
    
  def form_show(self, **event_args):
    self.initialise_dashboard_data()

  def reset_filters_link_click(self, **event_args):
    self.filters = {}
    self.initialise_start_dates()
    self.refresh_data_bindings()
    self.initialise_dashboard_data()

  def compare_show_changed(self, sender, **event_args):
    """This method is called when this radio button is selected"""
    self.dash_content.set_compare_show(name=sender.group_name, value=sender.value)
    #print(self.compare_show)
    self.initialise_dashboard_data()
    self.dash_content.initialise_account_grid()
    self.refresh_data_bindings()
  

