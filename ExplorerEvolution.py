import sys
import random
import math
import os
with open(os.devnull, 'w') as f: #This disables stdout when importing pygame to fix an issue where it repeatedly outputs a welcome message.
                                 #This is likely the result of multi-threading, but further investigation is needed.
    # disable stdout
    oldstdout = sys.stdout
    sys.stdout = f

    import pygame

    # enable stdout
    sys.stdout = oldstdout

import ctypes
from fractions import Fraction
from collections import Counter
import threading
import multiprocessing
import time

fitnessQueue = multiprocessing.Queue() #Creates a queue accessible to all threads 


class StateMachine:
    "A state machine representing the behavioral pattern of an individual"
    def __init__(self, statesDict):
        "Constructor"
        self.statesDict = statesDict #Dictionary with states keyed to their IDs
        self.removedStateIds = [] #List of IDs that have become available
        self.currentState = 0 #The current state of the machine
        self.highestId = len(statesDict)-1 #The highest identifier in use or in the removedStateIds list
        
    def getNewId(self):
        "Returns a unique identifier not in use in this StateMachine"
        if len(self.removedStateIds) > 0:
            return self.removedStateIds.pop(0)
        return len(self.statesDict)
    
    def removeState(self, identifier):
        "Removes the State with the given identifier, unless the identifier equals 0"
        if identifier != 0: #Cannot remove the starting state
            self.removedStateIds.append(identifier)
            self.statesDict.pop(identifier)
            if self.highestId == identifier:
                self.highestId -= 1
            
    def removeCurrentState(self):
        "Removes the current State, as long as it's not the zero State"
        self.removeState(self.currentState)
        
    def nextState(self):
        "Transitions the current State to its next State and returns that State. If next State doesn't exist, transitions to zero State. If the State's hit count reaches its breakAfter point, transitions to break State."
        current_state = self.statesDict.get(self.currentState)
        if current_state == None:
            raise RuntimeError("Current state does not exist. Current state: " + str(self.currentState))
        current_state.hitCount += 1
        breakAfter = current_state.breakAfter
        stateBroken = breakAfter > -1 and breakAfter <= current_state.hitCount
        if stateBroken:
            current_state.hitCount = 0
        self.currentState = current_state.nextState if not stateBroken else current_state.breakState
        if self.currentState in self.statesDict.keys():
            return self.statesDict.get(self.currentState)
        self.currentState = 0
        return self.statesDict.get(self.currentState)
    
    def blockedState(self):
        "Transitions the current State to its blocked State and returns that State. If blocked State doesn't exist, transitions to and returns zero State. If the State's hit count reaches its breakAfter point, transitions to break State."
        current_state = self.statesDict.get(self.currentState)
        if current_state == None:
            raise RuntimeError("Current state does not exist. Current state: " + str(self.currentState))
        current_state.hitCount += 1
        breakAfter = current_state.breakAfter
        stateBroken = breakAfter > -1 and breakAfter <= current_state.hitCount
        if stateBroken:
            current_state.hitCount = 0
        self.currentState = current_state.blockedState if not stateBroken else current_state.breakState
        if self.currentState in self.statesDict.keys():
            return self.statesDict.get(self.currentState)
        self.currentState = 0
        return self.statesDict.get(self.currentState)
    
    def replaceOrAddState(self, newState):
        "Adds the newState to the StateMachine if the State's identifier is unique, otherwise replaces the State with the same identifier"
        if newState.identifier in self.removedStateIds:
            self.removedStateIds.remove(newState.identifier)
        if newState.identifier > self.highestId:
            for i in range(self.highestId, newState.identifier):
                self.removedStateIds.append(i)
            self.highestId = newState.identifier
        self.statesDict[newState.identifier] = newState
        
    def purgeIslands(self):
        "Removes all unreachable States"
        stateHitCounter = {}
        for key in self.statesDict.keys():
            stateHitCounter[key] = 0
        self.recursiveGroom(stateHitCounter, 0)
        for state, hits in stateHitCounter.items():
            if hits == 0:
                self.statesDict.pop(state)
                
    def recursiveGroom(self, stateHitCounter, stateId):
        "Modifies the given stateHitCounter dictionary (containing State identifiers as keys paired with a value of 0) to add 1 to all values for reachable States"
        if stateId in stateHitCounter.keys():
            if stateHitCounter.get(stateId) < 1:
                stateHitCounter[stateId] += 1
                self.recursiveGroom(stateHitCounter, self.statesDict.get(stateId).nextState)
                self.recursiveGroom(stateHitCounter, self.statesDict.get(stateId).blockedState)
                self.recursiveGroom(stateHitCounter, self.statesDict.get(stateId).breakState)
                
    def getNextValue(self):
        "Transitions the current State to its next State and returns the value of that State"
        return self.nextState().value
    
    def getBlockedValue(self):
        "Transitions the current State to its blocked State and returns the value of that State"
        return self.blockedState().value
    
    def getCurrentValue(self):
        "Returns the value of the current State or the value of the zero State if the current State doesn't exist"
        if self.currentState in self.statesDict.keys():
            return self.statesDict.get(self.currentState).value
        self.currentState = 0
        return self.statesDict.get(self.currentState).value
    
    def toString(self):
        "Returns a string representation of this StateMachine"
        string = "{"
        for key in self.statesDict.keys():
            string = string + self.statesDict.get(key).toString() + ", "
        return string + "}"
    
    def copyMachine(self):
        "Constructs and returns a copy of this StateMachine"
        newStateDict = {}
        for ident, state in self.statesDict.items():
            newStateDict[ident] = state.copyState()
        newMachine = StateMachine(newStateDict)
        newMachine.removedStateIds = list(self.removedStateIds)
        return newMachine
    
    def resetStates(self):
        "Sets the hit count of all States to 0"
        for ident, state in self.statesDict.items():
            state.hitCount = 0
            
    def __eq__(self, other):
        "Overrides the default 'equals' implementation"
        if isinstance(other, StateMachine):
            return self.statesDict == other.statesDict
        return False
    
    def __hash__(self):
        "Overrides the default 'hash' implementation"
        return hash(self.statesDict.values())


class State:
    "A state in a state machine"
    values = 8 #Valid state values are 1 through 8
    valueDictionary = {1:'up', 2:'up-right', 3:'right', 4:'down-right', 5:'down', 6:'down-left', 7:'left', 8:'up-left'} #value meanings
    
    def __init__(self, nextState, blockedState, breakState, breakAfter, value, identifier):
        "Constructor"
        self.nextState = nextState #The ID of the next State in the graph
        self.blockedState = blockedState #The ID of next State if the previous direction value was blocked
        self.value = value #The value of this State. Represents the direction of movement.
        self.identifier = identifier #A unique ID for this State (unique within the StateMachine, not universally)
        self.breakState = breakState #The ID of the next State if the breakAfter point is reached
        self.breakAfter = breakAfter #The number of times the State can be hit before transitioning to the breakState
        self.hitCount = 0 #The number of times this State has been hit
        
    def __eq__(self, other):
        "Overrides the default 'equals' implementation"
        if isinstance(other, State):
            return self.nextState == other.nextState and self.blockedState == other.blockedState and self.breakState == other.breakState and self.breakAfter == other.breakAfter and self.value == other.value and self.identifier == other.identifier
        return False
    
    def __hash__(self):
        "Overrides the default 'hash' implementation. Bases hash off of nextState, blockedState, breakState, breakAfter, value, and identifier"
        return hash((self.nextState, self.blockedState, self.breakState, self.breakAfter, self.value, self.identifier))
    
    def toString(self):
        "Returns a string representation of this State"
        return "[" + State.valueDictionary[self.value] + ", next: " + str(self.nextState) + ", blocked: " + str(self.blockedState) + ", break: " + str(self.breakState) + ", break after: " + str(self.breakAfter) + ", ID: " + str(self.identifier) + "]"
    
    def copyState(self):
        "Constructs and returns a copy of this State object"
        return State(self.nextState, self.blockedState, self.breakState, self.breakAfter, self.value, self.identifier)


class Evolution:
    "Evolves a population to develop more advanced individuals or solutions"
    def __init__(self, popSize):
        "Constructor"
        self.population = [] #A list of objects representing each individual in the current population
        self.popSize = popSize #The number of individuals in the population
        self.generation = 0 #The current generation number
        self.popFitness = [] #The list of fitnesses of all individuals in the population
        self.evalMovements = 2500 #The number of movements attempted in each fitness evaluation
        self.bestIndividual = None #The best individual in the current generation
        self.maxFitness = 0 #The max fitness in the current generation
        self.maxStartingSize = 20 #Maximum number of states in initial individuals
        self.field = None #The Field used for evaluation
        self.startingPosition = None #The starting position in the evaluation Field
        self.fieldWidth = 480 #The width of the evaluation Field
        self.fieldHeight = 270 #The height of the evaluation Field
        self.fieldBorderValue = 1 #The value representing the border of the evaluation Field
        self.fieldObstacleFillerValue = 2 #The value representing the inside of obstacles in the evaluation Field
        self.highPop = [] #A list containing population members with high fitnesses relative to the rest of the population
        self.lowPop = [] #A list containing population members with low fitnesses relative to the rest of the population
        self.selectionPercentile = 30 #Percent of individuals in the highPop list
        self.probabilityHighParent = 0.8 #Probability a parent will be selected from the highPop list
        self.mutationRate = 0.1 #The probability an individual will be mutated
        self.carryOver = 0.75 #Fraction of new individuals in each generation
        self.evalSample = 10 #Number of random Fields to evaluate each individual against when determining fitness
        self.evalsDone = 0 #The number of fitness evaluations done
        self.evaluationBlockedShortcut = True #True if the fitness evaluation should stop prematurely if the individual may be blocked
        
        #threading variables
        self.threadCount = 4 #4 is best with my  processor, will need to be configured for best performance on a given machine.
        self.popChunks = [] #List of subsets/chunks of the population to be evaluated in seperate threads
        
    def initializePopulation(self):
        "Creates the initial random population"
        for i in range(0, self.popSize):
            self.population.append(self.generateRandomIndividual())
        self.popFitness = [0]*len(self.population)
        self.maxFitness = 0
        for i in range(0, self.evalSample):
            self.evaluatePopulation()
            
    def generateRandomIndividual(self):
        "Generates a random state machine"
        statesNum = random.randint(1, self.maxStartingSize)
        states = {}
        for i in range(0, statesNum):
            states[i] = State(random.randint(0, statesNum-1), random.randint(0, statesNum-1), random.randint(0, statesNum-1), random.choice((-1, random.randint(0, 100))), random.randint(1, State.values), i)
        stateMachine = StateMachine(states)
        stateMachine.purgeIslands()
        return stateMachine
    
    def evaluatePopulation(self):
        "Evaluates the fitness of each individual in the population"
        global fitnessQueue
        self.generateField()
        self.threadCounter = 0
        if self.threadCount > 1:
            popChunkSize = math.ceil(self.popSize/(self.threadCount))
            self.popChunks = list(Evolution.getChunks(self.population, popChunkSize))
            actualThreadCount = len(self.popChunks) #if ((self.popSize % (self.threadCount-1)) != 0) else (self.threadCount-1) #If there is no remainder, no need for last chunk

            processes = [multiprocessing.Process(target=self.evaluatePopChunk, args=(x, fitnessQueue, self.popChunks[x])) for x in range(actualThreadCount)]
            # Run processes
            for p in processes:
                p.start()
            # Exit the completed processes
            for p in processes:
                p.join()
            # Get process results from the output queue
            results = [fitnessQueue.get() for p in processes]
            results.sort()
            results = [r[1] for r in results]

            for i in range(0, self.popSize): #recombine fitness
                self.popFitness[i] += results[int(i / popChunkSize)][i % popChunkSize]
                if (self.popFitness[i] > self.maxFitness):
                    self.maxFitness = self.popFitness[i]
                    self.bestIndividual = self.population[i]
        else:
            self.evaluatePopSingleThread()
        
    def evaluatePopSingleThread(self):
        "Evaluates entire population"
        for index, individual in enumerate(self.population):
            fitness = self.evaluateFitness(individual)
            self.popFitness[index] += fitness
            if (self.popFitness[index] > self.maxFitness):
                self.maxFitness = self.popFitness[index]
                self.bestIndividual = individual
                
    def evaluatePopChunk(self, i, fitnessQueue, population):
        "Evaluates the given chunk of the population. Parameters: i: thread number, fitnessQueue: a queue that all fitnesses will be added to, population: the individuals to evaluate"
        fitnessList = []
        for index, individual in enumerate(population):
            fitness = self.evaluateFitness(individual)
            fitnessList.append(fitness)
        fitnessQueue.put((i, fitnessList))
        
    def getChunks(l, n): 
        "Yields n members of list l. Fist time called will return the first n members, the next time will return the next n members, etc."
        for i in range(0, len(l), n):  
            yield l[i:i + n] 
        
    def evaluateFitness(self, individual):
        "Evaluates the fitness of an individual based on the number of unique coordinates it travels to"
        coordinatesTravelled = []
        position = Coordinate(int(self.startingPosition.x), int(self.startingPosition.y))
        individual.currentState = 0
        individual.resetStates()
        direction = individual.getCurrentValue()
        statesNum = len(individual.statesDict)
        consecutiveBlocks = 0
        for i in range(0, self.evalMovements):
            startX = int(position.x)
            startY = int(position.y)
            if direction == 1: #up
                position.y += 1
            elif direction == 2: #up-right
                position.y += 1
                position.x += 1
            elif direction == 3: #right
                position.x += 1
            elif direction == 4: #down-right
                position.y += -1
                position.x += 1
            elif direction == 5: #down
                position.y += -1
            elif direction == 6: #down-left
                position.y += -1
                position.x += -1
            elif direction == 7: #left
                position.x += -1
            elif direction == 8: #up-left
                position.y += 1
                position.x += -1
            blocked = self.field.getValueAtCoordinate(position) != 0
            if blocked == True:
                consecutiveBlocks += 1
                if (self.evaluationBlockedShortcut and consecutiveBlocks > statesNum):
                    break #This is a shortcut for performance, but it may not actually be stuck since the hit count may transition to an unblocked break state eventually
                position = Coordinate(startX, startY)
                direction = individual.getBlockedValue()
            else:
                consecutiveBlocks = 0
                coordinatesTravelled.append(position)
                direction = individual.getNextValue()
        return len(Counter(coordinatesTravelled).keys())

    def generateField(self):
        "Randomly generates the field that individuals will be evaluated against"
        #minCircleSize = 0
        #maxCircleSize = 1
        #obstacles = 1
        self.field = Field(self.fieldWidth, self.fieldHeight, 0)
        minCircleSize = 10
        maxCircleSize = 80
        obstacles = random.randint(1, 10)
        for s in range(0, obstacles):
            sides = random.randint(1, 2) #change upper bound for other shapes
            if (sides < 3):
                self.field.generateCircle(random.randint(minCircleSize, maxCircleSize), Coordinate(random.randint(0, self.fieldWidth-1), random.randint(0, self.fieldHeight-1)), self.fieldBorderValue, self.fieldObstacleFillerValue)
            #else:
                #self.field.generateRandomShape(sides, random.randint(minCircleSize, maxCircleSize), Coordinate(random.randint(0, self.fieldWidth-1), random.randint(0, self.fieldHeight-1)), self.fieldBorderValue, self.fieldObstacleFillerValue)
        self.field.drawFieldBorder(self.fieldBorderValue)
        self.startingPosition = self.field.getOpenCoordinate()
		
    def nextGeneration(self):
        "Evaluates current generation and creates next generation of individuals"
        self.evalsDone = 0
        self.initializeOverselection()
        newPopulation = []
        for i in range(1, int(self.popSize*self.carryOver)):
            newPopulation.append(self.mutate(self.crossover(self.selectParent(), self.selectParent())))
        newPopulation.append(self.bestIndividual) #carry over best individual
        for i in range(0, self.popSize - len(newPopulation)): #Get the remaining individuals by cloning
            newPopulation.append(self.selectParent())
        self.population = newPopulation
        self.generation += 1
        #reset fitnesses and evaluate new fitnesses
        self.popFitness.clear()
        self.popFitness = [0]*len(self.population)
        self.maxFitness = 0
        for i in range(0, self.evalSample):
            self.evaluatePopulation()
            self.evalsDone = i + 1
            
    def selectParent(self):
        "Selects a parent from highPop with the probability of the probabilityHighParent value, otherwise selects a parent from lowPop"
        highNum = len(self.highPop)
        lowNum = len(self.lowPop)
        if (highNum != 0 and (random.randint(1,100)/100 <= self.probabilityHighParent)) or lowNum == 0:
            highNum-=1
            return self.highPop[random.randint(0, len(self.highPop)-1)];
        else:
            lowNum-=1
            return self.lowPop[random.randint(0, len(self.lowPop)-1)];
                
        return self.population[random.randint(0, len(self.population)-1)];
    
    def initializeOverselection(self):
        "Creates the groups of individuals for Overselection using the percentile value. (Percentile determines what percent of individuals go in the highPop list)"
        self.highPop = []
        self.lowPop = []
        fitness = self.popFitness[:]
        fitness.sort()
        #put top x% in high list
        boundary = fitness[int(self.popSize*((100 - self.selectionPercentile)/100))]
        for index, p in enumerate(self.population):
            if self.popFitness[index] >= boundary:
                self.highPop+=[p]
            else:
                self.lowPop+=[p]
                
    def crossover(self, a, b):
        "Combines 'a' and 'b' to create child. Chooses 50% of genes in 'a' to replace/add in 'b'"
        aKeys = list(a.statesDict.keys())
        bCopy = b.copyMachine()
        for i in range(0, int(len(aKeys)/2)):
            key = random.choice(aKeys)
            bCopy.replaceOrAddState(a.statesDict.get(key))
            aKeys.remove(key)
        #b.purgeIslands() #TODO: Investigate performance repercussions of the purgeIslands() call here. Consider moving elsewhere.
        return bCopy
    
    def mutate(self, individual):
        "Mutates individual by adding, removing, or modifying states"
        if (self.mutationRate*1000) >= random.randint(1, 1000): #may or may not mutate depending on rate.
            mutationType = random.randint(0, 2)
            if mutationType == 0: #insert new state
                if len(individual.statesDict) > 1:
                    key1 = random.choice(list(individual.statesDict.keys()))
                    stateType = random.randint(0,2)
                    key2 = individual.statesDict.get(key1).nextState if (stateType == 0) else individual.statesDict.get(key1).blockedState if (stateType == 1) else individual.statesDict.get(key1).breakState
                    ident = individual.getNewId()
                    nextState = 0
                    blockedState = 0
                    breakState = 0
                    breakAfter = random.choice((-1, random.randint(0, 100)))
                    stateType2 = random.randint(0,2)
                    if stateType2 == 0:
                        nextState = key2
                        blockedState = random.choice(list(individual.statesDict.keys()))
                        breakState = random.choice(list(individual.statesDict.keys()))
                    elif stateType2 == 1:
                        blockedState = key2
                        nextState = random.choice(list(individual.statesDict.keys()))
                        breakState = random.choice(list(individual.statesDict.keys()))
                    else:
                        blockedState = random.choice(list(individual.statesDict.keys()))
                        nextState = random.choice(list(individual.statesDict.keys()))
                        breakState = key2
                    individual.statesDict[ident] = State(nextState, blockedState, breakState, breakAfter, random.randint(1, 8), ident)
                    if stateType == 0:
                        individual.statesDict.get(key1).nextState = ident
                    elif stateType == 1:
                        individual.statesDict.get(key1).blockedState = ident
                    else:
                        individual.statesDict.get(key1).breakState = ident
                else:
                    stateType = random.randint(0,2)
                    ident = individual.getNewId()
                    nextState = 0
                    blockedState = 0
                    breakState = 0
                    breakAfter = random.choice((-1, random.randint(0, 100)))
                    individual.statesDict[ident] = State(nextState, blockedState, breakState, breakAfter, random.randint(1, 8), ident)
                    if stateType == 0:
                        individual.statesDict.get(0).nextState = ident
                    elif stateType == 1:
                        individual.statesDict.get(0).blockedState = ident
                    else:
                        individual.statesDict.get(0).breakState = ident
            elif mutationType == 1: #remove random state
                individual.removeState(random.choice(list(individual.statesDict.keys())))
            else: #modify random state
                key = random.choice(list(individual.statesDict.keys()))
                individual.statesDict[key] = individual.statesDict[key].copyState()
                modType = random.randint(0, 4)
                if modType == 0: #modify value
                    individual.statesDict.get(key).value = random.randint(1, 8)
                elif modType == 1: #modify nextState
                    individual.statesDict.get(key).nextState = random.choice(list(individual.statesDict.keys()))
                elif modType == 2: #modify blockedState
                    individual.statesDict.get(key).blockedState = random.choice(list(individual.statesDict.keys()))
                elif modType == 3: #modify breakState
                    individual.statesDict.get(key).breakState = random.choice(list(individual.statesDict.keys()))
                else: #modify breakAfter
                    individual.statesDict.get(key).breakAfter = random.choice((-1, random.randint(0, 1000)))
        return individual
    
    def getBestIndividual(self):
        "Returns best individual from the last generation"
        return self.bestIndividual


class Coordinate:
    "An object representing an X,Y coordinate pair"
    def __init__(self, x, y):
        "Constructor"
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        "Overrides the default 'equals' implementation"
        if isinstance(other, Coordinate):
            return self.x == other.x and self.y == other.y
        return False
    
    def __ne__(self, other):
        "Overrides the default 'not equal' implementation"
        return not self.__eq__(other)
    
    def __hash__(self):
        "Overrides the default 'hash' implementation. Bases hash off of x and y value."
        return hash((self.x, self.y))
    
    def toString(self):
        "Returns a string representation of this Coordinate with the form '(x, y)'"
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def copy(self):
        "Returns a copy of this Coordinate, with the same x and y"
        return Coordinate(self.x, self.y)

class Field:
    "An object representing an area"
    def __init__(self, width, height, filler):
        "Constructor"
        self.width = width #width of field
        self.height = height #height of field
        self.defaultFiller = filler #default filler for field background
        self.grid = [] #Grid containing all field values
        for i in range(0, width):
            yList = [filler]*height
            self.grid.append(yList)
            
    def writeValueAtCoordinate(self, coordinate, offsetCoordinate, value, edgeCorrect = False):
        "Writes a value at the sum of the given coordinates"
        x = coordinate.x + offsetCoordinate.x
        y = coordinate.y + offsetCoordinate.y
        if (x < self.width) and (y < self.height) and (x >= 0) and (y >= 0):
            self.grid[x][y] = value
            return True
        elif (edgeCorrect):
            x = 0 if x < 0 else self.width-1 if x >= self.width else x
            y = 0 if y < 0 else self.height-1 if y >= self.height else y
            self.grid[x][y] = value
        return False
            
    def getValueAtCoordinate(self, coordinate):
        "Returns the value at the coordinate"
        if (coordinate.x < self.width) and (coordinate.y < self.height) and (coordinate.x >= 0) and (coordinate.y >= 0):
            return self.grid[coordinate.x][coordinate.y]
        
    def generateCircle(self, radius, coordinate, borderValue, filler):
        "Adds a circle with the given radius centered around the given coordinate with the border defined by the given value and filled in with the given filler value"
        for x in range (0, radius+1):
            #draw border
            y = int(round(math.sqrt((radius*radius) - (x*x))))# x^2 +y^2 = r^2     y = sqrt(r^2 - x^2)
            self.writeValueAtCoordinate(coordinate, Coordinate(x, y), borderValue)
            self.writeValueAtCoordinate(coordinate, Coordinate(-1*x, y), borderValue)
            self.writeValueAtCoordinate(coordinate, Coordinate(x, -1*y), borderValue)
            self.writeValueAtCoordinate(coordinate, Coordinate(-1*x, -1*y), borderValue)
            #switch y and x to account for multiple border coordinates with the same x value
            self.writeValueAtCoordinate(coordinate, Coordinate(y, x), borderValue)
            self.writeValueAtCoordinate(coordinate, Coordinate(-1*y, x), borderValue)
            self.writeValueAtCoordinate(coordinate, Coordinate(y, -1*x), borderValue)
            self.writeValueAtCoordinate(coordinate, Coordinate(-1*y, -1*x), borderValue)
            #fill coordinates from 0 to y
            for y2 in range(0, y):
                self.writeValueAtCoordinate(coordinate, Coordinate(x, y2), filler)
                self.writeValueAtCoordinate(coordinate, Coordinate(-1*x, y2), filler)
                self.writeValueAtCoordinate(coordinate, Coordinate(x, -1*y2), filler)
                self.writeValueAtCoordinate(coordinate, Coordinate(-1*x, -1*y2), filler)
                
    def generateRandomShape(self, vertexCount, radius, coordinate, borderValue, filler): #Currently doesn't work. TODO: Use pygame's shape generation to draw shape
        "Draws a random shape with given number of vertices with a max radius centered around the given coordinate, and fills it with the filler value"
        if vertexCount < 3:
            return
        vertices = set()
        averageX = 0
        averageY = 0
        self.generateCircle(radius, coordinate, borderValue, filler)
        for i in range(0, vertexCount):
            x = random.randint(-1*(radius), radius)
            y = int(round(math.sqrt((radius*radius) - (x*x))))*random.choice((-1, 1))
            averageX += x
            averageY += y
            vertices.add(Coordinate(x, y))
        averageCoordinate = Coordinate(int((averageX/vertexCount)+coordinate.x), int((averageY/vertexCount)+coordinate.y))
        shapeField = Field(2*radius, 2*radius, self.defaultFiller)
        fieldOffset = Coordinate(coordinate.x + radius, coordinate.y + radius)
        shapeOffset = Coordinate(radius, radius)
        firstV = None
        #lastV = None
        lineCounter = 0
        verticesSize = len(vertices)
        allConnected = False
        foundVertex = None
        for x in range(-1*radius, radius):
            if allConnected:
                break;
            #find first vertex with positive y, link it with next vertex with positive y
            for vert in vertices:
                if (lineCounter == verticesSize - 1):
                    shapeField.drawLine(Coordinate(foundVertex.x, foundVertex.y), Coordinate(firstV.x, firstV.y), borderValue, shapeOffset, True)
                    allConnected = True
                    break;
                if (vert.x == x and vert.y >= 0):
                    if (foundVertex == None):
                        foundVertex = vert
                        firstV = vert
                    else:
                        shapeField.drawLine(Coordinate(foundVertex.x, foundVertex.y), Coordinate(vert.x, vert.y), borderValue, shapeOffset, True)
                        foundVertex = vert
                        lineCounter += 1
        for x in range(-1*radius, radius):
            if allConnected:
                break;
            #find first vertex with negative y, link it with next vertex with negative y
            oppX = x *-1
            for vert in vertices:
                if (lineCounter == verticesSize - 1):
                    shapeField.drawLine(Coordinate(foundVertex.x, foundVertex.y), Coordinate(firstV.x, firstV.y), borderValue, shapeOffset, True)
                    allConnected = True
                    break;
                if (vert.x == oppX and vert.y < 0):
                    if (foundVertex == None):
                        foundVertex = vert
                        firstV = vert
                    else:
                        shapeField.drawLine(Coordinate(foundVertex.x, foundVertex.y), Coordinate(vert.x, vert.y), borderValue, shapeOffset, True)
                        foundVertex = vert
                        lineCounter += 1
        #self.fillArea(averageCoordinate, filler, borderValue)
        runningCoordinate = None
        radius+= 10
        for x in range(-1*radius, radius):
            edgeY = int(round(math.sqrt((radius*radius) - (x*x))))
            fillCoordinates = []
            withinBorders = False
            #from (x, -y) to (x, y)
            for y in range(-1*edgeY, edgeY):
                runningCoordinate = Coordinate(x+radius, y+radius)
                previousCoordinate = Coordinate(x+radius, y+radius-1)
                if (shapeField.getValueAtCoordinate(runningCoordinate) == borderValue and shapeField.getValueAtCoordinate(previousCoordinate) != borderValue):
                    withinBorders = not withinBorders
                elif withinBorders:
                    fillCoordinates += [runningCoordinate]
                    #self.writeValueAtCoordinate(runningCoordinate, coordinate, filler)
            if not withinBorders and len(fillCoordinates) > 0:
                for c in fillCoordinates:
                    shapeField.writeValueAtCoordinate(c, Coordinate(0,0), filler)
        self.transferFrom(shapeField, fieldOffset)

    def transferFrom(self, otherField, offset):
        for x in range(otherField.width):
            for y in range(otherField.height):
                X = x + offset.x
                Y = y + offset.y
                value = otherField.grid[x][y]
                if (X < self.width) and (Y < self.height) and (X >= 0) and (Y >= 0):
                    if (value != otherField.defaultFiller):
                        self.grid[X][Y] = value
        
    def drawLine(self, a, b, value, offset, edgeCorrect = False): #TODO: Allow line to have an approximate slope to avoid noticeable staircasing
        "Draws a line between coordinate A and coordinate B using the value given"
        if a == None or b == None:
            return
        rise = b.y - a.y
        run = b.x - a.x
        riseAmt = 1 if rise >= 0 else -1
        runAmt = 1 if run >= 0 else -1
        absRise = abs(rise)
        absRun = abs(run)
        currentCoordinate = a.copy()
        self.writeValueAtCoordinate(currentCoordinate, offset, value)
        if (absRise > absRun):
            interval = int(absRise / absRun)+1 if absRun != 0 else 100000000
            remainder = absRise % absRun  if absRun != 0 else 0
            runCount = 0
            for i in range(1, absRise+1):
                currentCoordinate.y += riseAmt
                self.writeValueAtCoordinate(currentCoordinate, offset, value, edgeCorrect)
                if ((i % interval) == 0):
                    runCount += 1
                    currentCoordinate.x += runAmt
                    self.writeValueAtCoordinate(currentCoordinate, offset, value, edgeCorrect)
            for i in range(absRun - runCount):
                currentCoordinate.x += runAmt
                self.writeValueAtCoordinate(currentCoordinate, offset, value, edgeCorrect)
        else:
            interval = int(absRun / absRise)+1 if absRise != 0 else 100000000
            remainder = absRun % absRise  if absRise != 0 else 0
            riseCount = 0
            for i in range(1, absRun+1):
                currentCoordinate.x += runAmt
                self.writeValueAtCoordinate(currentCoordinate, offset, value, edgeCorrect)
                if ((i % interval) == 0):
                    riseCount += 1
                    currentCoordinate.y += riseAmt
                    self.writeValueAtCoordinate(currentCoordinate, offset, value, edgeCorrect)
            for i in range(absRise - riseCount):
                currentCoordinate.y += riseAmt
                self.writeValueAtCoordinate(currentCoordinate, offset, value, edgeCorrect)
                
    def fillArea(self, coordinate, filler, border, count =0):
        "Fills an enclosed area, containing the given coordinate and defined by the given border value, with the given filler"
        if count > 10:
            return
        value = self.getValueAtCoordinate(coordinate)
        count+=1
        if (value != filler and value != border):
            self.writeValueAtCoordinate(coordinate, Coordinate(0,0), filler)
            self.fillArea(Coordinate(coordinate.x+1, coordinate.y), filler, border, count)
            self.fillArea(Coordinate(coordinate.x-1, coordinate.y), filler, border, count)
            self.fillArea(Coordinate(coordinate.x, coordinate.y+1), filler, border, count)
            self.fillArea(Coordinate(coordinate.x, coordinate.y-1), filler, border, count)
            
    def drawFieldBorder(self, border):
        "Draws a border around the field"
        for x in range(0, self.width):
            self.grid[x][self.height-1] = border #top border
            self.grid[x][1] = border #bottom border
            self.grid[x][0] = border #bottom border
        for y in range(0, self.height):
            self.grid[0][y] = border #left border
            self.grid[self.width-1][y] = border #right border
            
    def getOpenCoordinate(self):
        "Get random open coordinate. Will loop through field after 10000 random attempts."
        count = 0
        while(count < 10000):
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            if self.grid[x][y] == self.defaultFiller:
                return Coordinate(x,y)
            count += 1
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.grid[x][y] == self.defaultFiller:
                    return Coordinate(x,y)
        return None

class Pixel:
    "An object representing a pixel"
    def __init__(self, x, y, r, g, b):
        "Constructor"
        self.x = x #x coordinate
        self.y = y #y coordinate
        self.r = r #red value (0 to 255)
        self.g = g #green value (0 to 255)
        self.b = b #blue value (0 to 255)
                        

class EvolutionVisualizer:
    def __init__(self):
        self.iteration = 0
        self.pixelArray = []
        self.newPixels = []
        self.screen = None
        self.genCount = 0
        self.evolution = None
        self.individual = None
        self.individualStates = None
        self.consecutiveBlocks = 0
        self.nextGenReady = True
        self.maxFitness = 0
        self.screenWidth = 0
        self.screenHeight = 0
        self.requestVisualizerLock = False
        self.visualizerLocked = False
        self.prevState = "0"
        self.totalEvals = 0
        self.progressString = "0%"
        self.background_colour = (0,0,0)
        self.displayFont = None
        self.true_res = (0, 0)
        self.populationSize = 200 #Number of individuals in each generation
        self.field = None
        self.fieldRendered = False
        self.initialized = False
        
    def initialize(self):
        pygame.font.init()
        self.displayFont = pygame.font.SysFont(None, 30)
        sys.setrecursionlimit(100000000)
        pygame.init()
        ctypes.windll.user32.SetProcessDPIAware()
        self.screenWidth = ctypes.windll.user32.GetSystemMetrics(0)
        self.screenHeight = ctypes.windll.user32.GetSystemMetrics(1)
        self.true_res = (self.screenWidth, self.screenHeight)
        self.screen = pygame.display.set_mode(self.true_res, pygame.FULLSCREEN)
        pygame.display.set_caption('Evolutionary Display')
        self.screen.fill(self.background_colour)
        textsurface = self.displayFont.render("Initializing evolution...", False, (255, 255, 255))
        self.screen.blit(textsurface,(0,0))
        pygame.display.flip()
        #initialize evolution and create loading screen
        initializationThread = threading.Thread(target=self.doInitializeEvolution)
        initializationThread.start()
        self.loadingWindowLoop()

    def doInitializeEvolution(self):
        "Generates and evaluates initial population and generates first visualizer field"
        #Begin evolution
        print("Starting evolution...")
        self.evolution = Evolution(self.populationSize)
        self.totalEvals = self.evolution.evalMovements * self.evolution.evalSample
        self.evolution.initializePopulation()
        self.individual = self.evolution.getBestIndividual().copyMachine()
        self.individualStates = len(self.individual.statesDict)
        self.maxFitness = self.evolution.maxFitness
        print("Evolution Started")
        self.createVisualizationField()
        print("Field Generated")
        self.initialized = True

    def windowLoop(self):
        "Visualizer run loop"
        while(not self.initialized): #Loop until visualizer is unlocked
            time.sleep(0.5)
        running = True
        while running:
            self.updateScreen()
            for event in pygame.event.get():
                if (event.type is pygame.KEYDOWN and event.key == pygame.K_f):
                    if self.screen.get_flags() & pygame.FULLSCREEN:
                        self.screen = pygame.display.set_mode(self.true_res)
                    else:
                        self.screen = pygame.display.set_mode(self.true_res, pygame.FULLSCREEN)
                    self.screen.fill(self.background_colour)
                    #set each pixel
                    for p in self.pixelArray:
                        self.screen.set_at((p[0],self.screenHeight-p[1]), (p[2],p[3],p[4]))
                    textsurface = self.displayFont.render(" Generation: "+str(self.genCount)+ "    Fitness: " + str(self.maxFitness), False, (255, 255, 255))
                    self.screen.blit(textsurface,(0,0))
                    pygame.display.flip()
                if event.type == pygame.QUIT or (event.type is pygame.KEYDOWN and event.key == pygame.K_q):
                    running = False
        pygame.quit()
                    
    def loadingWindowLoop(self):
        "Visualizer loading screen run loop"
        stop = False
        counter = 0
        animationCount = 0
        animationDisplayChar = "O "
        animationDisplay = ""
        while not (self.initialized or stop):
            time.sleep(0.5)
            if animationCount == 5:
                animationDisplay = "O "
                animationCount = 0
            else:
                animationDisplay += animationDisplayChar
            if self.screen.get_flags() & pygame.FULLSCREEN:
                self.screen.fill(self.background_colour)
                textsurface = self.displayFont.render("Initializing evolution...", False, (255, 255, 255))
                self.screen.blit(textsurface,(0,0))
                textsurface = self.displayFont.render(animationDisplay, False, (255, 255, 255))
                self.screen.blit(textsurface,(int(self.screenWidth/2),int(self.screenHeight/2)))
                pygame.display.flip()
            else:
                self.screen.fill(self.background_colour)
                textsurface = self.displayFont.render("Initializing evolution...", False, (255, 255, 255))
                self.screen.blit(textsurface,(0,0))
                textsurface = self.displayFont.render(animationDisplay, False, (255, 255, 255))
                self.screen.blit(textsurface,(150,150))
                pygame.display.flip()
            animationCount += 1

            for event in pygame.event.get():
                if (event.type is pygame.KEYDOWN and event.key == pygame.K_f):
                    if self.screen.get_flags() & pygame.FULLSCREEN:
                        self.screen = pygame.display.set_mode((300, 300))
                    else:
                        self.screen = pygame.display.set_mode(self.true_res, pygame.FULLSCREEN)
                    self.screen.fill(self.background_colour)
                    textsurface = self.displayFont.render("Initializing evolution...", False, (255, 255, 255))
                    self.screen.blit(textsurface,(0,0))
                    pygame.display.flip()
                if event.type == pygame.QUIT or (event.type is pygame.KEYDOWN and event.key == pygame.K_q):
                    stop = True

    def updateScreen(self):
        "Updates/renders up-to-date text, field, and demo explorer path as defined in newPixels and pixelArray"
        self.iterateStateMachine()
        if (not self.fieldRendered) and self.nextGenReady:
            self.fieldRendered = True
            self.screen.fill(self.background_colour)
            #set each pixel
            for p in self.pixelArray:
                self.screen.set_at((p[0],self.screenHeight-p[1]), (p[2],p[3],p[4]))
            textsurface = self.displayFont.render(" Generation: "+str(self.genCount)+ "    Fitness: " + str(self.maxFitness), False, (255, 255, 255))
            self.screen.blit(textsurface,(0,0))
        elif (self.iteration % 20) == 0:
            for p in self.newPixels:
                self.screen.set_at((p[0],self.screenHeight-p[1]), (p[2],p[3],p[4]))
            self.newPixels = []
            prevStateText = self.displayFont.render("Current State: " + str(self.prevState), False, (0,0,0)) #hide previous state
            prevProgressText = self.displayFont.render("Progress: " + self.progressString, False, (0,0,0))
            isBlocked = self.consecutiveBlocks > self.individualStates
            textColor = (255, 0, 0) if isBlocked else (255,255,255)
            self.progressString = str(float(int(((self.evolution.evalMovements * self.evolution.evalsDone)/self.totalEvals)*10000))/100) + "%"
            stateNumString = (str(self.individual.currentState) if not isBlocked else "BLOCKED")
            stateText = self.displayFont.render("Current State: " + stateNumString, False, textColor)
            progressText = self.displayFont.render("Progress: " + self.progressString, False, (255,255,255))
            self.screen.blit(prevStateText, (500, 0))
            self.screen.blit(prevProgressText, (800, 0))
            self.screen.blit(stateText, (500, 0))
            self.screen.blit(progressText, (800, 0))
            self.prevState = stateNumString
        pygame.display.flip()

    def iterateStateMachine(self):
        "Goes through next state and adds pixel values to pixelArray"
        if(self.requestVisualizerLock):
            self.visualizerLocked = True
            while(self.visualizerLocked): #Loop until visualizer is unlocked
                time.sleep(0.5)

        if not self.nextGenReady:
            #get new coordinate based on state machine movement
            coordinatesTravelled = set()
            direction = self.individual.getCurrentValue()
            startPosition = Coordinate(int(self.position.x), int(self.position.y))
            if direction == 1: #up
                self.position.y += 1
            elif direction == 2: #up-right
                self.position.y += 1
                self.position.x += 1
            elif direction == 3: #right
                self.position.x += 1
            elif direction == 4: #down-right
                self.position.y += -1
                self.position.x += 1
            elif direction == 5: #down
                self.position.y += -1
            elif direction == 6: #down-left
                self.position.y += -1
                self.position.x += -1
            elif direction == 7: #left
                self.position.x += -1
            elif direction == 8: #up-left
                self.position.y += 1
                self.position.x += -1
            blocked = self.field.getValueAtCoordinate(self.position) != 0
            if blocked == True:
                self.consecutiveBlocks += 1
                self.position = startPosition
                direction = self.individual.getBlockedValue()
            else:
                self.consecutiveBlocks = 0
                coordinatesTravelled.add(self.position)
                direction = self.individual.getNextValue()
                self.pixelArray += [(self.position.x, self.position.y, 255, 255, 255)]
                self.newPixels += [(self.position.x, self.position.y, 255, 255, 255)]
                self.pixelArray += [(startPosition.x, startPosition.y, 0, 255, 0)]
                self.newPixels += [(startPosition.x, startPosition.y, 0, 255, 0)]
        elif (self.iteration) > 0:
            print("Best Fitness: " + str(self.evolution.maxFitness))
            print(self.individual.toString())
            print("Starting next generation")
            self.nextGenReady = False
            #spawn new thread calling doEvolution()
            evoThread = threading.Thread(target=self.doEvolution)
            evoThread.start()
        self.iteration+=1

    def doEvolution(self):
        "Creates the next generation, creates the next visualization Field, and chooses individual to display in visualizer (highest fitness)"
        self.evolution.nextGeneration()
        
        self.requestVisualizerLock = True
        while(not self.visualizerLocked): #loop until visualizer is locked
            time.sleep(0.5)
            
        self.createVisualizationField()
        self.individual = self.evolution.getBestIndividual().copyMachine()
        self.individualStates = len(self.individual.statesDict)
        self.consecutiveBlocks = 0
        self.genCount = int(self.evolution.generation)
        self.maxFitness = int(self.evolution.maxFitness)
        print(self.genCount)
        self.iteration = 0
        self.nextGenReady = True
        self.requestVisualizerLock = False
        self.visualizerLocked = False


    def createVisualizationField(self):
        "Creates the Field to be displayed in the visualizer"
        self.fieldRendered = False
        self.pixelArray = []
        self.newPixels = []
        self.field = Field(self.screenWidth, self.screenHeight-40, 0)
        obstacles = random.randint(1, 20)
        for s in range(0, obstacles):
            sides = random.randint(1, 5)
            if (sides < 3):
                self.field.generateCircle(random.randint(10, 300), Coordinate(random.randint(0, self.screenWidth-1), random.randint(0, self.screenHeight-41)), 1, 2)
            else:
                self.field.generateRandomShape(sides, random.randint(10, 300), Coordinate(random.randint(0, self.screenWidth-1), random.randint(0, self.screenHeight-41)), 1, 2)
        self.field.drawFieldBorder(1)
        self.position = self.field.getOpenCoordinate()
        for x in range(0, self.field.width):
            for y in range(0, self.field.height):
                if self.field.grid[x][y] == 1:
                    self.pixelArray += [(x, y, 0, 0, 255)]
                    self.newPixels += [(x, y, 0, 0, 255)]
                elif self.field.grid[x][y] == 2:
                    self.pixelArray += [(x, y, 100, 100, 255)]
                    self.newPixels += [(x, y, 100, 100, 255)]
        

def main():
    "Initializes pygame and begins evolution and visualizer"
    print("Welcome to ExplorerEvolution! Please be patient while the starting population is generated.")
    visualizer = EvolutionVisualizer()
    visualizer.initialize()
    visualizer.windowLoop()

if __name__ == "__main__":
    main()
    


