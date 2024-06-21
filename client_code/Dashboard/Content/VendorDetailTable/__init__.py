from ._anvil_designer import VendorDetailTableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import Data
from ....Data import VendorsModel, TransactionsModel, CURRENT_YEAR, FinancialNumber
from ....Vendors.Vendors.Vendor import Vendor


class VendorDetailTable(VendorDetailTableTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.vendors = VendorsModel.VENDORS
    self.vendor_id = properties('vendor_id')

    self.tracking_table.options = {
      "index": "transaction_id",  # or set the index property here
      "selectable": "highlight",
      "css_class": ["table-striped", "table-bordered", "table-condensed"],
      "pagination": True,
      "paginationSize": 250,
      "frozenRows": 0,
      "height": "50vh",
      #'autoResize': False,
      # "pagination_size": 10,
    }

    self.colors = {
      "Actual": {"backgroundColor": "#ffffcc", "color": "black"},
      "Forecast": {"backgroundColor": "#ccffcc", "color": "black"},
      'Budget': {"backgroundColor": "#ccffff", "color": "black"},
    }
    self.loaded = False
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def load_data(self, year):
    d = Data.get_vendor_detail(year = CURRENT_YEAR, vendor_id=self.vendor_id)
    self.year_months = d["year_months"]
    self.transaction_types = d["transaction_types"]
    self.data = d["data"]
    # self.ly_data = d['ly_data']
    # self.b_data =  d['b_data']
    self.loaded = True
    self.tracking_table_table_built()

  def tracking_table_table_built(self, **event_args):
    """This method is called when the tabulator instance has been built - it is safe to call tabulator methods"""
    if not self.loaded:
      return

    # Vendor Formatter
    def vendor_formatter(cell, **params):
      vendor_id = cell.getData()["vendor_id"]
      vendor = self.vendors.get(vendor_id)

      def open_vendor(sender, **event_args):
        print("Opening vendor: {0}".format(sender.tag.vendor_name))
        ret = alert(
          Vendor(item=sender.tag, show_save=False),
          large=True,
          title="Vendor Details",
          buttons=[("Save Changes", True), ("Cancel", False)],
        )
        if ret:
          try:
            vendor.update()
          except Exception as e:
            print("Failed to update Vendor!")
        return

      link = Link(text=cell.get_value(), tag=vendor)
      link.set_event_handler("click", open_vendor)
      return link

    # Entry formatter
    def format_entry(cell, **params):
      val = cell.getValue()
      data = cell.get_data()
      ym = params.get("year_month")
      b_ym = f"{ym}B"
      ly_ym = f"{ym}LY"

      if params.get("backgroundColor", None):
        cell.getElement().style.backgroundColor = params["backgroundColor"]
      if params.get("color", None):
        cell.getElement().style.color = params["color"]

      try:
        ly_delta = (int(val) - int(data[ly_ym])) / int(data[ly_ym])
        ly_delta = int(ly_delta * 100)
      except Exception:
        ly_delta = "INF"

      tooltip = f"LY: {FinancialNumber(data[ly_ym]):,.0f}"

      if int(val) < int(data[ly_ym]):
        icon = "fa:arrow-down"
        tooltip += f"\n{ly_delta}%"
      elif int(val) > int(data[ly_ym]):
        icon = "fa:arrow-up"
        tooltip += f"\n+{ly_delta}%"
      else:
        icon = None
        tooltip = None

      try:
        val = Label(
          text="{:,.0f}".format(FinancialNumber(val)),
          icon=icon,
          tooltip=tooltip,
          align="right",
          icon_align="left",
          foreground=params["color"],
          background=params["backgroundColor"],
        )
        # val = "{:,.0f}".format(val)
      except Exception:
        print("Entry Exception!")
        pass
      return val

    # Total formatter
    def format_total(cell, **params):
      val = cell.get_value()
      ly_total = cell.get_data()["totalLY"]

      try:
        ly_delta = (int(val) - int(ly_total)) / int(ly_total)
        ly_delta = int(ly_delta * 100)
      except Exception:
        ly_delta = "INF"

      cell.getElement().style.color = "white"
      tooltip = f"LY: {FinancialNumber(ly_total):,.0f}"

      if int(val) < int(ly_total):
        background_color = "#043d1b"
        tooltip += f"\n{ly_delta}%"
      elif int(val) > int(ly_total):
        background_color = "#4d0404"
        tooltip += f"\n+{ly_delta}%"
      else:
        background_color = "#424140"

      cell.getElement().style.backgroundColor = background_color

      try:
        val = Label(
          text="{:,.0f}".format(FinancialNumber(val)),
          bold=True,
          align="right",
          icon_align="left",
          foreground="white",
          tooltip=tooltip,
          background=background_color,
        )
        # val = "{:,.0f}".format(val)
      except Exception:
        print("Total Exception!")
        val = "NA"
      return val

    # Change formatter
    def format_percent(cell, **params):
      val = cell.get_value()

      cell.getElement().style.backgroundColor = "#0d6e12" if val <= 0 else "#6e0d15"
      cell.getElement().style.color = "white"

      try:
        if val > 0:
          val = "+{:,.0f}%".format(val)
        elif val < 0:
          val = "-{:,.0f}%".format(val)
        else:
          val = ""
      except Exception:
        print("Percent Exception!")
        val = "NA"
      return val

    columns = [
      {
        "title": "Owner",
        "field": "owner",
        "width": 100,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        "formatter": None
      },
      {
        "title": "Description",
        "field": "description",
        "width": 250,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        "formatter": transaction_formatter,        
      },
      {
        "title": "Cost centre",
        "field": "cost_centre",
        "width": 150,
        "headerFilter": "input",
        "headerFilterFunc": "starts",
        "formatter": None        
      },
      
    ]

    for c in self.year_months:
      transaction_type = self.transaction_types[c]
      columns.append(
        {
          "title": c,
          "field": c,
          "formatter": format_entry,
          "hozAlign": "right",
          "formatterParams": {
            "year_month": c,
            "backgroundColor": self.colors[transaction_type]["backgroundColor"],
            "color": self.colors[transaction_type]["color"],
          },
          "width": 85,
          "headerFilter": "number",
        }
      )

    columns.append(
      {
        "title": "Total",
        "field": "total",
        "formatter": format_total,
        "width": 100,
        "headerFilter": "number",
        "hozAlign": "right",
      }
    )

    change_col = {
      "title": "Change",
      "field": "change",
      "formatter": format_percent,
      "width": 85,
      "hozAlign": "right",
    }

    if self.mode == "last_year":
      columns.append(change_col)
      compare = self.yes_compare
      c_data = self.ly_data
    elif self.mode == "budget":
      columns.append(change_col)
      compare = self.b_compare
      c_data = self.b_data
    else:
      compare = self.no_compare
      c_data = None

    self.tracking_table.columns = columns
    # self.tracking_table.data = self.data
    self.tracking_table.data = compare(c_data)

  def yes_compare(self, c_data):
    new_data = []
    for i, row in enumerate(self.data):
      new_row = {"vendor_name": row["vendor_name"], "vendor": row["vendor"]}
      new_row["total"] = row["total"] - c_data[i]["total"]
      try:
        new_row["change"] = int(
          (row["total"] - c_data[i]["total"]) / c_data[i]["total"] * 100
        )
      except Exception as e:
        new_row["change"] = 0

      for year_month in self.year_months:
        new_row[year_month] = row[year_month] - c_data[i][year_month]
      new_data.append(new_row)
    # print(new_data)
    return new_data

  def no_compare(self, c_data):
    def zero_filter(data, **params):
      non_zero = [
        int(int(x) != 0) for i, x in dict(data).items() if i in self.year_months
      ]
      # print(f"{data['vendor_name']}: {non_zero}")
      non_zero = sum(non_zero)
      return non_zero != 0

    self.tracking_table.set_filter(zero_filter)

    
    # print(self.data)
    return self.data
