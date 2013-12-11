import sys
import re
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
{   'WindowSize': T((648, 648)),
    'VELOCITY_BEET': 18,
    'VELOCITY_PLAYER': 6
}


VELOCITY = 2

FRAMES_PER_SEC = 60//VELOCITY

WHITE = 255,255,255
RED = 255, 0, 0
BLUE = 0, 0, 255
BLACK = 0, 0, 0
GREEN = 0, 255, 0

NONE = 0
UP = 1
DOWN = 2
LEFT = 4
RIGHT = 8

SCALAR = 1

TILE_SIZE = 36
COMMA = ","

VIEW_WIDTH = TILE_SIZE * 18
VIEW_HEIGHT = TILE_SIZE * 18
DIMENSIONS = (VIEW_WIDTH, VIEW_HEIGHT)
TRANSPARENT_COLOUR = GREEN
ORIGIN = (0, 0)

screen = pg.display.set_mode(DIMENSIONS)

DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

####### List of tiles from metadata

class TileSet:
    
    def __init__(self, tiles,access_set):
        self.tiles = tiles
        self.access_set = access_set
    
    
    def getTile(self, name):
        if name in self.tiles:
            return self.tiles[name]
        return None

    def getTileAccess(self, name):
        if name in self.tiles:
            return self.access_set[name]
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
    return scale(img, (TILE_SIZE*scalar, TILE_SIZE*scalar))

def getXY(xyStr, delimiter = COMMA):
    return [int(n) for n in xyStr.split(delimiter)]

def createRectangle(dimensions, colour = None):
    rectangle = pg.Surface(dimensions).convert()
    if colour is not None:
        rectangle.fill(colour)
    return rectangle

class Entity(pg.sprite.Sprite):
    """A class that manage the Graphical interface for Characters (Player or Beetles)"""
    
    def __init__(self, position, color, size=TILE_SIZE):
        
        pg.sprite.Sprite.__init__(self)
        
        self.position = position
        self.color = color
        self.size = size
        
        # grid-position wrt. to the map that holds it

class Character(Entity):
    """A class for defining the main parameter for Player and Beetle Monster"""
    
    def __init__(self, world_position, position, color, size, name,life=3):
        
        self.world_position = world_position
        Entity.__init__(self, position, color, size)
        self.name = name
        self.life = life
    

class Player(Character):
    """A class for the Player: it's just a copy of Character Class plus a method to Control the Player Movement and the Attack"""
    def HandleMovement(self,keyPresses,map_tiles):
        """Method for control the movement of the Player through the keys -UP-DOWN-LEFT-RIGHT-"""
        images = ["mouse_up.png","mouse_down.png","mouse_left.png","mouse_right.png"]
        index_dir = [1,1,0,0]
        tile_limit = [0,TILE_SIZE*17,0,TILE_SIZE*17]
        prev_pos=self.world_position
        presses=[keyPresses[K_UP],keyPresses[K_DOWN],keyPresses[K_LEFT],keyPresses[K_RIGHT]]
        coor = [self.world_position[0]/TILE_SIZE,self.world_position[1]/TILE_SIZE]
        res = [self.world_position[0]%TILE_SIZE,self.world_position[1]%TILE_SIZE]
        map_mov_x = [0,0,-1,1]
        map_mov_y = [-1,1,0,0]
        poss_dir =[1,1,1,1]
        porcata=[self.world_position[1] >=0, self.world_position[1] <17*TILE_SIZE, self.world_position[0] >=0, self.world_position[0] <17*TILE_SIZE]
        player_step_full = [(0,-TILE_SIZE/config['VELOCITY_PLAYER']),(0,TILE_SIZE/config['VELOCITY_PLAYER']),(-config['VELOCITY_PLAYER'],0),(TILE_SIZE/config['VELOCITY_PLAYER'],0)]
        player_step_x = [(0,0),(0,0),(-TILE_SIZE/config['VELOCITY_PLAYER'],0),(TILE_SIZE/config['VELOCITY_PLAYER'],0)]
        player_step_y = [(0,-TILE_SIZE/config['VELOCITY_PLAYER']),(0,TILE_SIZE/config['VELOCITY_PLAYER']),(0,0),(0,0)]
        
        for i_index,i_el in enumerate(presses):
            
            if(i_el):
                
                for cn_in in range(len(mov)):
                    if cn_in != i_index:
                        mov[cn_in]=0
                    else:
                        mov[cn_in] = mov[cn_in]+1
                
                
                self.position=self.world_position
                self.color=images[i_index]
                self.size=T((TILE_SIZE,TILE_SIZE))
                next_x = coor[0]+map_mov_x[i_index]
                next_y = coor[1]+map_mov_y[i_index]
                
                player_step = player_step_full
                if(next_x>=0 and next_x<=17 and next_y >=0 and next_y <=17):
                    intelligence = (map_tiles[next_x][next_y]).access
                else:
                    intelligence=0
                if(res[0] != 0):
                    y_control=0
                    if(i_index==1 or res[1]==0 ):
                        y_control=next_y
                    else:
                        y_control=coor[1]
                    
                    
                    if((map_tiles[int(coor[0])][y_control]).access==0 or (map_tiles[int(coor[0])+1][y_control]).access==0):
                        player_step = player_step_x
                        if(next_x>=0 and next_x<=17 and y_control >=0 and y_control <=17):
                            intelligence = 1
                    else:
                        player_step = player_step_full
                        if(y_control >=0 and y_control <=17):
                            intelligence = 1
                
                if(res[1] != 0):
                    x_control=0
                    if(i_index==3 or res[0]==0):
                        x_control=next_x
                    else:
                        x_control=coor[0]
                    if((map_tiles[x_control][int(coor[1])]).access==0 or (map_tiles[x_control][int(coor[1])+1]).access==0):
                        player_step = player_step_y
                        if(x_control>=0 and x_control<=17 and next_y >=0 and next_y <=17):
                            intelligence = 1
                    else:
                        player_step = player_step_full
                        if(x_control>=0 and next_x<=17):
                            intelligence = 1
                
                if(mov[i_index]>1 and porcata[i_index]and intelligence>0):
                    self.world_position=tuple(x+y for x, y in zip(self.world_position, player_step[i_index]))
                    self.position=self.world_position
        
        
        
        return prev_pos

    def Attack(self,keyPresses,beetle):
        """Method to control the Attack action of the Player with the key -SPACE-"""
        if keyPresses[K_SPACE]:
            action = True
            if(mov[3]>0):
                self.color="mouse_right_sword.png"
                self.size=T((2*TILE_SIZE,TILE_SIZE))
                for i in range(number_beetles):
                    if(beetle[i].position[1]==self.position[1] and (beetle[i].position[0] in range(self.position[0],self.position[0]+TILE_SIZE))):
                        beetle[i].position=(-1000,-1000)
            if(mov[2]>0):
                self.color="mouse_left_sword.png"
                self.size=T((2*TILE_SIZE,TILE_SIZE))
                self.position =tuple(x+y for x, y in zip(self.world_position, (-TILE_SIZE,0)))
                for i in range(number_beetles):
                    if(beetle[i].position[1]==self.position[1] and (beetle[i].position[0] in range(self.position[0],self.position[0]+TILE_SIZE))):
                        beetle[i].position=(-1000,-1000)
                            
            if(mov[0]>0):
                self.color="mouse_up_sword.png"
                self.size=T((TILE_SIZE,TILE_SIZE))
                for i in range(number_beetles):
                    if(beetle[i].position[0]==self.position[0] and (beetle[i].position[1] in range(self.position[1]-TILE_SIZE,self.position[1]))):
                        beetle[i].position=(-1000,-1000)
                            
            if(mov[1]>0):
                self.color="mouse_down_sword.png"
                self.size=T((TILE_SIZE,TILE_SIZE))
                for i in range(number_beetles):
                    if(beetle[i].position[0]==self.position[0] and (beetle[i].position[1] in range(self.position[1]+TILE_SIZE,self.position[1]+2*TILE_SIZE))):
                        beetle[i].position=(-1000,-1000)
    
    def LifeManager(self,beetle,playstate):
        """Method that handles the Life of the Player and the animation when he get dangered by the Beetles"""
        images_star = ["mouse_up_star.png","mouse_down_star.png","mouse_left_star.png","mouse_right_star.png"]
    
        life_index = 1
        for i in range(number_beetles):
            p_x = player.world_position[0]
            p_y = player.world_position[1]
            b_x = beetle[i].position[0]
            b_y = beetle[i].position[1]
            if(np.sqrt(np.power(p_x-b_x,2)+np.power(p_y-b_y,2))<TILE_SIZE):
                elapsed_time = time.time()-playstate.start_time
                playstate.start_time = time.time()
                if(elapsed_time>0.5):
                    player.life = player.life-1
                    life_index = 0
                    for i_color,index_color in enumerate(images_star):
                        print self.color[:8]
                        m = re.search(self.color[:8], images_star[i_color])
                        if(re.search(self.color[:8],images_star[2])):
                            self.position=self.world_position
                        if m:
                            self.size = T((TILE_SIZE,TILE_SIZE))
                            self.color = images_star[i_color]
        #print self.color
    
        if(life_index==0):
            print life_index
        return life_index

    pass

class Beetle(Character):
    """A class for the Beetle Monsters: it's a copy of the Class Character plus the function for the automatization of Beetle movements"""
    def MoveBeet(self,playstate):
        """Method of Beetle class which define the intelligence of Beetles, remember they are Beetles not Einstein"""
        beetle_color_vect=["beetle_right.png","beetle_left.png","beetle_up.png","beetle_down.png"]
        beetle_color_logic=[0,1,2,3]
        beetle_inc_pos=[(TILE_SIZE/config['VELOCITY_BEET'],0),(-TILE_SIZE/config['VELOCITY_BEET'],0),(0,-TILE_SIZE/config['VELOCITY_BEET']),(0,TILE_SIZE/config['VELOCITY_BEET'])]
        next_tile_step=[(1,0),(-1,0),(0,-1),(0,1)]
        limits=[17,0,0,17]
        suppress=[1,0,3,2]
        index=0
        index_1=-1
        index=self.color

        if((self.position[0]%TILE_SIZE)==0 and (self.position[1]%TILE_SIZE)==0):
            
            availabledir = self.CheckAvailability(playstate.mp.mapTiles, next_tile_step)
            

            numdir = np.sum(availabledir)

            incoming_position=-1


            for e in range(len(availabledir)):
                if(self.color==beetle_color_logic[e]):
                    incoming_position=suppress[e]
            dir = -1

            if(numdir==1):
                dir = incoming_position

            elif(numdir==2):
                for e,i in enumerate(availabledir):
                    if(e!=incoming_position and i==1):
                        dir=e

            elif(numdir>2):
                L=[0]
                f=0
                for e,i in enumerate(availabledir):
                    if(e!=incoming_position and i==1):
                        if(f==0):
                            L[f]=e
                        else:
                            L.append(e)
                        f=f+1
                dir = L[rd.randint(0,numdir-2)]

            ics_new=(self.position[0]/TILE_SIZE)+next_tile_step[dir][0]
            ipsilon_new=self.position[1]/TILE_SIZE+next_tile_step[dir][1]

            self.position=tuple(x+y for x, y in zip(self.position, beetle_inc_pos[dir]))
            self.color=beetle_color_logic[dir]
    
        else:
            self.position=tuple(x+y for x, y in zip(self.position, beetle_inc_pos[index]))
            self.color=beetle_color_logic[index]

    def CheckAvailability(self, map,nextstep):
        """Check the availability of the tiles around the beetle"""
        availabledirection=[1,1,1,1]
        for i in range(len(availabledirection)):
            if(self.position[0]/TILE_SIZE+nextstep[i][0]>17 or self.position[0]/TILE_SIZE+nextstep[i][0]<0 or self.position[1]/TILE_SIZE+nextstep[i][1]>17 or self.position[1]/TILE_SIZE+nextstep[i][1]<0):
                availabledirection[i]=0
        for i in range(len(availabledirection)):
            if(availabledirection[i]!=0):
                if(map[self.position[0]/TILE_SIZE+nextstep[i][0]][self.position[1]/TILE_SIZE+nextstep[i][1]].access!=1):
                    availabledirection[i]=0
        return availabledirection

    pass


class MapTile:
    """A Class that define the Tile of the map"""
    def __init__(self, x, y):
        """Inizialization of a single Tile"""
        self.x, self.y = x, y
        self.levels = []
        self.tiles = []
        self.originalLevels = None
        self.specialLevels = None
        self.downLevels = None
        self.masks = None
        self.events = None
        self.access = None
        
    
    def addTile(self, tile):
        """superimpose the tile"""
        self.tiles.append(tile)
        
    def createTileImage(self):
        """Method for creation of the image of the Tile"""
        if len(self.tiles) == 0:
            return None
        elif len(self.tiles) > 1:
            # if we're layering more than one image we don't want to draw on any of
            # the original images because that will affect every copy
            tileImage = view.createRectangle((TILE_SIZE, TILE_SIZE), view.TRANSPARENT_COLOUR)
            for image in self.tiles:
                tileImage.blit(image, (0, 0))
            return tileImage
    
        return self.tiles[0]



def loadRpgMap(name):
    """A method that load the RpgMap from a .map file stored into the same directory"""
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
    """Method a matrix of MapTile related to the map"""
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
                mapTile.access = tileSet.getTileAccess(tileName)

                
    return mapTiles


######### loadTileSet: it surfs through the metadata and provide the TileSet (all the tiles images related to a key name)

def loadTileSet(name):
    # print "load tileset: %s" % (name)
    # tileSet = map.TileSet()
    tiles = {}
    access_set ={}
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
                    x, y, A = tilePoint.split(COMMA)
                    px, py = int(x) * TILE_SIZE, int(y) * TILE_SIZE
                    tileRect = Rect(px, py, TILE_SIZE, TILE_SIZE)
                    tileImage = tilesImage.subsurface(tileRect).copy()
                    tiles[tileName] = tileImage
                    access_set[tileName] = int(A)
            # self.maskTiles[tileName] = view.createMaskTile(tileImage)
            except ValueError:
                pass
    # create tile set and return
    return TileSet(tiles,access_set)


class RpgMap:
    """A Class to handle the map of the game"""
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



def startGame(cont = False):
    global mov
    mov=[0,0,0,0]
    global world_pos
    global listfile
    
    global number_beetles
    number_beetles=rd.randint(2,10)
    
    global beet_pos
    beet_pos=[0 for i in range (number_beetles)]
    
    playstate=PlayState()
    x_pl=0
    y_pl=0
    cunt=0
    for x,i in enumerate(playstate.mp.mapTiles):
        for y,j in enumerate(i):
            if (j.access==1):
                x_pl=x
                y_pl=y
                world_pos=T((x*TILE_SIZE,y*TILE_SIZE))
                cunt=1
                break
        if cunt==1:
            break

    for i in range(number_beetles):
        while True:
            icsi= rd.randint(0,len(playstate.mp.mapTiles)-1)
            ipsilonne=rd.randint(0,len(playstate.mp.mapTiles[0])-1)
            if (icsi!= x_pl and ipsilonne!= y_pl and playstate.mp.mapTiles[icsi][ipsilonne].access==1):
                beet_pos[i]= (icsi*TILE_SIZE, ipsilonne*TILE_SIZE)
                break

    global beetle
    beetle = [Beetle(beet_pos[i],beet_pos[i], 0, T((TILE_SIZE,TILE_SIZE)), 'bee beetle') for i in range (number_beetles)]

    global player
    player = Player(world_pos,world_pos, "mouse_down.png", T((TILE_SIZE,TILE_SIZE)), 'hop_frog')


    return playstate

class PlayState():
    """A class that manage the key presses and related them to action of the Player and Beetles"""
    
    
    def __init__(self):
        self.mp =loadRpgMap('east_piace')
        # must set the player map + position before we create this state
        self.start_time = time.time()
        self.viewRect = Rect((0, 0), pg.display.get_surface().get_size())
        self.index_life = 1
    
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
        """This method reacts to the key that you press and takes action based on this key event"""
        action = False
        map_tiles = self.mp.mapTiles
        previous_position= player.HandleMovement(keyPresses,map_tiles)
        player.Attack(keyPresses,beetle)
        

        for i in range(97,122):
            if keyPresses[i]:
                action = True
                j=i-97
        min_x=0
        min_y=0
        max_x=0
        max_y=0
        if previous_position[0]>player.world_position[0]:
            min_x=player.world_position[0]
            max_x=previous_position[0]
        else:
            max_x=player.world_position[0]
            min_x=previous_position[0]
        if previous_position[1]>player.world_position[1]:
            min_y=player.world_position[1]
            max_y=previous_position[1]
        else:
            max_y=player.world_position[1]
            min_y=previous_position[1]
        
        self.index_life = player.LifeManager(beetle,self)
        return action

    def drawMapView(self, surface, increment = 1):
        beetle_color_vect=["beetle_right.png","beetle_left.png","beetle_up.png","beetle_down.png"]
        life_imm=["./start_end/life_empty.png","./start_end/life_last.png","./start_end/life_mid.png","./start_end/life_full.png"]
        surface.blit(self.mp.getMapView(self.viewRect), ORIGIN)
        
        for i in range(number_beetles):
            imagePath_2=os.path.join("sprites", beetle_color_vect[beetle[i].color])
            img_2=pg.image.load(imagePath_2)
            image_2=scale(img_2, beetle[i].size)
            image_2.convert()
            surface.blit(image_2,beetle[i].position)
    
        imagePath = os.path.join("sprites", player.color)
        img = pg.image.load(imagePath)
        image=scale(img, player.size)
        image.convert()
                #surface.blit(image,player.position)
            #if(self.index_life>0):
        surface.blit(image,player.position)
            #else:
                #print 'todo: add image of damage'
            
        image_life = pg.image.load(life_imm[player.life])
        image_life.convert()
        surface.blit(image_life, ORIGIN)
#pg.display.flip()


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
    """A Class that take care of creating the map display and of printing it onto the screen"""
    def __init__(self, screen, config, status):
        
        self.screen = screen
        self.config = config
        self.status = status
        self.viewRect = Rect((0, 0), pg.display.get_surface().get_size())
        self.state = 'LocaLmap'
 
    def run(self):
        
        # This does not register mouse movement - greatly reduces ressource
        # consumption
        pg.event.set_blocked(pg.MOUSEMOTION)
        # This avoids picking up events when releasing a key
        pg.event.set_blocked(pg.KEYUP)
        
        self.pause_game = False
        
        clock = pg.time.Clock()
        imm= "./start_end/end.png"
        
        while True:
            self.screen.fill(WHITE)
            clock.tick(FRAMES_PER_SEC)
            keyPresses = pg.key.get_pressed()
            self.viewRect = Rect((0, 0), pg.display.get_surface().get_size())
            image = pg.image.load("./start_end/start.png")
            self.screen.blit(image, ORIGIN)
            pg.display.flip()
            event = pg.event.wait()
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
            if event.key == K_RETURN:
                break
    
        while True:
            self.screen.fill(WHITE)
            clock.tick(FRAMES_PER_SEC)
            keyPresses = pg.key.get_pressed()
            self.status.execute(keyPresses)
            playstate=PlayState()

            for i in range(number_beetles):
                beetle[i].MoveBeet(playstate)

            for event in pg.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return
            if (playstate.mp.mapTiles[player.world_position[0]/TILE_SIZE][player.world_position[1]/TILE_SIZE].access == 2):
                imm="./start_end/end.png"
                break
            if (player.life<=0):
                imm="./start_end/dead.png"
                break
    
        while True:
            self.screen.fill(WHITE)
            clock.tick(FRAMES_PER_SEC)
            self.viewRect = Rect((0, 0), pg.display.get_surface().get_size())
            image = pg.image.load(imm)
            self.screen.blit(image, ORIGIN)
            pg.display.flip()
            event = pg.event.wait()
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return




if __name__ == '__main__':
    map=Map(config)
    map.launch()

