ircpybots
=========

IRC robots written in python

samplebot is a demo robot you can modify. It connects to a channel and responds to two type of messages:
if you mention its name, it will say hi to you.
If you start a message with “hay”, it will ask how you are, and then respond to your answer.

Storybot tells you an interactive branching story. If you don’t like it, you can say “No! D:” and change the story’s flow.
Storybot’s story management logic lives in a separate file, so you can use it to make your own non-irc based interactive stories!
say "storytime!" to start the story.

To run either robot, you should be able to just run the samplebot.py or storybot.py file using Python.
The robot will connect and join the channel that's specified in the file. It will continue printing debugging information to the console.
