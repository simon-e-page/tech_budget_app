from ._anvil_designer import AccountTemplate
from anvil import *
#import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .... import Validation


class Account(AccountTemplate):
  """This Form is responsible for linking a account to the transaction being created on the 'Details' Form. 
  
  It either creates a new account, or selects an existing account.
  Keyword Arguments:
    item (optional): a row from the 'Accounts' Data Table
  If initialised with an 'item' argument, this is initialised as self.selected_account in the form_show method.
  """
  
  def __init__(self, **properties):
    self.new = True
    self.new_account = {}
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Get customers from the server
    self.accounts = anvil.server.call('get_accounts')
    self.repeating_panel_results.items = []
    # Set up an event handler - this is called when a customer is selected in CustomerSearchRow
    self.repeating_panel_results.set_event_handler('x-result-selected', self.set_result)

  def new_account_button_click(self, **event_args):
    self.new = True
    self.repeating_panel_results.items = []
    self.text_box_search.text = ""
    self.new_account_box.visible = True

  def text_box_search_focus(self, **event_args):
    # Refresh the keys when the search box is selected, and populate the suggestions panel.
    self.text_box_search.text = ""
    self.selected_customer = {}
    self.new = False
    self.new_account_box.visible = False
    self.populate_results(self.text_box_search.text)
  
  def text_box_search_change(self, **event_args):
    # Populate the suggestions when text is entered.
    self.populate_results(self.text_box_search.text)

  def text_box_search_pressed_enter(self, **event_args):
    # Choose the top result when enter is pressed.
    results = self.repeating_panel_results.get_components()
    if results:
      results[0].link_search_result.raise_event('click')

  def populate_results(self, text):
    # Populate the suggestions panel.
    if text == '':
      self.repeating_panel_results.items = []
    else:
      # Populate the results list
      self.repeating_panel_results.items = [
        c for c in self.accounts
        if text.lower() in c['name'].lower()
        or text.lower() in c['description'].lower()
        or text.lower() in f"{c['name'].lower()} {c['description'].lower()}"
      ]

  def set_result(self, result, **event_args):
    self.selected_account = result
    self.refresh_data_bindings()
    self.text_box_search.text = f"{result['name']}"
    self.repeating_panel_results.items = []
    
  def add_transaction(self, transaction, details):
    if self.new:
      account = self.new_account
      account_validation_errors = Validation.get_account_errors(account)
    else:
      account = self.selected_account
      account_validation_errors = None
      if account == {}:
        alert("Please choose an account")
        return
    trans_validation_errors = Validation.get_transaction_errors(transaction)
    if not account_validation_errors and not trans_validation_errors:
      transaction = anvil.server.call('add_transaction', transaction, details, account)
      Notification('Ticket Added').show()
      homepage = get_open_form()
      homepage.open_transaction(item=transaction)
    elif account_validation_errors and trans_validation_errors:
      alert("The following fields are missing for your account: \n{}.\n\nThe following field are missing for your transaction: \n{}".format(
        ' \n'.join(word.capitalize() for word in account_validation_errors),
        ' \n'.join(word.capitalize() for word in trans_validation_errors)
      ))
    elif trans_validation_errors and not account_validation_errors:
      alert("The following transaction fields are missing: \n{}".format(' \n'.join(word.capitalize() for word in trans_validation_errors)))
    elif account_validation_errors and not trans_validation_errors:
      alert("The following account fields are missing: \n{}".format(' \n'.join(word.capitalize() for word in account_validation_errors)))

  def form_show(self, **event_args):
    if self.item:
      self.new = False
      self.selected_account = self.item
      self.text_box_search.text = f"{self.selected_account['name']}"


