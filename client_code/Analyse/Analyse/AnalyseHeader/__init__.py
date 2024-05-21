from ._anvil_designer import AnalyseHeaderTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
#import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server

from datetime import datetime, date
from .... import Data

class AnalyseHeader(AnalyseHeaderTemplate):
  """Header for Analyse"""

  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    print("Opening AnalyseHeader")
    self.accounts = [ ac.name for i, ac in Data.ACCOUNTS_D.items() ]
    #self.accounts = Data.ACCOUNTS_D
    self.prompt = ''
    self.selected_account = None
    self.content_form = None
    self.response_id = 0
    self.test_only = False
    
    self.test_responses = [
      "This is where a text response will go!",
      [ 
        { 'column1': 'text', 'column2': 12, 'column3': 4325, 'column4': 'whatever', 'column5': 'somehtinkg loing and lacporips', 'column6': 12.234, 'column7': 'olnltlsdf sdfsd fsd', 'column8': 4363456, 'column9': 'sdfgdsfagdsf' },
        { 'column1': 'text', 'column2': 12, 'column3': 4325, 'column4': 'whatever', 'column5': 'somehtinkg loing and lacporips', 'column6': 12.234, 'column7': 'olnltlsdf sdfsd fsd', 'column8': 4363456, 'column9': 'sdfgdsfagdsf' }
      ],
      { ('label1', 'label2'): 123, ('label1', 'label3'): 456 },
      Data.ICONS[Data.ACCOUNTS_D['ING Transaction'].icon_id].content
    ]
    
    self.init_components(**properties)
    # Any code you write here will run when the form opens.

  def set_content_form(self, content_form):
    self.content_form = content_form
    
  def go_button_click(self, **event_args):
    """This method is called when the button is clicked"""

    if not self.test_only:
      response = Data.gpt_run(prompt=self.prompt)
    else:
      response = self.test_responses[self.response_id]
      self.response_id += 1
      if self.response_id >= len(self.test_responses):
        self.response_id = 0
    
    if isinstance(response, anvil.Media):
      self.content_form.add_image_output(response)
      
    elif isinstance(response, str):
      self.content_form.add_text_output(response)
      
    elif isinstance(response, dict):
      self.content_form.add_dict_output(response)
      
    elif isinstance(response, list):
      if len(response)>0 and isinstance(response[0], dict):
        self.content_form.add_list_dict_output(response)
      elif len(response)>0:
        self.content_form.add_list_output(response)
      else:
        print("Got empty list!")
        self.content_form.add_text_output("No output!")
        
    else:
      print("Got response type: {0}".format(type(response)))
      print(str(response))
      self.content_form.add_text_output(str(response))
      
  def account_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.selected_account = self.account_dropdown.selected_value
    rows = Data.gpt_set_account_data(self.selected_account)
    self.rows_label.text = "{0} rows in selected account".format(rows)
    self.rows_label.visible = True
    self.account_image.source = Data.ACCOUNTS_D.get(self.selected_account).icon_id
    self.refresh_data_bindings()

  def prompt_box_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.prompt = self.prompt_box.text
    self.refresh_data_bindings()

  def prompt_box_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    if self.go_button.enabled:
      self.go_button_click()
    

    