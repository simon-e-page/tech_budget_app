from ._anvil_designer import AccountsTableTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
from datetime import datetime
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
from .... import Data

class AccountsTable(AccountsTableTemplate):
  def __init__(self, fin_year=None, **properties):
    # Set Form properties and Data Bindings.
    # TODO: dynamic default

    self.fin_year = self.calc_fin_year()
    self.entries = None
    self.accounts = Data.ACCOUNTS_D
    self.reconciled = self.accounts.test_reconciled()
    #self.reconciled = anvil.server.call('test_reconciled')

    self.init_components(**properties)
    # Any code you write here will run when the form opens.
    self.load_entries()

    
  def load_entries(self, refresh=False):
    if self.fin_year is not None:
      #self.entries = anvil.server.call('get_budget_entries', self.fin_year)
      self.entries = Data.get_budget_entries(self.fin_year, refresh=refresh)

  def calc_fin_year(self, date=None):
    if date is None:
      date = datetime.now()
  
    fy_date = datetime(date.year + (date.month > 7), 6, 30, 0, 0, 0)
    fy_str = 'FY{0}'.format(fy_date.strftime('%y'))
    return fy_str
    
  def get_icon(self, icon_id):
    icon = Data.get_icon(icon_id)
    return icon
    
  def build_grid(self):  
    grid = self.data_grid_1
    grid.clear()
    entries = None
    
    grid.columns = [
      { "id": "0", "title": "", "data_key": "", "width": 80 },
      { "id": "A", "title": "Type", "data_key": "type", "width": 100 },
      { "id": "B", "title": "Name", "data_key": "name", "width": 200 },
      { "id": "C", "title": "Description", "data_key": "description", "width": 350 },
      { "id": "F", "title": "Reconciled", "data_key": "reconciled", "width": 100 },
      { "id": "D", "title": "Monthly Budget", "data_key": "default_budget", "width": 80},
    ]

    if self.fin_year is not None:
      grid.columns.append( { "id": "E", "title": "{0} Budget".format(self.fin_year), "data_key": "", "width": 120 })
    
    grid.columns = grid.columns
    
    for i,r in self.accounts.items():
      row = DataRowPanel()
      #row.background = '#969A9C'
      row.spacing_above = 'none'
      row.spacing_below = 'none'
      row.row_spacing = 20
      
      image = Image(source=self.get_icon(r['icon_id']), height=50, width=50, display_mode='shrink_to_fit', horizontal_align='right')
      row.add_component(image, column='0')
      
      text = '{0}'.format(r['type'])
      textbox = Label(text=text, bold=True, foreground='black', underline=True)
      row.add_component(textbox, column='A')
      
      text = '{0}'.format(r['name'])
      link = Link(text=text, bold=False, foreground='blue')
      link.add_event_handler('click', self.open_account)
      row.add_component(link, column='B')
      
      text = '{0}'.format(r['description'])
      textbox = Label(text=text, bold=False, foreground='black', underline=False)
      row.add_component(textbox, column='C')
      
      if (r['budget']) and (r['default_budget'] is not None):
        text = '${:,.0f}'.format(r['default_budget'])
        textbox = Label(text=text, bold=False, foreground='black', underline=False, align='right')
        row.add_component(textbox, column='D')
        
        if self.fin_year:
          budget_amount = 0
          try: 
            budget_amount = self.entries.get(r['name']).amount
          except: 
            self.entries[r['name']] = Data.Entry(account_name=r['name'], amount=0)

          textbox = TextBox(type='number', placeholder=budget_amount, align='right', tag=r['name']) 
          textbox.add_event_handler('change', self.change_budget_entry)
          row.add_component(textbox, column='E')

      if r['name'] in self.reconciled:
        if self.reconciled[r['name']]:
          text = "Reconciled"
          foreground = "black"
          bold=False
          
        else:
          text = "Unreconciled"
          foreground = "red"
          bold=True
          
        textbox = Label(text=text, bold=bold, foreground=foreground, underline=False, align='left')
        row.add_component(textbox, column='F')
      
      grid.add_component(row)

  def is_fully_reconciled(self, account):
    return account.is_fully_reconciled()    
    #return anvil.server.call('is_fully_reconciled', account['name'])
    
  def open_account(self, sender=None, **args):
    print("calling open_account for {0}".format(sender.text))
    #account = anvil.server.call('get_account', sender.text)
    account = self.accounts[sender.text]
    homepage = get_open_form()
    homepage.open_account_transactions(account)
    #homepage.open_account_transactions(item=account)

  def change_budget_entry(self, sender=None, **event_args):
    print("Got change for {0}: {1}".format(sender.tag, sender.text))
    account_name = sender.tag
    try:
      self.entries[account_name].amount = float(sender.text)
    except Exception as e:
      self.entries[account_name] = Data.Entry(account_name=account_name, amount=0)
    self.parent.raise_event('x-enable-save')