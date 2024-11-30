from ._anvil_designer import HomepageTemplate
from anvil import *
import anvil.users
import anvil.server
import plotly.graph_objs as go

#from ..Tickets.Transactions import Transactions
from ..Tickets.Transaction import Transaction
from ..Dashboard import Dashboard
from ..Analyse.Analyse import Analyse
from ..Users.Users import Users
from ..Vendors.Vendors import Vendors
from ..Tickets.BudgetLines import BudgetLines
from ..Settings.Reference import Reference
from .NewBrand import NewBrand
from ..Tickets.BudgetLines.ImportBudget import ImportBudget 
from ..Payroll.Payroll import Payroll
from .. import Data


class Homepage(HomepageTemplate):
  """This Form controls navigation for the whole app.
  
  It has two "slots" that accept Anvil components, named 'default', and 'overlay'.
  Navigation works by loading Forms into this Form's "default" slot.
  
  The "overlay" slot is used by certain Forms to 'overlay' themselves
  on top of the content currently displayed in the "default" slot on the Hompage. 
  """

  def __init__(self, **properties):
    # Is the 'Ticket' Form currently open? - set default to False
    self.transaction_form_open = False
    # Is the 'Customers' Form currently open? - set default to False
    self.vendors_form_open = False
    self.analyse_form_open = False
    #self.last_import_id = ('', '')
    self.use_dashboard_cache = True
    
    Data.record_login()
    
    self.brands = Data.BRANDS_DD + [('Add New..', 'ADD')]
    #Data.CURRENT_BRAND = 'JB_AU'
    self.brand = Data.CURRENT_BRAND
    self.current_year = Data.CURRENT_YEAR
    self.budget_year = Data.BUDGET_YEAR
     
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.
    if anvil.users.get_user():
      self.open_dashboard()

  def set_dashboard_cache(self, value):
    self.use_dashboard_cache = value

  def get_icon(self, brand):
    return Data.get_brand_icon(brand)

  def open_dashboard(self):
    """Open the 'Dashboard' Form, by adding it to the "default" slot."""
    self.dash_panel.role = 'dash-link-selected'
    self.headline_label.text = "Dashboard"
    self.current_form = Dashboard(use_dashboard_cache=self.use_dashboard_cache)
    self.clear_page()
    self.add_component(self.current_form, slot="default")

  def open_actuals(self, initial_filters={}, initial_date_filter={}, initial_page=0, filter_settings={}, direction='descending', **kwargs):
    self.current_form = BudgetLines(mode='Actual',  initial_filters=initial_filters, year=Data.get_year())
    self.transaction_panel.role = 'dash-link-selected'
    self.headline_label.text = f"Actual Lines: {self.current_year}"
    self.clear_page()
    self.add_component(self.current_form, slot="default")
  
  def open_budgets(self, initial_filters={}, initial_date_filter={}, initial_page=0, filter_settings={}, direction='descending', **kwargs):
    self.current_form = BudgetLines(mode='Budget', initial_filters=initial_filters, year=Data.get_year())
    self.transaction_panel.role = 'dash-link-selected'
    self.headline_label.text = f"Budget Lines: {self.current_year}"
    self.clear_page()
    self.add_component(self.current_form, slot="default")

  def open_forecasts(self, initial_filters={}, initial_date_filter={}, initial_page=0, filter_settings={}, direction='descending', **kwargs):
    self.current_form = BudgetLines(mode='Forecast', initial_filters=initial_filters, year=Data.get_year())
    self.transaction_panel.role = 'dash-link-selected'
    self.headline_label.text = f"Forecast Lines: {self.current_year}"
    self.clear_page()
    self.add_component(self.current_form, slot="default")

  def open_payroll(self, **kwargs):
    self.current_form = Payroll()
    #self.transaction_panel.role = 'dash-link-selected'
    self.headline_label.text = f"Payroll: {self.current_year}"
    self.clear_page()
    self.add_component(self.current_form, slot="default")
  
  def open_transaction(self, item, back=None):
    """Open the 'Transaction' Form, by adding it to the "default" slot.

    Argments:
      item - a row from the 'Transactions' Data Table
      back - a dict with the form to open and filters to set if the user selects the Back button
    """
    print("In open_transaction")
    if self.transaction_form_open:
      print("form is already open")
      # If the current view is the 'Transaction' Form, only refresh items that need refreshing
      self.current_form.transaction_copy = item.copy()
      self.current_form.item = item
      #print(self.current_form.transactions_copy.items())
    else:
      print("opening form")
      self.transaction_panel.role = 'dash-link-selected'
      self.headline_label.text = "Transaction"
      self.current_form = Transaction(item=item, back=back)
      self.clear_page()
      self.add_component(self.current_form, slot="default")
      self.transaction_form_open = True
      print("opened form")
  
    
  def open_vendors(self):
    """Open the 'Vendors' Form, by adding it to the "default" slot."""
    self.vendors_form_open = True
    self.vendor_panel.role = 'dash-link-selected'
    self.headline_label.text = "Vendors"
    #self.current_form = Accounts()
    self.current_form = Vendors()
    self.clear_page()
    self.add_component(self.current_form, slot="default")
    print("open_vendors complete")



  def open_analyse(self):
    """ Open the settings form """
    if self.analyse_form_open:
      pass
    else:
      self.headline_label.text = "Analyse with GPT"
      self.current_form = Analyse()
      self.clear_page()
      self.add_component(self.current_form, slot="default")
  
  
  
  
  def dash_link_click(self, **event_args):
    # Open the dashboard when the dash_link is clicked
    self.open_dashboard()
    
  def transaction_link_click(self, **event_args):
    # Open the transactions  when the transaction_link is clicked
    self.open_budgets()
  
  def vendor_link_click(self, **event_args):
    # Open the accounts view when the account_link is clicked
    self.open_vendors()

  def new_transaction_button_click(self, **event_args):
    # Open the NewTransaction Form when the new_transaction_button is clicked
    self.open_new_transaction_form()

  def clear_page(self):
    self.transaction_form_open = False
    self.accounts_form_open = False
    # Clear both slots
    self.clear(slot="overlay")
    self.clear(slot="default")
    # Reset links in the links_panel so they are not highlighted
    #for panel in self.links_panel.get_components():
    #  panel.role = "dash-link"
      
  def close_overlay(self):
    """Clear the 'Overlay' slot."""
    self.clear(slot="overlay")
    
  def signout_link_click(self, **event_args):
    anvil.users.logout()
    open_form('Login')

  def form_show(self, **event_args):
    if anvil.users.get_user() is None:
      open_form('Login')

  def reference_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.open_settings()

  def open_settings(self):
    ref = Reference()
    alert(ref, title="Manage Reference Attributes", large=True)
    
  def gpt_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.open_analyse()

  def brand_image_mouse_down(self, x, y, button, keys, **event_args):
    """This method is called when a mouse button is pressed on this component"""
    self.brand_dropdown.visible = True

  def brand_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.brand_dropdown.selected_value == "ADD":
      new_brand_form = NewBrand(item={'code': None, 'name': None, 'icon_file': None })
      action = alert(new_brand_form, title="Create new Brand:", large=True, buttons=[ ('Create', True), ('Cancel', False) ])
      if action:
        result = new_brand_form.create_brand()
        if result:
          self.brand_dropdown.selected_value = result
          Data.refresh(brand=result)
        else:
          self.brand_dropdown.selected_value = self.brand
          self.brand_dropdown.visible = False
          return          
    else:
      Data.refresh(brand=self.brand_dropdown.selected_value)
      self.brand = Data.CURRENT_BRAND
      self.current_year = Data.CURRENT_YEAR
      
    self.brand_dropdown.visible = False
    self.refresh_data_bindings()
    self.open_dashboard()

  def users_link_click(self, **event_args):
    """Open the 'Users' Form, by adding it to the "default" slot."""
    self.headline_label.text = "Users and Roles"
    #self.current_form = Accounts()
    self.current_form = Users()
    self.clear_page()
    self.add_component(self.current_form, slot="default")

  def link_1_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.open_actuals()

  def forecast_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.open_forecasts()

  def prev_button_click(self, **event_args):
    """This method is called when the link is clicked"""
    Data.move_year(diff=-1)
    self.current_year = Data.CURRENT_YEAR
    self.refresh_data_bindings()
    self.open_dashboard()

  def next_button_click(self, **event_args):
    """This method is called when the link is clicked"""
    result = Data.move_year()
    if result:
      self.current_year = Data.CURRENT_YEAR
      self.refresh_data_bindings()    
      self.open_dashboard()
    else:
      next_year = Data.CURRENT_YEAR + 1
      if confirm(f"No data for {next_year}. Do you want to create a Budget now?"):
        form = ImportBudget(year=next_year)
        result = form.show(next_year)
        if result:
          Data.refresh(brand=self.brand)
          self.next_button_click()

  def payroll_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.open_payroll()

      




      



      






