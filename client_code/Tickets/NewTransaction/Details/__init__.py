from ._anvil_designer import DetailsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import datetime as dt
from .... import Data
from .... import Validation


class Details(DetailsTemplate):
  """This Form is responsible for collecting user inputs for a new transaction.
  
  The inputs are written to self.item using Data Bindings.
  """
  
  def __init__(self, **properties):
    print("Entering NewTransaction.Details")
    self.accounts = Data.ACCOUNTS_D.get_dropdown()
    self.accounts_d = Data.ACCOUNTS_D
    #self.load_organisations()
    self.organisations = Data.refresh_organisations()
    self.details = None
    #print(self.organisations)
    # Set Form properties and Data Bindings.
    
    self.item = Data.Transaction(transaction_json={})
    # Default transaction date to the last day of the prior month (most common use case)
    self.item['timestamp'] = self.last_day_of_previous_month()
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def last_day_of_previous_month(self):
      today = dt.date.today()
      first_day_of_this_month = today.replace(day=1)
      last_day_of_previous_month = first_day_of_this_month - dt.timedelta(days=1)
      return last_day_of_previous_month
  
  def save_transaction_button_click(self, **event_args):
    # This calls the 'add_transaction' method on the 'Accounts' Form
    self.add_transaction(transaction=self.item, details=self.details)
    
  def cancel_button_click(self, **event_args):
    homepage = get_open_form()
    homepage.open_transactions()

  def add_transaction(self, transaction, details):
    trans_validation_errors = Validation.get_transaction_errors(transaction)
    if not trans_validation_errors:
      if transaction.organisation is None:
        if len(self.organisation_textbox.text)>0:
          transaction.organisation = self.organisation_textbox.text
        else:
          transaction.organisation = ''
      transaction.source = "Manual entry"
      transaction.reconciled = False

      #try:
      new_trans = Data.TRANSACTIONS.new(transaction)
      #except Exception as e:
      #  print("Caught exception: {0}".format(e))
      #  new_trans = None
      
      if new_trans is None:
        alert("Error adding transaction!")
      else:
        Notification('New transaction added successfully').show()
        #print(dict(transaction))
        homepage = get_open_form()
        homepage.open_transaction(item=new_trans)
    else:
      alert("The following transaction fields are missing or incorrect: \n{}".format(' \n'.join(word.capitalize() for word in trans_validation_errors)))

  def new_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.item['organisation'] = self.organisation_textbox.text

 
  def load_organisations(self):
    self.organisations = Data.refresh_organisations()

  def get_icon(self, account_name):
    if account_name is not None:
      return Data.get_icon(self.accounts_d[account_name]['icon_id'])

  def select_debit_account_change(self, **event_args):
    """This method is called when an item is selected"""
    self.refresh_data_bindings()

  def select_credit_account_change(self, **event_args):
    """This method is called when an item is selected"""
    self.refresh_data_bindings()

  def description_box_lost_focus(self, **event_args):
    """This method is called when the TextBox loses focus"""
    desc = self.item['description']
    account_name = self.item['debit_account']
    if account_name is None:
      account_name = 'Unknown'
    if desc is not None and len(desc)>0:
      print("Looking for a match for description: {0}".format(desc))
      rule = Data.RULES.match(self.item)
      #organisation = Data.ORGANISATIONS.match(description=desc, account_name=account_name)
      #organisation = anvil.server.call('match_organisation', description=desc, account_name=account_name)
      if rule is not None and rule.status != 'draft':
        for attr in ['organisation', 'duplicate', 'tags', 'notes']:
          if rule[attr] is not None:
            self.item[attr] = rule[attr]
        self.refresh_data_bindings()

  def organisation_textbox_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    if len(self.organisation_textbox.text)>0:
      self.organisation_dropdown.enabled = False
    else:
      self.organisation_dropdown.enabled = True

    




