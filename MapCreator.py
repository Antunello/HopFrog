import sys
import os
import numpy as np
import math
import pygame as pg
import time
import random as rd
from utilities import T
from pygame.locals import *
from pygame.transform import scale

config =\
{   'WindowSize': T((792, 648))
}

dim_1=22
dim=18
VELOCITY = 2
FRAMES_PER_SEC = 60//VELOCITY

WHITE = 255, 255, 255
RED = 255, 0, 0
BLUE = 0, 0, 255
BLACK = 0, 0, 0
GREEN = 0, 255, 0

NONE = 0
UP = 1
DOWN = 2
LEFT = 4
RIGHT = 8

SCALAR = 2

TILE_SIZE = 18 * SCALAR
COMMA = ","

VIEW_WIDTH = TILE_SIZE * 22
VIEW_HEIGHT = TILE_SIZE * 22
DIMENSIONS = (VIEW_WIDTH, VIEW_HEIGHT)
TRANSPARENT_COLOUR = GREEN
ORIGIN = (0, 0)

screen = pg.display.set_mode(DIMENSIONS)

DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

def TimeIt(func):
    def timing_func(*args):
        t1 = time.time()
        func(*args)
        t2 = time.time()
    return timing_func


def getMovement(directionBits):
    if directionBits in MOVEMENT:
        return MOVEMENT[directionBits]
    return None

class TileSet:
    
    def __init__(self, tiles):
        self.tiles = tiles
    
    def getTile(self, name):
        if name in self.tiles:
            return self.tiles[name]
        return None


def loadImage(imagePath, colourKey = None):
    # fullName = os.path.join(folder, name)
    try:
        image = pg.image.load(imagePath)
    except pg.error, message:
        print "Cannot load image: ", os.path.abspath(imagePath)
        raise SystemExit, message
    image = image.convert()
    if colourKey is not None:
        image.set_colorkey(colourKey, RLEACCEL)
    return image


def loadScaledImage(imagePath, colourKey = None, scalar = SCALAR):
    img = loadImage(imagePath, colourKey)
    return scale(img, (TILE_SIZE, TILE_SIZE))

def getXY(xyStr, delimiter = COMMA):
    return [int(n) for n in xyStr.split(delimiter)]

def createRectangle(dimensions, colour = None):
    rectangle = pg.Surface(dimensions).convert()
    if colour is not None:
        rectangle.fill(colour)
    return rectangle

class Entity(pg.sprite.Sprite):
    
    def __init__(self, position, color, size=T((18,18))):
        
        pg.sprite.Sprite.__init__(self)
        
        self.position = position
        self.color = color
        self.size = size
        
        self.image = pg.Surface(size)
        self.image.fill(color)
        self.image.convert() # for speed reason, transforms the way blit is
        # called
        
        # grid-position wrt. to the map that holds it
        self.UpdateRect()
    
    def UpdateRect(self):
        self.rect = pg.Rect(self.position, self.size)

class Character(Entity):
    
    def __init__(self, world_position, position, color, size, name):
        
        self.world_position = world_position
        Entity.__init__(self, position, color, size)
        self.name = name


class Player(Character):
    pass


class MapTile:
    
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.levels = []
        self.tiles = []
        self.originalLevels = None
        self.specialLevels = None
        self.downLevels = None
        self.masks = None
        self.events = None
    
    def addTile(self, tile):
        self.tiles.append(tile)
        
    def createTileImage(self):
        if len(self.tiles) == 0:
            return None
        elif len(self.tiles) > 1:
            # if we're layering more than one image we don't want to draw on any of
            # the original images because that will affect every copy
            tileImage = view.createRectangle((TILE_SIZE, TILE_SIZE), view.BLACK)
            for image in self.tiles:
                tileImage.blit(image, (0, 0))
            return tileImage
        return self.tiles[0]



def loadRpgMap(name):
    # check cache first
    # tileData is keyed on an x,y tuple
    tileData = {}
    spriteData = []
    eventData = []
    # parse map file - each line represents one map tile
    mapPath = os.path.join("./", name + ".map")
    with open(mapPath) as mapFile:
        # eg. 10,4 [1] water:dark grass:l2 wood:lrs_supp:3
        maxX, maxY = 0, 0
        for line in mapFile:
            try:
                line = line.strip()
                if len(line) > 0:
                    bits = line.split()
                    if len(bits) > 0:
                        tilePoint = bits[0]
                        #print "%s -> %s" % (tileRef, tileName)
                        x, y = getXY(tilePoint)
                        maxX, maxY = max(x, maxX), max(y, maxY)
                        if len(bits) > 1:
                            tileData[(x, y)] = bits[1:]
            except ValueError:
                pass

        mapTiles = createMapTiles(maxX + 1, maxY + 1, tileData)
    
    # create map and return
    myMap = RpgMap(name, mapTiles)
    return myMap

def createMapTiles(cols, rows, tileData):
    # create the map tiles
    mapTiles = [[MapTile(x, y) for y in range(rows)] for x in range(cols)]
    # iterate through the tile data and set the map tiles
    tileSets = {}
    for tilePoint in tileData.keys():
        bits = tileData[tilePoint]
        x, y = tilePoint[0], tilePoint[1]
        mapTile = mapTiles[x][y]
        # print bits
        startIndex = 0
        # tiles images
        for tileIndex, tiles in enumerate(bits[startIndex:]):
            tileBits = tiles
            if len(tileBits) > 1:
                tileSetName = tileBits
                if tileSetName in tileSets:
                    tileSet = tileSets[tileSetName]
                else:
                    tileSet = loadTileSet(tileSetName)
                    tileSets[tileSetName] = tileSet
                tileName = tileBits
                mapTile.addTile(tileSet.getTile(tileName))

    return mapTiles

def loadTileSet(name):
    # print "load tileset: %s" % (name)
    # tileSet = map.TileSet()
    tiles = {}
    # load tile set image
    imagePath = os.path.join("tiles", name + ".png")
    tilesImage = loadScaledImage(imagePath, TRANSPARENT_COLOUR)
    # parse metadata - each line represents one tile in the tile set
    metadataPath = os.path.join("tiles/meta", name + "_metadata.txt")
    with open(metadataPath) as metadata:
        # eg. 1,5 lst1
        for line in metadata:
            try:
                line = line.strip()
                if len(line) > 0:
                    tilePoint, tileName = line.strip().split()
                    # print "%s -> %s" % (tileRef, tileName)
                    x, y, z = tilePoint.split(COMMA)
                    px, py = int(x) * TILE_SIZE, int(y) * TILE_SIZE
                    tileRect = Rect(px, py, TILE_SIZE, TILE_SIZE)
                    tileImage = tilesImage.subsurface(tileRect).copy()
                    tiles[tileName] = tileImage
            # self.maskTiles[tileName] = view.createMaskTile(tileImage)
            except ValueError:
                pass
    # create tile set and return
    return TileSet(tiles)


class RpgMap:
    
    def __init__(self, name, mapTiles):
        self.name = name
        self.mapTiles = mapTiles
        self.initialiseMapImage()
        self.toRestore = None
    
    def initialiseMapImage(self):
        self.mapImage = createRectangle((22 * TILE_SIZE, 22 * TILE_SIZE),
                                        BLACK)
        for tiles in self.mapTiles:
            for tile in tiles:
                tileImage = tile.createTileImage()
                if tileImage:
                    self.mapImage.blit(tileImage, (tile.x * TILE_SIZE, tile.y * TILE_SIZE))
        self.mapRect = self.mapImage.get_rect()

    
    def getMapView(self, viewRect):
        return self.mapImage.subsurface(viewRect)

    def getBaseRectTiles(self, rect):
        rectTiles = []
        x1, y1 = self.convertTopLeft(rect.left, rect.top)
        x2, y2 = self.convertBottomRight(rect.right - 1, rect.bottom - 1)
        self.verticals = {}
        for x in range(x1, x2 + 1):
            self.verticals[x] = self.mapTiles[x][y1:y2 + 1]
            rectTiles += self.verticals[x]
        self.horizontals = {}
        for y in range(y1, y2 + 1):
            self.horizontals[y] = [self.mapTiles[x][y] for x in range(x1, x2 + 1)]
        return rectTiles


def startGame(cont = False):
    global player
    player = Player((TILE_SIZE,TILE_SIZE),(0, 0), GREEN, T((TILE_SIZE,TILE_SIZE)), 'mouse')
    global L
    global listfile
    os.chdir(os.getcwd()+"/tiles")
    listfile=[x for x in os.listdir(os.getcwd()) if not os.path.isdir(x)]
    os.chdir(os.getcwd()+"/..")
    global liststring
    liststring=['' for x in range(len(listfile)-1)]
    for co in range(0,len(listfile)):
        leng=len(listfile[co])
        string=listfile[co]
        string_1=' '+string[0:leng-4]
        liststring[co-1]=string_1
    L=[[ '' for i in range(dim)]for j in range(dim_1)]

    return PlayState()

class PlayState:
    
    def __init__(self):
        print 'qui carichero la prima mappa base'
        # must set the player map + position before we create this state
    
        self.viewRect = Rect((0, 0), pg.display.get_surface().get_size())
    
    def execute(self, keyPresses):
        transition = self.getNextTransition(keyPresses)
        self.drawMapView(screen)
        pg.display.flip()
        if transition:
            return transition
        else:
            return None
    
    def getNextTransition(self, keyPresses):
        # have we triggered any events?
        transition = self.handleInput(keyPresses)
        if transition:
            return transition
        else:
            return None

    def handleInput(self, keyPresses):
        action = self.processKeyPresses(keyPresses)
        if action:
            return 1
        else:
            return None
    
    def processKeyPresses(self, keyPresses):
        action = False
        if (keyPresses[K_UP] and player.world_position[1] >0):
            player.world_position=tuple(x+y for x, y in zip(player.world_position, (0,-TILE_SIZE)))
        if (keyPresses[K_DOWN] and player.world_position[1] <17*TILE_SIZE):
            player.world_position=tuple(x+y for x, y in zip(player.world_position, (0,TILE_SIZE)))
        if (keyPresses[K_LEFT] and player.world_position[0] >0):
            player.world_position=tuple(x+y for x, y in zip(player.world_position, (-TILE_SIZE,0)))
        if (keyPresses[K_RIGHT]and player.world_position[0] <17*TILE_SIZE):
            player.world_position=tuple(x+y for x, y in zip(player.world_position, (TILE_SIZE,0)))
        if keyPresses[K_SPACE]:
            action = True
        for i in range(97,122):
            if keyPresses[i]:
                action = True
                j=i-97
                if(j<len(liststring)):
                    L[player.world_position[0]/TILE_SIZE][player.world_position[1]/TILE_SIZE]=liststring[j]
        return action

    def drawMapView(self, surface, increment = 1):
        mp=loadRpgMap('east')
        surface.blit(mp.getMapView(self.viewRect), ORIGIN)

class Map(object):
    
    def __init__(self, config):
        
        self.config = config
        pg.init()
        
        # this is very important. This is how often a key will repeat when held
        # down.
        pg.key.set_repeat(300, 30)
        
        self.status = startGame()
        pg.display.set_caption("Hop-Frog - the escape")
        self.screen = pg.display.set_mode(self.config['WindowSize'])
        self.paint = Mapcreation(self.screen, self.config, self.status)
    
    def launch(self):
        self.paint.run()
        print 'Finishing, drawn map'
        pg.quit()
        print 'Done!'

class Mapcreation(object):
    
    def __init__(self, screen, config, status):
        
        self.screen = screen
        self.config = config
        self.status = status
        self.viewRect = Rect((0, 0), pg.display.get_surface().get_size())
        self.state = 'LocaLmap'
 
    def run(self):
        
        count=0
        for k in range(dim):
            for m in range(dim_1):
                if(m< dim):
                    L[m][k]= ' '+(listfile[1])[0:len(listfile[1])-4]
                else:
                    fl=len(liststring)
                    if(count<fl):
                        count=count+1
                        L[m][k]= liststring[count-1]
                        
        
        # This does not register mouse movement - greatly reduces ressource
        # consumption
        pg.event.set_blocked(pg.MOUSEMOTION)
        # This avoids picking up events when releasing a key
        pg.event.set_blocked(pg.KEYUP)
        
        self.pause_game = False
        
        clock = pg.time.Clock()
        
        out_file = open("east.map","w")
        
        for k in range(dim):
            for m in range(dim_1):
                out_file.write("%d,%d"%(m,k)+str(L[m][k])+"\n")
        out_file.close()

        while True:
            self.screen.fill(WHITE)
            clock.tick(FRAMES_PER_SEC)
            keyPresses = pg.key.get_pressed()
            newState =self.status.execute(keyPresses)
            # wait for player input and perform its action
            self.Draw()
                #for event in pg.event.get():
            event = pg.event.wait()
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
            if newState:
                out_file = open("east.map","w")
                for k in range(dim):
                    for m in range(dim_1):
                        out_file.write("%d,%d"%(m,k)+str(L[m][k])+"\n")
                out_file.close()
                currentState = newState
        return currentState

    @TimeIt
    def Draw(self):
            self.screen.blit(player.image,player.world_position)
            pg.display.update()



if __name__ == '__main__':
    map=Map(config)
    map.launch()