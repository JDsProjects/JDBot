class Minecraft:
  __slots__ = ("name", "uuid", "history")
  def __init__(self, data):
    self.name = data.get("username")
    self.uuid = data.get("uuid")
    self.history = data.get("name_history")

  @property
  def formatted_history(self):
    d = self.history
    
    formatted = ""
    for x in d:
        formatted += f"{x['changedToAt'].replace('Origanal', 'Original')} >> {x['name']}\n"
            
    return formatted
  
  @property
  def reversed_formatted_history(self):
    d = self.history
    
    formatted = ""
    for x in d[::-1]:
        formatted += f"{x['changedToAt'].replace('Origanal', 'Original')} >> {x['name']}\n"
            
    return formatted