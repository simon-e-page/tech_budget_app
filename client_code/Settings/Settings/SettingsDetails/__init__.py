from ._anvil_designer import SettingsDetailsTemplate
from anvil import *
#import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .... import Data

class SettingsDetails(SettingsDetailsTemplate):
  """This Form captures Settings by Section

    """

  def __init__(self, **properties):
    self.load_organisations()
    self.amount_items = [ "credit", "debit" ]
    self.accounts = [ ac.name for i, ac in Data.ACCOUNTS_D.items() ]
    self.checks = {}
    self.pattern_changed = False
    self.value_changed = False
    self.edit_mode = False

    self.rule_template = { 'pattern_description': '',
                            'pattern_source': None,
                            'pattern_amount': None,
                            'account_name': None,
                            'organisation': None,
                            'duplicate': None,
                            'tags': None,
                            'notes': None,
                            'status': 'current'
                          }
    
    self.item = Data.Rule(self.rule_template)
    
    self.main_form = None
    self.init_components(**properties)
    self.set_button_status()

  def set_main_form(self, main_form):
    self.main_form = main_form
    
  def set_rule(self, item=None):
    self.organisation_textbox.text = None
    self.organisation_dropdown_new.enabled = True
    
    if item is None:
      label = "Add New Rule:"
      item = Data.Rule(self.rule_template)
      self.edit_mode = False
    else:
      label = "Edit Rule:"
      self.edit_mode = True
      
    self.item = item
    self.set_button_status()
    self.refresh_data_bindings()
        
  def load_organisations(self):
    self.organisations = Data.refresh_organisations()
    self.sources = Data.refresh_sources()
    
  def form_show(self, **event_args):
    pass

  def add_button_click(self, **event_args):
    """This method is called when the Save button is clicked"""

    if not self.organisation_dropdown_new.enabled:
      self.item['organisation'] = self.organisation_textbox.text
  
    new_account = self.Import_account_dropdown.selected_value
    new_pattern = self.pattern_textbox.text

    verify_issues = []
    if new_pattern is None or len(new_pattern)==0:
      verify_issues.append("Description is required")
      
    if new_account is None or new_account == '<None>':
      verify_issues.append("Account is required")

    if self.edit_mode:
      self.item.save()
      self.main_form.build_datagrid(selected_id=self.item.id)
      Notification("Rule updated").show()
      
    elif len(verify_issues)==0:
      new_id = self.item.save()
      Data.RULES.add(new_id, self.item)
      self.main_form.change_account(self.item.account_name, selected_id=new_id)
      Notification("New Rule created").show()
      
    else:
      message = "Cannot save"
      for issue in verify_issues:
        message += ". " + issue
        
      alert(message, 'Error!')

  
  def delete_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    Data.RULES.delete(self.item.id)
    Notification("Rule deleted!").show()
    #self.main_form.get_account_rules()
    self.main_form.account_select_change()
  
  def pattern_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.pattern_changed = True
    self.set_button_status()

  def value_change(self, **event_args):
    """This method is called when an item is selected"""
    self.value_changed = True
    self.set_button_status()

  def organisation_textbox_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    if len(self.organisation_textbox.text)>0:
      self.organisation_dropdown_new.enabled = False
      self.value_change()
    else:
      self.organisation_dropdown_new.enabled = True
      self.value_change()
      

  def set_button_status(self):
    self.add_button.visible = self.item['status']=='current' and self.pattern_changed or (self.edit_mode and self.value_changed)
    self.add_button.enabled = self.add_button.visible
    self.keep_button.visible = self.item['status']=='draft' and self.edit_mode
    self.keep_button.enabled = self.keep_button.visible
    
  def keep_button_click(self, **event_args):
    """This method is called when we want to confirm a system-suggested draft rule"""
    self.item['status'] = 'current'
    self.add_button_click()

    



