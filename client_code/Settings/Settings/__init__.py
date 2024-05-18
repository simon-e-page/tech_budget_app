from ._anvil_designer import SettingsTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server


class Settings(SettingsTemplate):
  """This Form sets out the framework for capturing Settings

  """

  def __init__(self, **properties):
    print("Opening Settings Form")
    self.init_components(**properties)
    self.settings_main.set_details_form(self.settings_details)
    self.settings_details.set_main_form(self.settings_main)
    
    #self.settings_details.set_rule()

  def form_show(self, **event_args):
    #self.initialise_dashboard_data()
    pass
