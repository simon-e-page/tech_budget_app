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
    
    self.brands = Data.BRANDS_DD
    Data.CURRENT_BRAND = 'JB_AU'
    self.brand = Data.CURRENT_BRAND
    self.current_year = Data.CURRENT_YEAR
     
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.
    if anvil.users.get_user():
      self.open_dashboard()

  def set_dashboard_cache(self, value):
    self.use_dashboard_cache = value
    
  def open_dashboard(self):
    """Open the 'Dashboard' Form, by adding it to the "default" slot."""
    self.dash_panel.role = 'dash-link-selected'
    self.headline_label.text = "Dashboard"
    self.current_form = Dashboard(use_dashboard_cache=self.use_dashboard_cache)
    self.clear_page()
    self.add_component(self.current_form, slot="default")
  
  def open_transactions(self, initial_filters={}, initial_date_filter={}, initial_page=0, filter_settings={}, direction='descending'):
    """Open the 'Transactions' Form, by adding it to the "default" slot.
    
    Arguments:
      initial_filters - can be passed through to instantiate 
                        the 'Transactions' Form with filters already in place.
                        e.g initial_filters={'status': Data.OPEN} to show all unresolved Tickets.
      initial_date_filters - as with initial_filters, but for dates.
      initial_page - page of data_grid to display
      filter_settings - settings to update controls
    """
    #self.current_form = Transactions(initial_filters, initial_date_filter, initial_page=initial_page, filter_settings=filter_settings, direction=direction)
    self.current_form = BudgetLines(initial_filters=initial_filters, initial_date_filter=initial_date_filter, initial_page=initial_page, filter_settings=filter_settings, direction=direction)
    self.transaction_panel.role = 'dash-link-selected'
    self.headline_label.text = "Budget Lines"
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
    self.open_transactions()
  
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

  def link_2_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.open_settings()

  def gpt_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.open_analyse()

  def brand_image_mouse_down(self, x, y, button, keys, **event_args):
    """This method is called when a mouse button is pressed on this component"""
    self.brand_dropdown.visible = True

  def brand_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    Data.CURRENT_BRAND = self.brand_dropdown.selected_value
    self.brand = Data.CURRENT_BRAND
    self.brand_dropdown.visible = False
    self.refresh_data_bindings()

  def users_link_click(self, **event_args):
    """Open the 'Users' Form, by adding it to the "default" slot."""
    self.headline_label.text = "Users and Roles"
    #self.current_form = Accounts()
    self.current_form = Users()
    self.clear_page()
    self.add_component(self.current_form, slot="default")


      




      



      






