#!/usr/local/bin/python

# import things:
import socket
import ssl
import time
import re
import sys
from random import randrange

import storytime

### IRC stuff ###


# irc-related constants
server = "irc.arcti.ca" # server and port to connect to
port = 6697
channel = "#GIR"
botnick = "storybot" #bot's name
password = "" # no password needed

# make stuff that lets you talk to IRC
irc_C = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
irc = ssl.wrap_socket(irc_C)


def connectAndLoop():
# Connect to the irc channel and go into an infinite loop waiting for input and processing it.

  # irc.setblocking(False)  # sets socket as non-blocking (other things can use it, I guess) but breaks... something so not using it.
  print "Establishing connection to [%s]" % (server)
  # Connect
  irc.connect((server, port))
  
  # send info about yourself to the server
  # irc.send("PASS %s\n" % (password))  # not bothering with passwords
  irc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :testbot\n")
  irc.send("NICK "+ botnick +"\n")
  irc.send("PRIVMSG nickserv :iNOOPE\r\n")    #auth
  irc.send("JOIN "+ channel +"\n")

  while True:  # TODO: have a boolean variable 
    #time.sleep(2)  # this would wait 2 seconds before waiting for the next input each time, but it's a bit silly to do that. 

    try:
      text=irc.recv(2040) # wait for the next bit of input from the IRC server. Limit to 2040 characters.
      # (the rest would stay in the buffer and get processed afterwards, I think)
      print text # print it to your local console for debugging purposes

      # Prevent Timeout - this is how the IRC servers know to kick you off for inactivity, when your client doesn't PONG to a PING.
      if text.find('PING') != -1: # if there is a "PING" anywhere in the text
        irc.send('PONG ' + text.split() [1] + '\r\n') # send PONG - this doesn't actually show up in chat.
      
      processInput(text) # actually process the input

    except Exception as e:
      # this is just in case something within the 'try' block throws an exception.
      # not sure what would do that. might be unnecessary.
      print sys.exc_info()
      print str(e)
      continue # don't crash on exception; keep going


### Helper functions for processing input ###


def sendMsg(line):
  # send message to irc channel
  irc.send('PRIVMSG '+channel+' :'+line+' \r\n')

  
def getName(line):
  # assumes format :[name]!blahblah
  return line[1:line.find('!')] 

  
def getMsg(line):
  # returns the contents of a message to the channel
  # The format of a message is "PRIVMSG #channel :[message]"
  # If line doesn't fit that format, then just return empty string (wasn't a message)
  m = line.split('PRIVMSG '+channel+' :')
  if len(m)>1:
    return m[1]
  else:
    return ""
  
  
# TODO: get nth word?
  
  
def getFirstWord(line):
  # returns the first word of a message to the channel.
  # assumes line is a full message, returns first word of the actual content
  msg = getMsg(line)
  return msg.split()[0]
  
  
def getFirstWordAndRest(line):
  # Returns the first word and the rest of the message.
  return getMsg(line).split(None,1)


### Conversation-related variables and functions ###


awaitingResponses = {}


def awaitResponse(userName, question, callbackFunction):
  # for when a bot wants to ask a specific user a question, and do something when the user responds.
  sendMsg(userName + ", "+ question)
  awaitingResponses[userName] = callbackFunction # store (under the user's name) what you have to do when they answer.
  

def processResponse(text):
  # check whether this answers one of my questions. If it does, do whatever I was supposed to do when it's answered.
  userName = getName(text)
  message = getMsg(text)
  if userName in awaitingResponses: # if we are waiting for this user to respond
    callbackFunction = awaitingResponses[userName]
    awaitingResponses.pop(userName) # take them off awaitingResponses
    callbackFunction(userName, message.strip()) # do whatever you're supposed to do when they answer


# example callback function:
def parrotBack(userName, message):
  sendMsg("I am also " + message + "!")


### Parameters and functions for the story ###


storyPlaying = False  # whether we are currently in the middle of playing a story. TODO: keep within story?
storyPaused = False  # whether we paused the story to make changes to it
prevRoom = None  # TODO: keep within story?
prevPath = None  # TODO: keep within story?
newRoomName = None  # a new room that's being made by a player


def changePath(userName, newroom):
  # change the path from prevRoom through prevPath to lead to roomname
  global newRoomName, storyPaused
  storytime.addPath(prevRoom, newroom, prevPath, True)
  if not newroom in storytime.rooms:
    newRoomName = newroom
    awaitResponse(userName, newroom + " doesn't exist yet! what do you want its description to be?", makeRoom)
  else:
    storytime.currentRoom = newroom
    # TODO: consolidate logic for 'if at end room, game over' in one place.
    # TODO: also consolidate 'unpause game'?
    sendMsg(storytime.getCurrentDesc())
    storyPaused = False # unpause story
    

def makeRoom(userName, newdesc):
  global storyPaused
  storytime.addRoom(newRoomName, newdesc)
  storytime.currentRoom = newRoomName
  sendMsg(storytime.getCurrentDesc())
  storyPaused = False


### Function for reacting to input ###
  

def processInput(text):
  # process a line of text from the IRC server.
  # Sometimes it's a chat message someone sent to the channel; sometimes it's some administrative IRC info.

  # try to get contents of a message.
  # these functions will return emtpy strings if the text wasn't actually a message to the channel.
  firstAndRest = getFirstWordAndRest(text)
  userName = getName(text)
  message = getMsg(text).strip()
  print message
  
  # initialize helper variables for responding to message:
  firstWord = ""
  restOfText = ""
  
  if len(firstAndRest) > 0:  # must have found a message to the channel
    firstWord = firstAndRest[0]
    
    if len(firstAndRest) > 1: # there is more than one word in the message
      restOfText = firstAndRest[1].strip()

  # check whether the message is a response to a question:
  processResponse(text)
  
  
  global storyPlaying, storyPaused, prevPath, prevRoom
  # respond to message as needed:
  if message == "storytime!":
    if storyPlaying:
      sendMsg("But we are already in a story!")
    else:
      storyPlaying = True
      storytime.reset()
      sendMsg("OK, storytime!")
      sendMsg("Start your message with '>' if it's an instruction for the story.")
      sendMsg(storytime.getCurrentDesc())
      
  elif storyPlaying and message.startswith(">"): # story directions need to start with a special character
    path = message[1:].strip()
    room = storytime.currentRoom
    if path == "look":
      sendMsg(storytime.getCurrentDesc())
    elif storyPaused:
      sendMsg("Shh, we\'re waiting on a story change")
    else:
      # save previous room/path for editing:
      prevRoom = room
      prevPath = path
      if storytime.takePath(path): # try to take the indicated path
        # if you took the path:
        sendMsg(storytime.getCurrentDesc())
        # check if we need to go back:
        if storytime.currentRoom in ['DEATH', 'WIN']:
          storyPlaying = False
      else:
        # if that fails:
        sendMsg("Sorry, I don't know how to "+path)
        
  elif message == "No! D:":
    if prevPath and prevRoom:
      storyPaused = True
      awaitResponse(userName, 'OK, where do you go instead when you go '+prevPath+' from '+prevRoom+'?', changePath)
    else:
      sendMsg("We didn't go anywhere yet!")
      
  elif botnick in message:
    sendMsg("Hello "+userName+"!!")
  
  elif firstWord == 'hay':
    awaitResponse(userName, 'hay :V how are you?', parrotBack)
  
  else: # If the message doesn't match something you can respond to
    pass # do nothing


### Start running the loop ###


connectAndLoop()