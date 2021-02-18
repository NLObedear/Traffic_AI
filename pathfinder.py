from Map import mapofscats
from Map import splitstring
from predict import predict, setup_predict
import numpy as np
from globals import working_path, debug

frontier = []
searched = []
currentstate = ""
endstate = ""
link = {}
distances = {}
timesinmap = {}
Path = []
paths = []
Totaltimes = []
TotalDistances = []
traveltime = 0


def findpath(start, end, model, currenttime, scaler, time_data, scats_convert):
  global traveltime, distances, timesinmap, endstate
  mapofscats()
  newStates = {}
  endstate = end
  addtoFrontier(start, start, end)
  distances[start] = 0
  timesinmap[start] = 0
  # if the frontier is empty end to loop
  while len(frontier) != 0:
    # change currentstate to next in queue
    currentstate = popFrontier()
    # Check if new state is the end state
    if currentstate == endstate:
      if debug:
        print("Path Found")
      # if it is get whole path and add time to a list of times for result
      path = getwholepath(currentstate, start)
      Totaltimes.append(timesinmap[currentstate])
      TotalDistances.append(distances[currentstate])
      if debug:
        print(path)
      # Deletes the link endstate to its parent
      link.pop(end)
      # yields path to whatever called this function
      yield path
    else:
      # if state isnt the end explore new states
      newStates = explore(currentstate)
      # finds the distance and time for all new states.
      for i in range(len(newStates)):
        addtodistance(newStates[i], currentstate, model, currenttime, scaler, time_data, scats_convert)
      # Orders new states and adds them to the frontier
      newStates = orderchildren(newStates)
      for i in range(len(newStates)):
        addtoFrontier(newStates[i], currentstate, end)


#finds up to 5 paths
def fivepaths(start, end, modele, currenttime):
  global Totaltimes, TotalDistances
  model, scaler, time_data, scats_convert = setup_predict(modele)
  i = 0
  # runs findpath 5 times
  for sol in findpath(start, end, model, currenttime, scaler, time_data, scats_convert):
    paths.append(sol)
    if i == 5:
        break
    i += 1
  return paths, Totaltimes


#takes a node out of the frontier and adds it into the searched states
def popFrontier():
  global endstate
  currentstate1 = frontier.pop(0)
  if currentstate1 != endstate:
    searched.append(currentstate1)
  return currentstate1

#adds children nodes to the frontier
def addtoFrontier(state, currentstate, end):
  if (state in searched) or (state in frontier):
    return False
  else:
    # add to the queue to be searched
    if state == end:
      frontier.insert(0, state)
    else:
      frontier.append(state)

    # add to the link dictionary to find path back
    if state != currentstate:
      link[state] = currentstate
    return True


# adds distances to a map to calculate travel from start
def addtodistance(state, currentstate, model, currenttime, scaler, time_data, scats_convert):
  global traveltime, timesinmap
  time = 0
  if (state in searched) or (state in frontier):
    return False
  else:
    nodes = mapofscats.intersections[currentstate]
    for x in nodes:
      split = splitstring(x)
      if state == split[1]:
        # finds the distance and time using the parent node
        add = distances[currentstate] + int(split[2])
        time = predict(int(currentstate), currenttime, int(split[2]), model, scaler, time_data, scats_convert)
        traveltime = timesinmap[currentstate] + time
        distances[state] = add
        timesinmap[state] = traveltime
       #print('Path: ', currentstate, ' to ', state, ' Time: ', time, ' Distance: ', int(split[2]))
    return True

# Explores new nodes from a parent node
def explore(state):
  newstates = []
  # puts the current states links in a variable
  nodes = mapofscats.intersections[state]
  # Grabs the names of all the linked states
  for x in nodes:
    split = splitstring(x)
    newstates.append(split[1])
  return newstates

# Returns the whole path from end node to start node
def getwholepath(state, start):
  current = state
  pathto = []
  found = False
  pathto.append(state)
  while not found:
    # When current = start we are back at beginning
    if current == start:
      found == True
      # reverses path since it is backwards
      pathto.reverse()
      return pathto
    else:
      # Travels through the map using parent/child link
      pathto.append(link[current])
      current = link[current]

# Orders the children nodes by travel time
def orderchildren(list):
  global timesinmap
  # sorts an input list of Scats sites from smallest to largest
  # Based on their estimated travel time from start node
  for i in range(len(list)):
    for j in range(len(list)):
      if timesinmap[list[j]] > timesinmap[list[i]]:
        list[j], list[i] = list[i], list[j]
  return list

