from ._anvil_designer import AccountTransactionsTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
#import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
from datetime import datetime, timedelta

from .... import Data

class AccountTransactions(AccountTransactionsTemplate):
  def __init__(self, account, period=None, **properties):
    self.account = account
    self.periods = self.load_periods()
    if period:
      self.period = period
    elif len(self.periods)>0:
      self.period = self.periods[0][1]
    else:
      self.period = None
    self.all_reconciled = False

    self.TRANSACTIONS = Data.get_transactions()
    self.load_transactions()
    self.period_dropdown.selected_value = self.period

    self.build_account_plot()
    self.hide_label = {0: ('Show', 'fa:angle-down'), 1: ('Hide', 'fa:angle-up')}

    if account.type in ['EXPENSE', 'INCOME']:
      self.plot_panel.visible = True
      self.hide_link.visible = True
    else:
      self.plot_panel.visible = False
      self.plot_panel.visible = True
      
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.repeating_panel_1.set_event_handler('x-transaction-detail', self.transaction_detail_link)
    #homepage = get_open_form()
    #homepage.open_account(account)
    
  def back_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    homepage = get_open_form()
    homepage.open_accounts()
    
  def period_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.period = self.period_dropdown.selected_value
    print("Changing to new period: {0}".format(self.period))
    self.load_transactions()
    
  def reconcile_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if confirm("About to reconcile this period for {1}. Are you sure?".format(self.period_dropdown, self.account['name']), large=True):
      count = 0
      updates = { 'reconciled': True }
      # TODO: is this way too slow?
      #for t in self.transactions:
      #  t.update(updates)
      #  count += 1
      count = self.TRANSACTIONS.reconcile(self.transactions)      
      #count = anvil.server.call('reconcile_transactions', self.transactions)                  
      Notification("{0} transactions reconciled successfully!".format(count)).show()
      self.load_transactions()
                
  def transaction_detail_link(self, transaction_id, **event_args):
      homepage = get_open_form()
      trans = self.TRANSACTIONS.get(transaction_id=transaction_id)
      #trans = anvil.server.call('get_transaction_by_id', transaction_id)
      back = {
        'open_func': homepage.open_account_transactions,
        'account': self.account,
        'period': self.period,
      }
      homepage.open_transaction(trans, back=back)

  def get_dates(self, period):
    if period is not None:
      year = int(period/100)
      month = period - (year * 100)
      print("Loading transactions for period = {0}-{1}".format(year, month))
      
      start = datetime(year, month, 1, 0, 0, 0)
      
      end_year = year
      end_month = month + 1
      if end_month > 12:
        end_month = 1
        end_year += 1
        
      end = datetime(end_year, end_month, 1, 0, 0, 0)
      end = end - timedelta(days=1)
      return (start, end)
    else:
      return None, None
    
  def load_transactions(self):
    #print(end)
    start, end = self.get_dates(self.period)
    if start is None:
      self.starting_balance = 0
      self.ending_balance = 0
      self.all_reconciled = True
      self.transactions = {}
      
    else:
      sort='timestamp'
      filters={'account': self.account.name, 'duplicate': False }
      direction='ascending'
      date_filter={ 'start': start, 'end': end }
      
      transactions = self.TRANSACTIONS.search(sort=sort, filters=filters, date_filter=date_filter, direction=direction)
      #transactions = anvil.server.call('get_transactions', sort, filters=filters, date_filter=date_filter, direction=direction)
      
      #self.transactions = anvil.server.call('get_account_transactions', self.account, filters={})
      print("Got {0} transactions for {1}".format(len(transactions), self.account.name))
      
      self.starting_balance = self.account.get_balance(as_date=start - timedelta(days=1))
      #self.starting_balance = anvil.server.call('get_starting_balance', self.account.name, start - timedelta(days=1))
      #print(self.starting_balance)
      # Do this on the server along with balance calc?
      prev_balance = self.starting_balance
      all_reconciled = True
      
      for t in transactions:
        if t.debit_account == self.account.name:
          t.amount *= -1
        prev_balance += t['amount'] 
        t['balance'] = prev_balance
        all_reconciled = all_reconciled and t['reconciled']
  
      transactions.reverse()
      self.transactions = transactions
      self.ending_balance = prev_balance
      self.all_reconciled = all_reconciled
      
    self.refresh_data_bindings()
    
  
  def load_periods(self):
    return self.account.get_account_periods()
    #return anvil.server.call('get_account_periods', self.account['name'])

  def match_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    #TODO: trigger after import..?
    start, end = self.get_dates(self.period)
    count = Data.IMPORTER.process_paypal(self.account.name, start=start, end=end)
    
    #count = anvil.server.call('process_paypal', self.account['name'], start=start, end=end)
    Notification("{0} transactions updated".format(count))
    self.load_transactions()

  def build_account_plot(self):
    start_year = int(self.periods[-1][1]/100)
    start_month = self.periods[-1][1] % 100
    start = datetime(start_year - (start_month<7), 7, 1, 0, 0, 0).date()

    end_year = int(self.periods[0][1]/100)
    end_month = self.periods[0][1] % 100
    end = datetime(end_year + (end_month>=7), 6, 30, 0, 0, 0).date()

    compare_type = 'budget'
    if (self.account.type == 'ASSET' and self.account.subtype != 'Cash') or (self.account.type == 'LIABILITY' and self.account.subtype == 'Long-term'):
      compare_type = 'balance'
      
    raw = Data.ACCOUNTS_D.get_accounts_by_month(end, compare=compare_type, start=start, account_names=[self.account.name], fill=False)
    #print(raw)

    data = raw[self.account.type.lower()][0]
    #print(data)
    del data['account']

    if len(raw['compare'])>0:
      c_data = raw['compare'][0]
      #print(data)
      del c_data['account']
    else:
      c_data = None
      
    months = sorted(list(data.keys()))
    values = [ data[x] for x in months ]
    avg_value = sum(values) / len(values)

    self.account_plot.data = [
        go.Bar(
        x = months,
        y = values,
        name = 'Actuals. Average is {0:.0f}'.format(avg_value)
      )
    ]
    
    if c_data is not None:
      # applies to Accounts with Budgets set
      compare = [ c_data[x] for x in months ]
      if compare_type == 'budget':
        avg_budget = sum(compare) / len(compare)
        name = "Budget. Average is {0:.0f}".format(avg_budget)
      else:
        name = "Account Balance"
      self.account_plot.data.append(
        go.Scatter(
          x = months,
          y = compare,
          name = name
                  )      
      )
    
    self.account_plot.layout = {
      'template': 'material-light',
      'title': 'Historical Spend by Month',
      'xaxis': {
        'title': 'Month'
      },
      'yaxis': {
      'title': 'Spend / $'
      }
    }

  def hide_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.plot_panel.visible = not self.plot_panel.visible
    self.hide_link.text = self.hide_label[self.plot_panel.visible][0]
    self.hide_link.icon = self.hide_label[self.plot_panel.visible][1]

  def account_plot_click(self, points, **event_args):
    month = points[0]['x']
    month = int(month[0:8].replace('-',''))
    print("Got click for {0}".format(month))
    self.period_dropdown.selected_value = month
    self.period = month
    print("Changing to new period: {0}".format(self.period))
    self.load_transactions()
    
    