from ._anvil_designer import TransactionsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server
from ... import Data
from datetime import date, datetime, time, timezone


class Transactions(TransactionsTemplate):
  """This Form is responsible for passing user-defined filters to the 'TransactionList' Form.
  
  The filtering logic is collected from user inputs and sent to the 'TransactionList' Form to be processed. 
  """
  
  def __init__(self, initial_filters=None, initial_date_filter=None, initial_page=0, filter_settings=None, direction='descending', **properties):
    """Collect filters, and send them to the TransactionList Form to retrieve a list of transaction.
    
    Arguments: 
      initial_filters (optional): dict of filters on the transaction view
      initial_date_filters (optional): dict of date filters on the transaction view
    """
    self.filter_settings = filter_settings or {}
    self.direction = direction
    self.filters = initial_filters or { 'duplicate': False }
    self.date_filter = initial_date_filter or {}
    self.initial_page = initial_page
    self.current_import_ids = []
    self.load_organisations()
    
    if (isinstance(self.filters, dict) and len(self.filters)>0):
      #print(self.filters)
      self.set_filter_settings()
    elif isinstance(self.filters, dict):
      pass
    else:
      #print(self.filters)
      self.set_filter_settings()

    if (isinstance(self.date_filter, dict) and len(self.date_filter)>0):
      self.set_date_filter_settings()
    elif isinstance(self.date_filter, dict) or self.date_filter is None:
      pass
    else:
      self.set_date_filter_settings()
      
    self.accounts = Data.ACCOUNTS_D.get_dropdown()
    self.init_components(**properties)
    self.load_transactions()
    # Any code you write here will run when the form opens.

  def load_organisations(self):
    orgs = Data.ORGANISATIONS
    #orgs = list(anvil.server.call('get_organisation_map').keys())
    orgs.sort()
    self.organisations = ['<Blank>'] + orgs
    
  def load_transactions(self, **event_args):
    # If the filters are changed, de-select any currently selected transaction. This is done on the 'TransactionList' Form
    # Why is this set up as an event? Does it need to be?
    self.transaction_list.clear_selected_link_click()
    self.transaction_list.load_transactions(filters=self.filters, date_filter=self.date_filter, initial_page=self.initial_page, filter_settings=self.filter_settings, direction=self.direction)

  def set_filter_settings(self):
    #print(self.filter_settings)
    account_name = self.filter_settings.get('account', None)
    if account_name is not None:
      self.account_dropdown.selected_value = self.filter_settings.get('account', None)
      # Does this get called automatically?
      #self.account_dropdown_change()
    self.description_text.text = self.filter_settings.get('description', None)
    self.duplicate_check.checked = not self.filter_settings.get('duplicate', False)
    org = self.filter_settings.get('organisation', None)
    if org is not None:
      if len(org)==0:
        self.organisation_dropdown.selected_value = '<Blank>'
      else:
        self.organisation_dropdown.selected_value = org

  def set_date_filter_settings(self):
    if isinstance(self.date_filter['end'], datetime):
      self.date_filter['end'] = self.date_filter['end'].date()
      self.date_filter['start'] = self.date_filter['start'].date()
    
  
  def clear_filters_link_click(self, **event_args):
    self.filters = { 'duplicate': False}
    self.date_filter = {}
    self.account_dropdown.selected_value = 'all'
    self.description_text.text = ''
    self.duplicate_check.checked = True
    #self.end_date_picker.date = None
    #self.end_date_picker.date = None
    
    self.refresh_data_bindings()
    #self.transaction_list.sort_dropdown.selected_value = 'Timestamp (descending)'
    self.load_transactions()

  def description_text_change(self, **event_args):
    """ Do we need to validate the text input?"""
    pass
    
  def apply_button_click(self, **event_args):
    """This method is called when an filter is changed.
       Logic is:
        Filter 1: A match on either the credit_account or the debit_account field
        Filter 2: A case-insensitive match on the description field and removal of duplicates (if checked)
    """
    filter1 = {}
    filter2 = {}
    filter3 = {}
    filter_settings = {}
    
    account = self.account_dropdown.selected_value
    if account is not None and account != 'all':
      print("Setting account filter to {0}".format(account))
      filter3['account'] = account
      filter_settings['account'] = account
    else:
      filter_settings.pop('account', '')
      
    description = self.description_text.text
    if description is not None and len(description)>0:
      print("Setting description filter to {0}".format(description))
      filter3['description'] = description
      filter_settings['description'] = description
    else:
      filter_settings.pop('description', '')

    organisation = self.organisation_dropdown.selected_value
    if (organisation is not None) and (organisation != 'All'):
      if organisation == '<Blank>':
        print("Setting organisation filter to <Blank>")
        filter3['organisation'] = ""
        filter_settings['organisation'] = ""
      else:
        print("Setting organisation filter to {0}".format(organisation))
        filter3['organisation'] = organisation
        filter_settings['organisation'] = organisation
    else:
      filter_settings.pop('organisation', '')
      
    if self.duplicate_check.checked:
      print("Setting duplicate filter")
      #filter2['duplicate'] = False
      filter3['duplicate'] = False
      filter_settings['duplicate'] = True
    else:
      filter_settings['duplicate'] = False
      filter3.pop('duplicate', None)

    if (self.import_dropdown.selected_value is not None) and (self.import_dropdown.selected_value != 'All'):
      print('Setting import filter')
      filter3['import_id'] = self.import_dropdown.selected_value
      filter_settings['import_id'] = self.import_dropdown.selected_value
      
    self.filters = filter3
    self.filter_settings = filter_settings
    self.initial_page = 0
    self.load_transactions()

  def start_date_dropdown_change(self, **event_args):
    """This method is called when the selected date changes"""
    start_time = datetime.combine(self.start_date_picker.date, time(0,0), tzinfo=timezone.utc)
    #start_time = start_time.replace(tzinfo=None)
    self.date_filter['start'] = start_time.date()

  def end_date_dropdown_change(self, **event_args):
    """This method is called when the selected date changes"""
    end_time = datetime.combine(self.end_date_picker.date, time(0,0), tzinfo=timezone.utc)
    #end_time = end_time.replace(tzinfo=None)
    self.date_filter['end'] = end_time.date()

  def account_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    account_name = self.account_dropdown.selected_value
    if account_name != 'all':
      import_ids = Data.IMPORTER.get_import_ids(account_name)
      #import_ids = anvil.server.call_s('get_import_ids', account_name)
      print("Found import_ids for {0}:{1}".format(account_name, import_ids))
      self.current_import_ids = import_ids
      self.refresh_data_bindings()







