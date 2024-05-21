from ._anvil_designer import LoginTemplate
from anvil import *
import anvil.server
##import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
##

class Login(LoginTemplate):
  """This is the Startup Form of the app. 
  
  It either prompts users to log in 
  or redirects them to the 'Homepage' Form if they are already logged in.
  """
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def login_button_click(self, **event_args):
    if anvil.users.login_with_form():
      open_form('Homepage')

  def demo_login_button_click(self, **event_args):
    pass
  #  user = anvil.server.call('login_demo_user')
  #  if user:
  #    open_form('Homepage')

  def form_show(self, **event_args):
    if anvil.users.get_user():
      open_form('Homepage')



