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

from ...Tickets.BudgetLines.ImportActuals import ImportActuals
from .AttributeReview import AttributeReview

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

    self.task = None
    self.loaded = False
    self.raw_data = None

    self.budget = { 'total': 0, 'delta': 0 }
    self.forecast = { 'total': 0, 'delta': 0 }

    self.actions = [ 
      ('Import actuals', self.import_actuals),
      ('Refresh and reload', self.reset),
      ('Download quarterly report', self.download_quarterly),
      ('Analyse attributes', self.review_attributes),
      ('Export to Excel', self.export_excel),
    ]
    
    self.balance_data = {} 
    
    self.end_date = self.fin_year
    self.add_event_handler('x-refresh-tables', self.refresh_tables)
    #self.set_overview_label_str()
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    # This event is called from the HeadlineStats Form
    self.flow_panel_headline_stats.set_event_handler('x-open-transactions', self.open_transactions)
    self.initialise_headline_cards()
    self.tracking_table_1.set_event_handler('x-data-loaded', self.update_headline_cards)
    self.budget_table_1.set_event_handler('x-data-loaded', self.update_headline_cards)
    #anvil.js.get_dom_node(self.next_button).style.cursor = 'pointer'
    #anvil.js.get_dom_node(self.prev_button).style.cursor = 'pointer'
    self.load_data(self.fin_year)
    d = self.load_quarterly_data()
    self.quarterly_table.prepare_data(d)

  
  def refresh_tables(self, sender, **event_args):
    print(f"Got refresh tables event from {sender}")
    self.refresh = True
    

  def load_quarterly_data(self):
    data = Data.get_quarterly_table()
    return data
      
  def reset(self):
    self.loaded = False
    self.load_data(self.fin_year, refresh=True)
    d = self.load_quarterly_data()
    self.quarterly_table.prepare_data(d)

  
  def get_data(self):
    return self.raw_data


  
  def load_data(self, year, refresh=False):
    if self.task is not None or self.loaded:
      return
      
    with anvil.server.no_loading_indicator:
      task = Data.get_tracking_table_background(year, refresh)
      if task is None:
        print("Error launching background task!")
        return
  
      #print(f"Got task: {task}")
      self.task = task
      t = anvil.Timer(interval=1)
    
      def test_loaded(**event_args):
        task = self.task
        if task is None:
          print("Error: No Task object!!")
          t.interval = 0
          return
          
        if not task.is_running():
          t.interval = 0
          #print("Fnished Loading!")
          d = task.get_return_value()
          if isinstance(d, dict):
            self.prepare_components(d)
          else:
            print(d)
          self.task = None
          t.remove_from_parent()
          
      t.set_event_handler('tick', test_loaded)
      self.add_component(t)


  
  def prepare_components(self, d):
    self.raw_data = d
    self.tracking_table_1.prepare_data(d)
    self.budget_table_1.prepare_data(d)


  
  def update_headline_cards(self, sender, **kwargs):
    actuals = kwargs.get('actuals', None)
    budgets = kwargs.get('budgets', None)
    forecasts = kwargs.get('forecasts', None)
    
    # Budget   
    if budgets:
      self.budget_card.value = "${0:,.0f}".format(budgets['total'])
      self.budget_card.delta = budgets['delta']
      self.budget_card.good = (budgets['delta']<0) and 'positive' or 'negative'
      
    # Forecast   
    if forecasts:
      self.forecast_card.value = "${0:,.0f}".format(forecasts['total'])
      self.forecast_card.delta = forecasts['delta']
      self.forecast_card.good = (forecasts['delta']<0) and 'positive' or 'negative'

    # Actuals
    if actuals:
      self.actuals_card.value = "${0:,.0f}".format(actuals['total'])
      self.actuals_card.delta = actuals['delta']
      self.actuals_card.good = (actuals['delta']<0) and 'positive' or 'negative'


  
  def initialise_headline_cards(self):
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
    def new_card(title):
      empty = {'total': 0, 'delta': 0}
      return HeadlineStats(
              title=title, 
              value="${0:,.0f}".format(empty['total']), 
              delta=empty['delta'], 
              time_period=" vs LY", 
              good=(empty['delta']<0) and 'positive' or 'negative'
      )

    self.budget_card = new_card('Budget')
    self.forecast_card = new_card('Forecast')
    self.actuals_card = new_card('Actuals')
    
    self.flow_panel_headline_stats.add_component(self.budget_card)
    self.flow_panel_headline_stats.add_component(self.forecast_card)
    self.flow_panel_headline_stats.add_component(self.actuals_card)
    
   
  def open_transactions(self, account, **event_args):
    # This event is raised from the 'HeadlineStats' Form
    # Raise an event on the parent 'Dashboard' Form
    self.parent.raise_event('x-open-transactions', account=account)


  def details_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.details_visible = not self.details_visible
    if self.details_visible and self.loaded:
      self.tracking_table_1.prepare_data(self.raw_data)
    self.refresh_data_bindings()


  def budget_link_click(self, **event_args):
    self.budget_visible = not self.budget_visible
    if self.budget_visible and self.loaded:
      self.budget_table_1.prepare_data(self.raw_data)
    self.refresh_data_bindings()


  def action_menu_change(self, **event_args):
    """This method is called when an item is selected"""
    self.action_menu.selected_value()
    self.action_menu.selected_value = None

  def review_attributes(self):
    """This method is called when the link is clicked"""
    attribute_review_form = AttributeReview()
    attribute_review_form.show()

  def download_quarterly(self):
    """This method is called when the link is clicked"""
    obj = Data.get_quarterly_table_excel(self.fin_year)
    anvil.media.download(obj)

  def import_actuals(self):
    import_form = ImportActuals()
    (success, num_vendor_ids, num_renamed, num_actual_line_ids, num_entries) = import_form.run_import()
    if success:
      alert(f"Successful import! {num_vendor_ids} new vendors, {num_renamed} existing vendors remapped, {num_actual_line_ids} Actual Lines and {num_entries} new entries created")
      if num_vendor_ids > 0:
        self.vendors.load()
      self.reset()

  def export_excel(self):
    """This method is called when the link is clicked"""
    obj = Data.get_excel_table(self.fin_year)
    anvil.media.download(obj)
