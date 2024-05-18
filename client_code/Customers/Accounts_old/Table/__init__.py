from ._anvil_designer import TableTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import string


class Table(TableTemplate):
  """This Form is responsible for displaying Account data, grouped by letter of the alphabet.
  
  Keyword Arguments:
    item: accepts a list of accounts from the Accounts Data Table (a Data Tables search iterator)
          this is passed through from the 'Accounts' Form. 
          This is initialised as self.accounts in the `form_refreshing_data_bindings` method
  """
  
  def __init__(self, **properties):
    self.selected_accounts = []
    self.accounts = None
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.accounts_repeating_panel.set_event_handler('x-select-account', self.select_account)
    self.accounts_repeating_panel.set_event_handler('x-deselect-account', self.deselect_account)
    print("Accounts.Table init complete")
    
  # Selecting and Deselecting customers
  def select_all_box_change(self, **event_args):
    if self.select_all_box.checked:
      self.select_all()
    else:
      self.deselect_all()
  
  def select_account(self, account, **event_args):
    self.selected_account.append(account)
    self.clear_selected_link.visible = True
    
  def deselect_account(self, account, **event_args):
    self.selected_account.remove(account)
    if self.selected_account == []:
      self.clear_selected_link.visible = False
  
  def select_all(self):
    self.selected_account = []
    self.clear_selected_link.visible = True
    for t in self.account_repeating_panel.get_components():
      for c in t.account_repeating_panel.get_components():
        self.selected_accounts.append(c)
        c.role = "customers-repeating-panel-selected"
        c.check_box_1.checked = True

  def deselect_all(self):
    self.selected_accounts = []
    self.clear_selected_link.visible = False
    for t in self.accounts_repeating_panel.get_components():
      for c in t.accounts_repeating_panel.get_components():
        c.role = "customers-repeating-panel"
        c.check_box_1.checked = False

  def delete_account_link_click(self, **event_args):
    if self.selected_accounts:
      names = [f"{c['name']}" for c in self.selected_accounts]
      if confirm("""Are you sure you want to delete these account(s)?: \n{} 
                 \nThis will also delete all transactions associated with this account.""".format(' \n'.join(names))):
        anvil.server.call('delete_accounts', self.selected_accounts)
        Notification('Accounts deleted successfully').show()
        homepage = get_open_form()
        homepage.open_accounts()
      else:
        self.deselect_all()
    else:
      alert("No accounts selected")
      
  def form_refreshing_data_bindings(self, **event_args):
    # Populate the list of accounts in the RepeatingPanel from self.item
    # self.item is a list of accounts passed through from the 'Accounts' Form
    if self.item and self.accounts is None:
      letters = list(string.ascii_uppercase)
      self.accounts = self.item
      data = []
      for let in letters:
        accounts = [x for x in self.accounts if x['name'][0].upper() == let]
        if accounts:
          data.append({'letter': let, 'accounts':accounts})
      # Pass a dict of letters and customers to the 'LetterGroup' Form which is the ItemTemplate of customers_repeating_panel
      self.accounts_repeating_panel.items = data

  def scroll_accounts_letter_group(self, letter):
    # Scroll the appropriate LetterGroup on the customers_repeating_panel into view
    for letter_group in self.accounts_repeating_panel.get_components():
      if letter_group.item['letter'] == letter:
        letter_group.scroll_into_view()

  def clear_selected_link_click(self, **event_args):
    self.select_all_box.checked = False
    self.deselect_all()


