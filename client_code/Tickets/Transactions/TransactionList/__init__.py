from ._anvil_designer import TransactionListTemplate
from anvil import *
#import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
from datetime import datetime
from operator import itemgetter
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server
from .... import Data

from ....Data import TransactionsModel
      
class TransactionList(TransactionListTemplate):
  """This Form is responsible for fetching transactions from the server and displaying them.
    
  It also handles transaction pagination, selecting transactions and deleting transactions.
  """
  
  def __init__(self, **properties):
    self.upload_progress.visible = False
    self.last_import_id = None
    self.selected_transactions = []
    self.filtered_transactions = []
    self.sort_values = [('Timestamp', 'timestamp'), ('Credit Account', 'credit_account'), ('Debit Account', 'debit_account')]
    self.direction_values = [('Ascending', 'ascending'), ('Descending', 'descending')]
    self.direction = 'descending'
    self.sort = 'timestamp'
    self.filters = {}
    self.date_filter = {}
    self.filter_settings = {}
    self.transactions = TransactionsModel.get_transactions()
    

    # These controls all appear / disappear as a group
    self.select_controls = [
      self.clear_selected_link,
      self.selected_label,
      self.set_debit_account_label,
      self.debit_account_dropdown,
      self.set_credit_account_label,
      self.credit_account_dropdown,
      self.duplicate_check,
      self.set_credit_account_button,
      self.delete_button
    ]
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.
    # Set event handlers on repeating_panel_1 that will be raised from the 'TransactionRow' Form
    self.repeating_panel_1.set_event_handler('x-select-ticket', self.select_transactions)
    self.repeating_panel_1.set_event_handler('x-deselect-ticket', self.deselect_transactions)
    self.repeating_panel_1.set_event_handler('x-transaction-detail', self.transaction_detail_link)

    # Default duplicate checkbox to 'indeterminate' state
    self.duplicate_check.checked = None
    
  def transaction_detail_link(self, transaction_id, **event_args):
    homepage = get_open_form()
    trans = self.transactions.get(transaction_id)
    print("Got Transaction with ID: {0}".format(transaction_id))

    #trans = anvil.server.call('get_transaction_by_id', transaction_id)
    back = {
      'open_func': homepage.open_transactions,
      'initial_filters': self.filters,
      'initial_date_filter': self.date_filter,
      'initial_page': self.transactions.get_current_page(),
      'filter_settings': self.filter_settings,
      'direction': self.direction
    }
    homepage.open_transaction(trans, back=back)
    
  def load_transactions(self, filters={}, date_filter={}, direction='descending', initial_page=0, filter_settings=None, sort='owner'):
    """Load a list of transactions from the 'Transactions' Data Table.
    
    Arguments:
      filters: dict of filters
      sort: field to sort on
      date_filter: dict of date filters
      initial_page: page to set data_grid to (if not 1)
      direction: direction to sort
    """
    
    # Initialise self.filters if 'filters' have been passed in
    self.filters = filters
    self.filter_settings = filter_settings
    self.date_filter = date_filter
    self.initial_page=initial_page
    self.direction = direction
    self.sort = sort
    
    print("Loading transaction list")
    
    page_size = self.data_grid_1.rows_per_page
    
    self.transactions.reset(  sort=self.sort,
                              filters=filters,
                              date_filter=date_filter,
                              direction=self.direction,
                              page_size=page_size,
                              initial_page=initial_page
                            )

    self.set_pages()
    
  # Change the order of transactions being displayed
  def sort_dropdown_change(self, **event_args):
    self.transactions.new_sort(self.sort)
    self.set_pages()
    #self.load_transactions(filters=self.filters, date_filter=self.date_filter, initial_page=0, filter_settings=self.filter_settings, sort=self.sort, direction=self.direction)

  def direction_dropdown_change(self, **event_args):
    self.transactions.reverse()
    self.set_pages()
    #self.load_transactions(filters=self.filters, date_filter=self.date_filter, initial_page=0, filter_settings=self.filter_settings, sort=self.sort, direction=self.direction)
    
    
  # PAGINATION CONTROLS
  def previous_page_link_click(self, **event_args):
    self.transactions.previous_page()
    self.set_pages()

  def next_page_link_click(self, **event_args):
    self.transactions.next_page()
    self.set_pages()
    
  def first_page_link_click(self, **event_args):
    self.transactions.set_page(0)
    self.set_pages()

  def last_page_link_click(self, **event_args):
    self.transactions.set_page(self.transactions.get_max_page())
    self.set_pages()
  
  # Calculating "transactions X-Y of Z"  
  def set_pages(self):
    page = self.transactions.get_current_page()
    #print(page)
    no_rows = self.transactions.get_page_size()
    first_trans = page * no_rows + 1
    last_trans = min(first_trans + no_rows - 1, len(self.transactions))
    text = f"{first_trans}-{last_trans} of {len(self.transactions)}"
    self.pagination_label.text = text
    self.filtered_transactions = self.transactions.get_page(page)
    #self.filtered_transactions = self.transactions[first_trans-1:last_trans]
    self.refresh_data_bindings()
    
  # Selecting and deselecting transactions
  def select_transactions(self, transaction, **event_args):
    self.selected_transactions.append(transaction)    
    self.update_selected_transactions()
    
  def deselect_transactions(self, transaction, **event_args):
    self.selected_transactions.remove(transaction)
    self.update_selected_transactions()
  
  def select_all_box_change(self, **event_args):
    self.selected_transactions = []
    if self.select_all_box.checked:
      self.selected_transactions += self.filtered_transactions
      for t in self.repeating_panel_1.get_components():
        t.role = "tickets-repeating-panel-selected"
        t.check_box_1.checked = True
    else:
      for t in self.repeating_panel_1.get_components():
        t.role = "tickets-repeating-panel"
        t.check_box_1.checked = False
    self.update_selected_transactions()

  def clear_selected_link_click(self, **event_args):
    self.select_all_box.checked = False
    self.select_all_box_change()
    self.duplicate_check.checked = None
    self.debit_account_dropdown.selected_value = "Leave as-is"
    self.credit_account_dropdown.selected_value = "Leave as-is"
    self.update_selected_transactions()
  
  def update_selected_transactions(self):
    """ Update the number of selected transactions and reset visibility of controls """
    if len(self.selected_transactions) == 0:
      self.selected_label.text = ""
      visible = False
    else:
      self.selected_label.text = f"{len(self.selected_transactions)} selected:"
      visible = True
    for control in self.select_controls:
      control.visible = visible

  def delete_button_click(self, **event_args):
    """This method is called when the button is clicked
      Delete all selected transactions
    """
    if confirm('Are you sure you want to delete {0} transactions?'.format(len(self.selected_transactions)), large=True):
      count = len(self.selected_transactions)
      ids = [ x.transaction_id for x in self.selected_transactions ]
      self.transactions.delete(ids)
      Notification("{0} records deleted".format(count)).show()
      self.clear_selected_link_click()
      self.transactions.clear_cache()
      page = self.transactions.get_current_page()
      self.load_transactions(filters=self.filters, date_filter=self.date_filter, initial_page=page, filter_settings=self.filter_settings, direction=self.direction)
  
  def set_credit_account_button_click(self, **event_args):
    updates = {}
    number = len(self.selected_transactions)
    changed = False
    message = 'Update {0} transactions'.format(number)
    
    credit_account_name = self.credit_account_dropdown.selected_value
    if credit_account_name != 'Leave as-is':
      message += ", setting the Credit Account to {0}".format(credit_account_name)
      updates['credit_account'] = credit_account_name
      changed = True

    debit_account_name = self.debit_account_dropdown.selected_value
    if debit_account_name != 'Leave as-is':
      message += ", setting the Credit Account to {0}".format(debit_account_name)
      updates['debit_account'] = debit_account_name
      changed = True

    set_dup = self.duplicate_check.checked
    if set_dup is not None:
      message = message + ", setting duplicate to {0}".format(set_dup)
      updates['duplicate'] = set_dup
      changed = True
    
    if changed and confirm(message, large=True):
      ids = [ x.transaction_id for x in self.selected_transactions ]
      count = self.transactions.update(ids, updates)
      Notification("{0} transactions updated successfully!".format(count)).show()
      self.clear_selected_link_click()
      page = self.transactions.get_current_page()
      self.load_transactions(filters=self.filters, date_filter=self.date_filter, initial_page=page, filter_settings=self.filter_settings, direction=self.direction)

  
  def new_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    homepage = get_open_form()
    # TODO: implement 'Back' by sending current state
    homepage.open_new_transaction_form()

  def import_button_change(self, file, **event_args):
    return
    """This method is called when a new file is loaded into this FileLoader"""
    #account_name = self.accounts_d.match_filename(file.name)
    #account_name = anvil.server.call('get_account_from_filename', file.name)
    
    if not account_name:
      alert("Could not match {0} with an account! Please check account settings!".format(file.name))
    else:
      (result, message, code) = Data.IMPORTER.start(file, account_name)
      #(result, message, code) = anvil.server.call('upload_transactions', file, account_name)
      if result != 200:
        print(result, message, code)
        alert("File preparation failed with message: {0}".format(message))
      else:
        try:
          remaining = int(message)          
          total = remaining
          cumul_count = 0
          self.upload_progress.clear_progress()
          self.new_button.visible = False
          #self.import_button.visible = False
          self.import_button.text = "Loading {0} records".format(total)
          self.upload_progress.visible = True
                  
          while remaining > 0 and result==200:
            # Use the code retrieved above to lookup each batch
            (result, count, remaining, message) = Data.IMPORTER.next_batch(code)
            #(result, count, remaining, message) = anvil.server.call('upsert_batch', code)
            print("Uploaded {0} rows".format(count))
            self.upload_progress.value = round((total - remaining) / total * 100)
            cumul_count += count
            
          if result==200:
            alert("Upload succeeded. {0} transactions added in/out of '{1}'".format(cumul_count, account_name))
            self.load_transactions(filters=self.filters, date_filter=self.date_filter, initial_page=self.initial_page, direction=self.direction, sort=self.sort)
            self.set_pages()
          else:
            alert("Upload failed with message: {0}".format(message))
        except Exception as e:
          print(e)
          alert("File preparation failed with message: {0}".format(message))
          code = ""

    #self.last_import_id = (account_name, code)
    
    self.import_button.text = "Upload"
    self.import_button.visible = True
    self.import_button.clear()
    self.upload_progress.clear_progress()
    self.upload_progress.visible = False
    self.undo_button.visible = True
    self.new_button.visible = True

  def undo_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.last_import_id is None:
      self.undo_button.visible = False
      # Should not happen but just in case!
      return
      
    account_name, import_id = self.last_import_id
    if confirm("Undo last import into {0} by deleting transactions?".format(account_name)):
      #TODO: implement - safer to set to duplicates?
      #sort='timestamp'
      filters={'account': account_name, 'import_id': import_id }
      #direction='ascending'
      #date_filter={}

      transaction_ids = [ x.transaction_id for x in self.transactions.search(filters=filters) ]
      self.transactions.delete(transaction_ids)
        
      #count = anvil.server.call('get_and_delete_transactions', sort=sort, filters=filters, date_filter=date_filter, direction=direction)
      Notification("{0} transactions deleted".format(len(transaction_ids))).show()



    










