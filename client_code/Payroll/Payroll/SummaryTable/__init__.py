from ._anvil_designer import SummaryTableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ....Data import PositionsModel, EmployeesModel
from ....Data.BaseModel import FinancialNumber
from .... import Data

COLORS={
  'actual': '#ffffcc',
  'forecast': '#ccffcc',
  'total': 'white'
}

class SummaryTable(SummaryTableTemplate):
  def __init__(self, **properties):
    self.positions = PositionsModel.POSITIONS
    self.employees = EmployeesModel.EMPLOYEES
    self.year = Data.CURRENT_YEAR
    self.brand = Data.CURRENT_BRAND

    self.data = None
    year_months_keys = [ (self.year - (x>6))* 100 + x for x in [ 7,8,9,10,11,12,1,2,3,4,5,6 ]  ]
    self.year_months = { k: 'forecast' for k in year_months_keys }
    #self.year_months = [ (self.year - (x>6))* 100 + x for x in [ 7,8,9,10,11,12,1,2,3,4,5,6 ]  ]
    
    self.summary_table.options = {
      "index": "position_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      'pagination': True,
      'paginationSize': 5,
      'frozenRows': 1
    }
    # Set Form properties and Data Bindings.
    self.get_data()
    self.init_components(**properties)

  
  def get_data(self):
    self.data = self.employees.get_annual_summary(brand=self.brand, year=self.year)
    # TODO: identify Actual columns, create total row, create total column

    actuals_map = { ym: False for ym in self.year_months.keys() }
    
    for row in self.data:
      actuals_map = { ym: current or (row[str(ym)]['actual'] != 0) for ym, current in actuals_map.items() }
      row_total = sum(row[str(ym)][cost_type] for ym, cost_type in self.year_months.items())
      prior_total = sum(row[str(ym)]['prior_year_actual'] for ym in self.year_months.keys())
      row['total'] = { 'total': row_total, 'prior_year_actual': prior_total }

    self.year_months = { ym: actuals_map[ym] and 'actual' or 'forecast' for ym in self.year_months.keys() }
    totals_map = { str(ym): 0 for ym in self.year_months.keys() }
    py_totals_map = { str(ym): 0 for ym in self.year_months.keys() }
    for row in self.data:
      totals_map = { str(ym): totals_map[str(ym)] + row[str(ym)][cost_type] for ym, cost_type in self.year_months.items()}      
      py_totals_map = { str(ym): py_totals_map[str(ym)] + row[str(ym)]['prior_year_actual'] for ym in self.year_months.keys()}
      
    total_row = { str(ym): { 'total': totals_map[str(ym)], 'prior_year_actual': py_totals_map[str(ym)], 'cost_type': 'total' } for ym in self.year_months.keys() }
    grand_total =  sum(total_row[str(ym)]['total'] for ym in self.year_months.keys())
    prior_grand_total =  sum(total_row[str(ym)]['prior_year_actual'] for ym in self.year_months.keys())
    total_row['team'] = 'Total'
    total_row['total'] = { 'total': grand_total, 'prior_year_actual': prior_grand_total }
    self.data = [total_row] + self.data
  
  def prepare_summary_table(self):
    def cy_formatter(cell, **params):
      values = cell.get_value()
      data = cell.get_data()
      cost_type = params.get('cost_type', 'forecast')
      cost_type = (data['team'] == 'Total') and 'total' or cost_type
      bold = (cost_type == 'total')
      amount = values[cost_type]

      cell.getElement().style.backgroundColor = COLORS[cost_type]  
      obj = Label(text=FinancialNumber(amount), bold=bold)
      return obj

    def ly_formatter(cell, **params):
      data = cell.get_data()
      cost_type = params.get('cost_type', 'forecast')
      cost_type = (data['team'] == 'Total') and 'total' or cost_type
      year_month = params.get('year_month')
      values = data[year_month]
      bold = (cost_type == 'total')
      amount = values[cost_type]
      prior_amount = values['prior_year_actual']
      if prior_amount != 0:
        percent = (amount - prior_amount) / prior_amount * 100
        display = f"{percent:,.1f}%"
      else:
        display = 'NA' 
        
      #cell.getElement().style.backgroundColor = COLORS[cost_type]  
      obj = Label(text=display, bold=bold, tooltip=FinancialNumber(prior_amount))
      return obj

    def team_formatter(cell, **params):
      val = cell.get_value()
      bold = (val=='Total')
      obj = Label(text=val, bold=bold)
      return obj
      
    columns = [
      {
        'title': 'Team',
        'field': 'team',
        'width': 250,
        'formatter': team_formatter,
        'headerSort': False
      },
      
    ]


    for year_month, cost_type in self.year_months.items():
      month_cols = [ {
          'title': str(year_month),
          'field': str(year_month),
          'width': 70,
          'formatter': cy_formatter,
          'formatterParams': { 'cost_type': cost_type },
          'headerSort': False
        }, {
          'title': 'LY',
          'field': '',
          'width': 50,
          'formatter': ly_formatter,
          'formatterParams': { 'cost_type': cost_type, 'year_month': str(year_month) },
          'headerSort': False
        } ]
    
      columns += month_cols

    total_cols = [{
          'title': 'Total',
          'field': 'total',
          'width': 70,
          'formatter': cy_formatter,
          'formatterParams': { 'cost_type': 'total' },
          'headerSort': False

    },{
          'title': 'LY',
          'field': '',
          'width': 50,
          'formatter': ly_formatter,
          'formatterParams': { 'year_month': 'total', 'cost_type': 'total' },
          'headerSort': False
    }]            
    columns += total_cols
    
    self.summary_table.columns = columns
    self.summary_table.data = self.data

    def zero_filter(data, **params):
      d = dict(data)
      actuals = abs(d['total']['total']) > 1
      prior_actuals =  abs(d['total']['prior_year_actual']) > 1
      return (actuals or prior_actuals)

    self.summary_table.set_filter(zero_filter)
    # Any code you write here will run before the form opens.

  def summary_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    self.prepare_summary_table()

    