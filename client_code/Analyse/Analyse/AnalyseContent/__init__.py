from ._anvil_designer import AnalyseContentTemplate
from anvil import *
#import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class AnalyseContent(AnalyseContentTemplate):
  """This Form is responsible for collecting user inputs for a new transaction.

  The inputs are written to self.item using Data Bindings.
  """

  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.panel_main.role = "horizontal-scroll"
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def add_text_output(self, text):
    print("Adding new text output: {0}".format(text))
    text_output = TextArea(border='thin', text=text, auto_expand=True, width=500, height=50)
    self.panel_main.add_component(text_output)

  
  def add_list_output(self, lsit_obj):
    """ Creates a single column datagrid to display the contents of list """
    print("Adding a new list object: {0}".format(list_obj))
    if len(list_obj)==0:
      self.add_text_output("No output!")
            
    grid = DataGrid(columns=[], width=column_num*200+300, rows_per_page=10, show_page_controls=True, auto_header=True, border='solid' )
    
    grid.columns.append({ "id": "0", "title": "", "data_key": "key0", "width": 200 })

    grid.columns = grid.columns
    
    for d in list_obj:
      row = DataRowPanel(border='dotted', spacing_above='none', spacing_below='none', row_spacing=20)
      text = '{0}'.format(d)
      textbox = Label(text=text, bold=False, foreground='black', underline=False)
      row.add_component(textbox, column='0')
      grid.add_component(row)
    
    self.panel_main.add_component(grid)
    
  
  def add_list_dict_output(self, list_obj):
    """ Creates a datagrid to display the contents of list[dict] """
    print("Adding a new list[dict] object: {0}".format(list_obj))
    if len(list_obj)==0:
      self.add_text_output("No output!")
      
    column_num = len(list_obj[0])
      
    grid = DataGrid(columns=[], width=column_num*200+300, rows_per_page=10, show_page_controls=True, auto_header=True, border='solid' )
    #grid = DataGrid(columns=[], width="default", rows_per_page=10, show_page_controls=True, auto_header=True, border='solid' )
    
    print("{0} columns in a dictionary".format(column_num))
    
    for k in list_obj[0].keys():
      grid.columns.append({ "id": "{0}".format(k), "title": "{0}".format(k), "data_key": "key{0}".format(k), "width": 200 })

    grid.columns = grid.columns
    
    for d in list_obj:
      row = DataRowPanel(border='dotted', spacing_above='none', spacing_below='none', row_spacing=20)
      for k,v in d.items():
        text = '{0}'.format(v)
        textbox = Label(text=text, bold=False, foreground='black', underline=False)
        row.add_component(textbox, column='{0}'.format(k))
      
      grid.add_component(row)
    
    self.panel_main.add_component(grid)


  
  def add_dict_output(self, dict_obj):
    """ Creates a datagrid to display the contents of dict[tuple, value] """
    print("Adding a new dictionary object: {0}".format(dict_obj))
    if len(dict_obj)==0:
      self.add_text_output("No output!")
    
    first_key = list(dict_obj.keys())[0]
    label_columns = len(first_key) if isinstance(first_key, tuple) else 1
      
    grid = DataGrid(columns=[], width=label_columns*200+300, rows_per_page=10, show_page_controls=True, auto_header=False, border='solid')
    
    if label_columns == 1:
      print("Only one label")
      grid.columns.append({ "id": "0", "title": "", "data_key": "key0", "width": 200 })
    else:
      print("{0} labels in a tuple".format(label_columns))
      for i in range(0, label_columns):
        grid.columns.append({ "id": "{0}".format(i), "title": "", "data_key": "key{0}".format(i), "width": 200 })

    grid.columns.append({ "id": 'data', "title": "", "data_key": "data", "width": 200 })

    grid.columns = grid.columns
    
    for k, v in dict_obj.items():
      row = DataRowPanel(border='dotted', spacing_above='none', spacing_below='none', row_spacing=20)
      #row.spacing_above = 'none'
      #row.spacing_below = 'none'
      #row.row_spacing = 20
      
      if label_columns==1:
        text = '{0}'.format(k)
        textbox = Label(text=text, bold=False, foreground='black', underline=False)
        row.add_component(textbox, column='0')
      else:
        for i in range(0, label_columns):
          text = '{0}'.format(k[i])
          textbox = Label(text=text, bold=False, foreground='black', underline=False)
          row.add_component(textbox, column='{0}'.format(i))

      text = '{0}'.format(v)
      textbox = Label(text=text, bold=False, foreground='black', underline=False)
      row.add_component(textbox, column='data')
      
      grid.add_component(row)
    
    self.panel_main.add_component(grid)



  
  def add_image_output(self, image):
    """ Creates a image_media container to display an image """
    print("Adding a new Image object")
    width, height = anvil.image.get_dimensions(image)
    new_image = Image(source=image, width=width, height=height, display_mode='zoom_to_fill')
    self.panel_main.add_component(new_image)


  
  def clear_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.panel_main.clear()





