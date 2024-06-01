from ._anvil_designer import UsersTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# import anvil.google.auth, anvil.google.drive
# from anvil.google.drive import app_files
import anvil.users

# import anvil.tables as tables
# import anvil.tables.query as q
# from anvil.tables import app_tables
import anvil.server
from datetime import datetime
from ... import Data


class Users(UsersTemplate):
  """This Form displays transaction and account information for a single transaction. It also allows you to edit the transaction being displayed.

  Keyword Arguments:
    item - a row from the 'Transaction' Data Table
    back - a dictionary containg the form to open and the filters to apply when back is clicked

  A copy of this row from the 'Transaction' table is initialised as self.transaction_copy in form_refreshing_data_bindings()
  """

  def __init__(self, **properties):
    self.init_components(**properties)
