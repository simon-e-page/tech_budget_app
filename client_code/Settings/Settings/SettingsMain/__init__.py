from ._anvil_designer import SettingsMainTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .... import Data

class SettingsMain(SettingsMainTemplate):
  """This Form captures Settings by Section

    """

  def __init__(self, fin_year_date=None, **properties):
    print("Opening settings main content form")
    self.selected_name = None
    self.selected_patterns = {}
    self.existing_visible = True
    self.accounts_with_rules = self.get_sources()
    self.import_functions = ['upload_ING', 'upload_CBA', 'upload_paypal']
    self.checks = {}

    self.details_form = None
    self.search_mode = 'account'
    #self.item = {}
    
    self.init_components(**properties)
    self.header_column_panel.visible = True
    self.content_column_panel.visible = True
    
  def form_show(self, **event_args):
    pass

  def get_sources(self):
    return Data.RULES.get_sources()
    
  def set_details_form(self, details_form):
    self.details_form = details_form
    
  def get_account_rules(self, account_name):
    # TODO: handle 'None'?
    return Data.RULES.search(pattern_source=account_name)

  def get_draft_rules(self):
    return Data.RULES.search(status='draft')
    
  def change_account(self, account_name, selected_id=None):
    """ This is called to auto-select a specific account and rule """
    self.account_select.selected_value = account_name
    self.selected_name = account_name
    self.search_mode = 'account'
    self.build_datagrid(selected_id=selected_id, search='account')
    
  def account_select_change(self, **event_args):
    """This method is called when an account is selected by the user. Builds table with all rules associated with the account """
    self.search_mode = 'account'
    self.details_form.set_rule()
    self.build_datagrid()


  def build_datagrid(self, search=None, selected_id=None):
    """ Build and display the datagrid with the patterns for the selected Organisation """      
    if search is None:
      search = self.search_mode
    
    self.checks = {}
    grid = self.rules_datagrid
    grid.clear()
    entries = None
    
    grid.columns = [
      { "id": "0", "title": "", "data_key": "select", "width": 50 },
      { "id": "A", "title": "Description", "data_key": "pattern_description", "width": 200 },
      { "id": "B", "title": "Source", "data_key": "pattern_source", "width": 200 },      
      { "id": "C", "title": "Amount", "data_key": "pattern_amount", "width": 200 },      
      { "id": "D", "title": "Status", "data_key": "status", "width": 200 }      
    ]
    
    if search != 'account':
      grid.columns.append({ "id": "E", "title": "Account Name", "data_key": "account_name", "width": 200 })
    
    grid.columns = grid.columns
    if search == 'account':
      account_rows = self.get_account_rules(self.selected_name)
    else:
      account_rows = self.get_draft_rules()

    if len(account_rows) > 0:
      for rule in account_rows:
        rule_id = rule.id
        row = DataRowPanel()
        row.spacing_above = 'none'
        row.spacing_below = 'none'
        row.row_spacing = 20

        checked = (rule_id == selected_id)
        checkbox = CheckBox(checked=checked, enabled=True, text='', align='left', tag=rule_id)
        checkbox.add_event_handler('change', self.change_selected_entry)
        row.add_component(checkbox, column='0')
        
        text = '{0}'.format(rule.pattern_description)
        textbox = Label(text=text, bold=False, foreground='black', underline=False)
        row.add_component(textbox, column='A')

        source = rule.pattern_source
        if source is None:
          textbox = Label(text="Any", bold=False, foreground='grey', underline=False, italic=True)
        else:
          text = '{0}'.format(source)
          textbox = Label(text=text, bold=False, foreground='black', underline=False)
        row.add_component(textbox, column='B')

        amount = rule.pattern_amount
        if amount is None:
          textbox = Label(text='Any', bold=False, foreground='grey', underline=False, italic=True)
        else:
          text = '{0}'.format(rule['pattern_amount'])
          textbox = Label(text=text, bold=False, foreground='black', underline=False)
        row.add_component(textbox, column='C')

        status = rule.status
        if status == 'draft':
          textbox = Label(text="Import Suggested", bold=False, foreground='grey', underline=False, italic=True)
        else:
          text = ''
          textbox = Label(text=text, bold=False, foreground='black', underline=False)
        row.add_component(textbox, column='D')

        if search != 'account':
          account_name = rule.account_name
          textbox = Label(text=account_name, bold=False, foreground='black', underline=False, italic=False)
          row.add_component(textbox, column='E')
        grid.add_component(row)
        
      grid.visible = True
    else:
      grid.visible = False

    if selected_id is not None:
      self.details_form.set_rule(Data.RULES.get(selected_id))

  def clear_senders(self, keep_tag=None):
    """ Clear all checkboxes except the one now selected """
    for tag, sender in self.checks.items():
      if tag != keep_tag:
        sender.checked = False
  
  def change_selected_entry(self, sender=None, **event_args):
    print("Got change for {0}: {1}".format(sender.tag, sender.checked))
    self.checks[sender.tag] = sender
    
    if sender.checked:
      self.clear_senders(sender.tag)
      self.details_form.set_rule(Data.RULES.get(sender.tag))
    else:
      self.details_form.set_rule()

  def rescan_button_click(self, **event_args):
    """This method is called when the button is clicked"""
#    if confirm("This will rescan all transactions to match Organisations. Are you sure?"):
#      count = anvil.server.call('rescan_organisations')
#      Notification("{0} transactions updated successfully".format(count)).show()

  def existing_fold_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.existing_visible = not self.existing_visible
    self.refresh_data_bindings()
    self.existing_fold.icon = 'fa:angle-right' if self.existing_fold.icon == 'fa:angle-down' else 'fa:angle-down'

  def draft_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.details_form.set_rule()
    self.account_select.selected_value = None
    self.search_mode = 'draft'
    self.build_datagrid(search='draft')


 



      




