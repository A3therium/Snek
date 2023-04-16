# Imports
from common import *
import time
import random as rn
import keyboard
import sys
# Globals
entityList = []
# Functions
class Entity:
    def __init__(self,pos,sprite,identifier):
        self.id = identifier
        self.sprite = sprite
        self.pos = pos
        entityList.append(self)

    def tick(self):
        pass

class Head(Entity):
    def __init__(self, map, auto):
        self.auto = auto
        pos = [0,0]
        super().__init__(pos, '\x1b[1;32m^\x1b[0m','head')
        self.sprites = ['\x1b[1;32m^\x1b[0m','\x1b[1;32m<\x1b[0m','\x1b[1;32mv\x1b[0m','\x1b[1;32m>\x1b[0m']
        self.direciton = 3
        self.directions = [[0,-1],[-1,0],[0,1],[1,0]]
        if self.auto:
            self.speed = 3 # How many frames to move 1 cell
        else:
            self.speed = 10 # How many frames to move 1 cell
        self.frameCount = 0 # Total frames elapsed
        self.score = 0
        self.apple = Apple(map)
        Tail(self.pos)
        self.maxTailFrames = self.speed
        self.turnCooldown = False

        if self.auto:
            # Perfect path generator, requires min 4x4 and even width and height
            self.path = ('3' * (len(map[0]) - 2)) + (('2' + ('1' * (len(map[0])-2)) + '2' + ('3' * (len(map[0]) - 2))) * ((len(map[0]) - 2) // 2)) + '2' + ('1' * (len(map[0])-1)) + ('0' * (len(map)-1)) + '3' 

    def tick(self, map):
        if self.turnCooldown == False:
            if keyboard.is_pressed('w') and self.direciton != 2: 
                self.direciton = 0
                self.turnCooldown = True
            elif keyboard.is_pressed('a') and self.direciton != 3: 
                self.direciton = 1
                self.turnCooldown = True
            elif keyboard.is_pressed('s') and self.direciton != 0: 
                self.direciton = 2
                self.turnCooldown = True
            elif keyboard.is_pressed('d') and self.direciton != 1: 
                self.direciton = 3
                self.turnCooldown = True

        self.sprite = self.sprites[self.direciton]
        if self.frameCount % self.speed == 0:
            entityList.append(Tail(self.pos))
            self.pos = arrAdd(self.pos,self.directions[self.direciton])
            self.turnCooldown = False

            if self.auto:
                self.direciton = int(self.path[(self.frameCount // self.speed) % len(self.path)])
        
        # Score code
        i = 0
        while i < len(entityList):
            if entityList[i].id == 'tail':
                if entityList[i].tick(self.maxTailFrames):
                    entityList.pop(i)

                elif self.pos == entityList[i].pos:
                    gameOver(self.score)
            
            i += 1

        if self.pos[0] < 0 or self.pos[0] >= len(map[0]) or self.pos[1] < 0 or self.pos[1] >= len(map):
            gameOver(self.score)

        if self.pos == self.apple.pos:
            self.apple.move(map, self.score)
            self.score += 1
            self.maxTailFrames += self.speed * 2

        self.frameCount += 1



    def printScore(self):
        print(f'\x1b[37mScore: {self.score}\x1b[0m')

class Tail(Entity):
    def __init__(self, pos):
        super().__init__(pos, '\x1b[32m#\x1b[0m','tail')
        self.frames = 0

    def tick(self, maxFrames):
        self.frames += 1
        if self.frames > maxFrames: return True
        else: return False

class Apple(Entity):
    def __init__(self,map):
        super().__init__([rn.randint(0,len(map[0])-1),rn.randint(0,len(map)-1)],'\x1b[1;31m@\x1b[0m','apple')

    def move(self, map, score):
        validPositions = []
        for i in range(0,len(map)):
            for j in range(0,len(map[0])):
                validPositions.append([j,i])

        for i in entityList:
            for k in validPositions:
                if i.pos == k:
                    validPositions.remove(k)
                    break

        if len(validPositions) > 0: 
            self.pos = rn.choice(validPositions)
        else:
            victory(score)

class World:
    def __init__(self,dim):
        self.dim = dim
        self.clearMap()

    def clearMap(self):
        self.map = [[' ' for i in range(0,self.dim[0])] for i in range(0,self.dim[1])] 

    def tick(self):
        self.clearMap()
        self.frame()


    def frame(self):
        for i in reversed(entityList):
            self.map[i.pos[1]][i.pos[0]] = i.sprite
        output = '--' + ('--' * len(self.map[0])) + '-\n| '
        for i in self.map:
            for j in i:
                output += f'{j} '
            output += '|\n| '
        output = output[:-2] + '--' + ('--' * len(self.map[0])) + '-\n'
        print('\x1b[H\x1b[0J',end='') # Clears console and moves cursor to 0,0
        print(output, end='')

def gameOver(score):
    input(f'\x1b[H\x1b[0J\x1b[31mGame Over!\n\x1b[37mFinal Score: {score}\n\x1b[0mPress enter to exit\n\x1b[8m')
    print('\x1b[0m',end='')
    exit()

def victory(score):
    input(f'\x1b[H\x1b[0J\x1b[32mYou Win!\n\x1b[37mFinal Score: {score}\n\x1b[0mPress enter to exit\n\x1b[8m')
    print('\x1b[0m',end='')
    exit()

def main():
    dim = input('\x1b[0mEnter dimensions: (x,y)\n').split(',')
    dim = [int(i) for i in dim]
    SECONDS_PER_FRAME = 0.02
    map = World(dim)
    if input('\x1b[0mPress enter to begin\n') == 'auto':
            player = Head(map.map, True)
    else:
        player = Head(map.map, False)

    while True:
        startTime = time.time()
        player.tick(map.map)
        map.tick()
        player.printScore()
        time.sleep(max(SECONDS_PER_FRAME-(startTime - time.time()),0))

# Driver
if __name__ == '__main__':
    main()