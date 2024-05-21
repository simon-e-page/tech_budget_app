"""This module is responsible for validating user inputs.

It is used to verify inputs by both client code and server code
"""

#import anvil.server
##import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
#import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables

required_transaction_keys = ['description', 'timestamp', 'amount', 'credit_account', 'debit_account']
required_account_keys = ['name', 'type', 'description']

#required_customer_keys = ['first_name', 'last_name', 'title', 'company', 'email', 'phone']
#required_ticket_keys = ['title', 'priority', 'category', 'due', 'owner']
required_transaction_settings_keys = ['description', 'timestamp', 'amount', 'credit_account', 'debit_account']
#required_message_keys = ['type', 'details']

def get_account_errors(account_dict):
  missing_keys = []
  for k in required_account_keys:
    if not account_dict.get(k, None):
      missing_keys.append(k)
  if missing_keys != []:
    return missing_keys
  else:
    return None

#def get_customer_errors(customer_dict):
#  missing_keys = []
#  for k in required_customer_keys:
#    if not customer_dict.get(k, None):
#      missing_keys.append(k)
#  if missing_keys != []:
#    return missing_keys
#  else:
#    return None
  
def get_transaction_errors(transaction_dict):
  missing_keys = []
  for k in required_transaction_keys:
    if not transaction_dict.get(k, None):
      missing_keys.append(k)
      
  # Debit account cannot be the same as Credit Account!
  if transaction_dict['debit_account'] == transaction_dict['credit_account']:
    missing_keys.append('credit_account')
    
  # Amount cannot be negative!
  if transaction_dict['amount'] < 0:
    missing_keys.append('amount')
    
  if missing_keys != []:
    return missing_keys
  else:
    return None
  
def get_transaction_settings_errors(transaction_dict):
  missing_keys = []
  for k in required_transaction_settings_keys:
     if not transaction_dict.get(k, None):
       missing_keys.append(k)
  if missing_keys != []:
    return missing_keys
  else:
    return None

#def get_message_errors(message_dict):
#  missing_keys = []
#  for k in required_message_keys:
#    if not message_dict.get(k, None):
#      missing_keys.append(k)
#  if missing_keys != []:
#    return missing_keys
#  else:
#    return None