from ._anvil_designer import DetailsTemplate
from anvil import *
#import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server
from .. import Account
from .... import Data
from .... import Validation

from datetime import datetime

class Details(DetailsTemplate):
  """This Form is responsible for displaying Account Information and Recent Transactions for the Account.
  
  Keyword Arguments:
    item: accepts a row from the Accounts Data Table
          initialises this in the 'form_refreshing_data_bindings' method.
  """
  
  def __init__(self, **properties):
    self.account_transactions = None
    self.initialised = False
    self.refreshed = False
    self.task = None
    self.account_copy = {}
    self.types = Data.TYPES
    self.importers = Data.IMPORTERS
    self.subtypes = Data.SUBTYPES
    self.retrieved_balance = False
    self.icon_changed = False
    self.more = None
    print("Creating Details Form: {0}".format(id(self)))
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    
  def form_refreshing_data_bindings(self, **event_args):
    # Called from AccountDetailsOverlay to initialise the data and kick off the balance calc (async)
    # Only copy from self.item ONCE!
    print("In Details.form_refreshing_data_bindings")
    if not self.initialised and self.item:
      self.initialised = True
      self.refresh_data()

      with anvil.server.no_loading_indicator:
        self.task = self.item.get_balance()

  
  def refresh_data(self):
    """Set self.account_copy to the original account, stored in self.item"""
    #print("Details: Entering refresh_data")
    if not self.refreshed and self.item:
      print("Refreshing data from item to copy")
      self.refreshed = True
      self.account_copy = self.item.copy()   
      # These controls need alternate formatting
      self.account_copy['order_string'] = '{0}'.format(self.account_copy['order'])
      l = self.account_copy['duplicates']
      self.account_copy['duplicates_box'] = '\n'.join(l)

  def form_show(self, **event_args):
    # Disable the close button if opened from the Tickets view
    homepage = get_open_form()
    if homepage.transaction_form_open:
      self.close_pane_link.visible = False
      self.edit_account_link.visible = False
      self.more_link.visible = False

  
  def get_icon(self, icon_id):
    return Data.get_icon(icon_id)
  
  def close_pane_link_click(self, **event_args):
    homepage = get_open_form()
    homepage.close_overlay()

  
  def more_link_click(self, **event_args):
    """ This opens a new instance of this class - need to copy over any changes """
    homepage = get_open_form()
    homepage.add_account_edit_overlay(item=self.account_copy, account_copy=self.account_copy)

  def set_notes(self, notes):
    self.account_copy['notes'] = notes
    print(id(self))
    
  def edit_account_link_click(self, **event_args):
    #print(id(self))
    # Remap altered attributes back after possible editing
    l = self.account_copy['duplicates_box'].split('\n')
    self.account_copy['duplicates'] = l
    self.account_copy['order'] = int(self.account_copy.get('order_string',0))
    
    #account_submit = self.account_copy.copy()
    #account_submit.pop('duplicates_box', None)
    #account_submit.pop('order_string', None)
    
    account_validation_errors = Validation.get_account_errors(self.account_copy)
    
    if not account_validation_errors:
      name = self.account_copy['name']
      #anvil.server.call('update_account', self.item, self.account_submit)
      self.account_copy.save()
      Data.ACCOUNTS_D.add(name, self.account_copy)
      #Data.refresh_account(name)
      Notification('Account details updated').show()
      self.item = self.account_copy
      self.refresh_data()
    else:
      alert("The following mandatory fields are missing: \n{}".format(
        ' \n'.join(account_validation_errors)
      ))

  def icon_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    title = "{0}_icon_{1}.{2}".format(self.item['name'], timestamp)
    try:
      icon = Data.Icon(name=title, content=file, icon_id=None)
      Data.ICONS.add(icon.icon_id, icon)
      self.item['icon_id'] = icon.icon_id
      self.refresh_data_bindings()
    except Exception as e:    
      alert("Error uploading new icon!")
      icon = None
      self.item['icon_id'] = ''


      
  def balance_timer_tick(self, **event_args):
    """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
    with anvil.server.no_loading_indicator:
      if (self.task is not None) and (self.task.is_completed()) and (self.task.get_termination_status()=='completed') and (self.retrieved_balance==False):    
        self.balance_label.text = "${:,.2f}".format(self.task.get_return_value()).replace("$-", "-$")
        self.retrieved_balance = True
        self.balance_timer.interval=0





      
    




  


