from ._anvil_designer import DashboardTemplate
from anvil import *
##import anvil.google.auth, anvil.google.drive
##from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server
from datetime import datetime, timedelta, date
from .. import Data

from ..Data import VendorsModel
from ..Tickets.BudgetLines.ImportActuals import ImportActuals
from .Content.AttributeReview import AttributeReview

class Dashboard(DashboardTemplate):
  """This Form fetches the information required to populate the Dashboard from the server.
  
  It send this information to the 'Content' Form to populate the charts and cards.
  """
  
  def __init__(self, use_dashboard_cache=True, **properties):
    # Initialise a dict of empty filters when the dashboard loads
    self.filters = {}
    self.vendors = VendorsModel.VENDORS
    # Initialise a dict of empty date filters when the dashboard loads
    self.date_filters = {}
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.set_event_handler('x-open-transactions', self.open_transactions)
    
    
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
    return
    """Fetch the data required to populate the 'Dashboard' from the server.
    
    Send it to the 'Content' Form to populate the appropriate labels and charts
    """
    
    
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


  def unused_vendors_link_click(self, **event_args):
    """This method is called when the button is clicked"""
    unused_vendors = self.vendors.get_unused()
    if len(unused_vendors)>0:
      unused_list = "\n".join(unused_vendors)
      textbox = TextArea(text=unused_list, auto_expand=True)
      message = Label(text=f"There are {len(unused_vendors)} vendors that are unused (no transaction lines, no entries) and can be deleted:")
      message2 = Label(text="Proceed?")
      panel = LinearPanel()
      panel.add_component(message)
      panel.add_component(textbox)
      panel.add_component(message2)
      ret = alert(panel, 'Delete unused vendors?', buttons=[('Yes', True), ('Cancel', False)] )
      if ret:
        count = self.vendors.delete(unused_vendors)
        Notification(message=f"{count} vendors deleted successfully!").show()
    else:
      Notification(message="There are no vendors that are unused!").show()
      

  def export_all_link_click(self, **event_args):
    """This method is called when the button is clicked"""
    obj = Data.get_excel_table(self.dash_content.fin_year)
    anvil.media.download(obj)

  def refresh_link_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.dash_content.reset()

  def import_link_click(self, **event_args):
    import_form = ImportActuals()
    (success, num_vendor_ids, num_renamed, num_actual_line_ids, num_entries) = import_form.run_import()
    if success:
      alert(f"Successful import! {num_vendor_ids} new vendors, {num_renamed} existing vendors remapped, {num_actual_line_ids} Actual Lines and {num_entries} new entries created")
      self.refresh_link_click()
    else:
      alert("Failed import?")

  def quarterly_download_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    obj = Data.get_quarterly_table_excel(self.dash_content.fin_year)
    anvil.media.download(obj)

  def align_references_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    attribute_review_form = AttributeReview()
    attribute_review_form.show()



 
  