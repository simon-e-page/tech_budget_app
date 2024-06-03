import anvil.server
import anvil.users

from ..Data import AttributeToDict, AttributeToKey, ACCEPTABLE_IMAGES

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from .Data import Module1
#
#    Module1.say_hello()
#


#####################################################################
#  ICON
#####################################################################


class Icon(AttributeToKey):
  
  def __init__(self, icon_id, content):
    try:
      # Max file size of 100kB (note not Kibibytes to be technical!)
      if content.length > 100000:
        print("Selected file is too large. Please reduce and try again!")
      elif (content.content_type in ACCEPTABLE_IMAGES.keys()):
        self.icon_id = icon_id
        self.content = content
      else:
        print('Not an acceptable image file. Please try again!')
    except Exception as e:    
      print("Error adding new icon!")
        
    if not icon_id:
      print("Could not create new Icon")
      return

  def save(self):
    #try:
    anvil.server.call('Vendors', 'add_icon', self.icon_id, self.content)
    #except Exception as e:
    #  print("Error uploading icon!")
      

class Icons(AttributeToDict):
  def __init__(self):
    self.__d__ = {}

  def length(self):
    return len(self.__d__)

  def load_all(self):
    icons_cache = anvil.server.call('Vendors', 'get_icons')
    for k, v in icons_cache.items():
      self.add(k, Icon(icon_id=k, content=v))

  def load(self, icon_id):
    try:
      content = anvil.server.call('Vendors', 'get_icon', icon_id)
      icon = Icon(icon_id=icon_id, content=content)
      self.add(icon_id, icon)
    except Exception as e:
      print(f"Could not find icon_id: {icon_id}!")
      icon = None
      
    return icon

  def get_content(self, icon_id):
    try:
      content = self.get(icon_id, self.load(icon_id)).content
    except Exception as e:
      content = None
    return content

#############################
# MAIN
############################

ICONS = Icons()
