from ._anvil_designer import AnalyseTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
#import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
import anvil.server



class Analyse(AnalyseTemplate):
  """This Form sets out the framework for capturing Settings

  """

  def __init__(self, **properties):
    print("Opening Analyse Form")
    self.init_components(**properties)
    
    self.analyse_header.set_content_form(self.analyse_content)

  
  def form_show(self, **event_args):
    pass
