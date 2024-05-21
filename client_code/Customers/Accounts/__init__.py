from ._anvil_designer import AccountsTemplate
from anvil import *
import anvil.server
#import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
#from .AccountsTable import AccountsTable
from ... import Data

class Accounts(AccountsTemplate):
  def __init__(self, **properties):
    self.fin_year = None
    self.fin_years= Data.FIN_YEARS
    self.accounts = Data.ACCOUNTS_D
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.fin_year_dropdown.selected_value = max( [ x[0] for x in self.fin_years ] )
    self.fin_year = self.fin_year_dropdown.selected_value
    self.accounts_table.load_entries()
    self.accounts_table.build_grid()
    self.save_button.enabled = False
    self.refresh_data_bindings()
    self.set_event_handler('x-enable-save', self.enable_save)

  def fin_year_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.fin_year = self.fin_year_dropdown.selected_value
    print(self.fin_year)
    self.accounts_table.fin_year = self.fin_year
    self.accounts_table.load_entries()
    self.accounts_table.build_grid()
    self.save_button.enabled = True
    self.refresh_data_bindings()

  def save_button_click(self, **event_args):
    """This method is called when the Save button is clicked"""
    print("Saving budget for {0}".format(self.fin_year))
    count = 0
    print(self.accounts_table.entries)
    self.accounts_table.entries.save()
    #anvil.server.call('save_budget_entries', fin_year=self.fin_year, entries=self.accounts_table.entries)
    count = len(self.accounts_table.entries)

    Notification("{0} new or altered budget entries saved for {1}".format(count, self.fin_year))
    #self.accounts_table.load_entries(refresh=True)
    self.save_button.enabled = False
    homepage = get_open_form()
    homepage.set_dashboard_cache(False)

  def default_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    print("Setting defaults for {0}".format(self.fin_year))
    if confirm("This will set all budgets for this financial year to the defaults. Are you sure?", large=True):
      count = 0
      for i,v in self.accounts.items():
        if v['budget'] and (v['default_budget'] is not None):
          self.accounts_table.entries[i] = Data.Entry(account_name=i, amount=v['default_budget'])
          #anvil.server.call('save_budget_entry', self.fin_year, i, v['default_budget'])
          count += 1
      #self.accounts_table.entries.save()
      Notification("{0} default budget entries saved for {1}".format(count, self.fin_year)).show()
      #self.accounts_table.load_entries()
      self.accounts_table.build_grid()
      self.save_button.enabled = True
      self.refresh_data_bindings()

  def enable_save(self, **event_args):
    self.save_button.enabled = True

  def new_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    homepage = get_open_form()
    homepage.open_new_account()

      



    
