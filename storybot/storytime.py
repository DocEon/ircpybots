# TODO: enable keeping track of several stories by making this a class.

# A room is a specific place you can be in the story, like a forest or a room in a dungeon.
# it can also be used to represent a state of being, not just a physical location.
# We start out with a few "special" rooms that will be used to start and end the game.
rooms = {'START':   ['It is very dark. You are likely to be eaten by a grue.', {'torch':'WIN', 'north':'DEATH'}],
         'DEATH':   ['You have died! better luck next time.', {}],
         'WIN':     ['You win! Congratulations', {}]}

# we list the special room names so we know when we hit them later.
specialNames = ['START', 'DEATH', 'WIN']

currentRoom = 'START' # start at the beginning!

prevRoom = None  # previous room, if any
prevPath = None  # previous path, if any

playing = False  #Whether we are currently in the middle of playing a game 

def reset():
  # reset the game by moving back to the start.
  global currentRoom, prevRoom, prevPath, playing
  currentRoom = 'START'
  prevRoom = None
  prevPath = None
  playing = True


def stop():
  global playing
  playing  = False


def roomExists(name):
  return (name in rooms)
  

def pathExists(roomName, pathText):
  paths = rooms[roomName][1]  # paths from this room
  return (pathText in paths)


def addRoom(name, description):
  # add room with a given name and description. Return False if room already exists.
  if name in rooms:
    return False
  else:
    rooms[name] = [description, {}]
    return True


def changeDesc(roomName, newDesc):
  # tries to change the description of a given room
  if not roomName in rooms:
    return False
  else:
    rooms[roomName][0] = newDesc
    return True

  
def addPath(fromRoom, toRoom, inputText, forceChange = False):
  # add a path (connection) from one room to the next.
  # inputText is what the player has to type in to take that connection.
  # note that paths are one-way!
  
  # TODO: verify that fromRoom exists
  fromPaths = rooms[fromRoom][1]  # fromPaths is the dictionary of connections from a given room.
  if inputText in fromPaths and not forceChange:
    return False  # if that path is already there, and we aren't supposed to force a change, don't change it. Return False.
  else:
    fromPaths[inputText] = toRoom  # TODO: check that 'to' exists already?
  
  
def getCurrentDesc():
  # returns the description of the current room that should be printed out.
  # if current room doesn't actually exist, returns none.
  global currentRoom
  if currentRoom in rooms:
    desc = rooms[currentRoom][0]
    if not currentRoom in specialNames:
      desc = currentRoom+": "+desc
    return desc
  else:
    return None

def goToRoom(roomName):
  # go to a specific room; handle room logic like ending the game.
  # TODO: move room existence check here?
  global currentRoom
  currentRoom = roomName
  if currentRoom in ['WIN','DEATH']:
    stop()
  
def takePath(inputText):
  # Change current room based on the input text, by matching it to one of the paths out of the room.
  # Return True if took path successfully, False otherwise.
  # TODO: special case somewhere for trying to take existing path to non-existing room.
  global currentRoom, prevPath, prevRoom
  # record previous path and room regardless of whether the attempt to move succeeded
  prevPath = inputText
  prevRoom = currentRoom
  # try to move
  if currentRoom in rooms:
    paths = rooms[currentRoom][1]  # paths from this room
    if inputText in paths:
      goToRoom( paths[inputText] )
      return True
    else:
      return False  # no such path
  else:
    return False  # no such room (current room does not exist)
