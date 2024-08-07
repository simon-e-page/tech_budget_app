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
    self.fin_year = Data.get_year()
    
    self.budget_data = None
    self.overview_visible = True
    self.details_visible = False
    self.details_loaded = False
    self.org_visible = False
    self.budget_visible = False

    self.budget = { 'total': 0, 'delta': 0 }
    self.forecast = { 'total': 0, 'delta': 0 }
    #self.actuals = { 'total': 0, 'delta': 0 }

    self.balance_data = {} 
    
    self.end_date = self.fin_year
    #self.set_overview_label_str()
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    # This event is called from the HeadlineStats Form
    self.flow_panel_headline_stats.set_event_handler('x-open-transactions', self.open_transactions)
    self.tracking_table_1.set_event_handler('x-data-loaded', self.initialise_headline_cards)
    #anvil.js.get_dom_node(self.next_button).style.cursor = 'pointer'
    #anvil.js.get_dom_node(self.prev_button).style.cursor = 'pointer'

        
  def initialise_headline_cards(self, sender, **kwargs):
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
    empty = { 'total': 0, 'delta': 0 }
    
    # Add three HeadlineStats components to the Dashboard
    actuals = kwargs.get('actuals', empty)
    
    # Budget   
    self.flow_panel_headline_stats.add_component(HeadlineStats(
      title="Budget", 
      value="${0:,.0f}".format(self.budget['total']), 
      delta=self.budget['delta'], 
      time_period=" vs LY", 
      good=(self.budget['delta']<0) and 'positive' or 'negative'
    ))
    
    # Forecast
    self.flow_panel_headline_stats.add_component(HeadlineStats(
      title="Forecast", 
      delta=self.forecast['delta'], 
      value="+${0:,.0f}".format(round(self.forecast['total'],0)).replace('+$-', '-$'), 
      time_period=" vs LY", 
      good=(self.forecast['delta']<0) and 'positive' or 'negative'
    ))
    
    # Actuals
    self.flow_panel_headline_stats.add_component(HeadlineStats(
      title="Actuals", 
      delta=actuals['delta'], 
      value="${0:,.0f}".format(round(actuals['total'],0)).replace('+$-', '-$'), 
      time_period="vs LY", 
      good=(actuals['delta']<0) and 'positive' or 'negative'
    ))

  # This is called initially in the form_show event of the Dashboard Form
  def initialise_progress_charts(self, progress_dash_stats):
    return

  def setup_summary_chart(self): 
    return
      
  def initialise_resolution_chart(self, resolution_data):
    return
   
  def open_transactions(self, account, **event_args):
    # This event is raised from the 'HeadlineStats' Form
    # Raise an event on the parent 'Dashboard' Form
    self.parent.raise_event('x-open-transactions', account=account)


  def details_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.details_visible = not self.details_visible
    #self.details_link.icon = self.arrows[self.details_visible]
    if self.details_visible:
      self.tracking_table_1.load_data(self.fin_year)
    self.refresh_data_bindings()


  def budget_link_click(self, **event_args):
    self.budget_visible = not self.budget_visible
    if self.budget_visible:
      self.budget_table_1.load_data(self.fin_year)
    self.refresh_data_bindings()

  