import pygame as pg
import gameobject
import constants

# Basic physics entity class, no AI.
# has collisions and gravity, both can be turned off.
# You can also ignore collisions and gravity and just turn on/off physics
# which if the latter two are ignored will change them as well.
class Entity(gameobject.GameObject):
    def __init__(self, rect, x, y, images=None, physics=True, collisions=None, gravity=None):
        super().__init__(x, y)
        self.move = [0,0]
        self.rect = rect
        
        self.gravity = gravity
        self.physics = physics
        self.collisions = collisions
        
        self.collide_rects = {}
        
        self.gravity_modifier = 0
        
        self.images = images
        
        # change latter 2 perameters if they don't exist
        if not gravity:
            if physics == True:
                self.gravity = True
            else:
                self.gravity = False
                
        if not collisions:
            if physics == True:
                self.collisions = True
            else:
                self.collisions = False
        
        
        # set up collision boxes
        if self.collisions:
            self.collide_rects["left"] = pg.Rect((self.rect.left-1, self.rect.top), (1, self.rect.height))
            self.collide_rects["right"] = pg.Rect((self.rect.right, self.rect.top), (1, self.rect.height))
            self.collide_rects["up"] = pg.Rect((self.rect.left, self.rect.top-1), (self.rect.width, 1))
            self.collide_rects["down"] = pg.Rect((self.rect.left, self.rect.bottom), (self.rect.width, 1))
    
    # Updates the collision rectangles
    # also updates the position of the entity
    def update_rects(self):
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)
        
        # update the x coordinate of all the collision rects
        self.collide_rects["left"].x = self.rect.left-1
        self.collide_rects["right"].x = self.rect.right
        self.collide_rects["up"].x = self.rect.left
        self.collide_rects["down"].x = self.rect.left
        
        # update the y coordinate of all the collision rects
        self.collide_rects["left"].y = self.rect.top
        self.collide_rects["right"].y = self.rect.top
        self.collide_rects["up"].y = self.rect.top - 1
        self.collide_rects["down"].y = self.rect.bottom
    
    # Finds which blocks to check around the player (5x5 centered on the player)
    # then see which (if any) of the collision rectangles intersect with them
    # TODO: optimize
    def check_collisions(self, loaded_chunks):
        # blocks to be checked for collisions
        to_collide = {}
        
        # coordinates of the player
        coords = [(self.x+(constants.BLOCK_SIZE//2))//constants.BLOCK_SIZE, (self.y+(constants.BLOCK_SIZE//2))//constants.BLOCK_SIZE]
        
        # figure out which blocks to be checked for collisions
        for x in range(coords[0] - 1, coords[0] + 2):
            for y in range(coords[1] - 1, coords[1] + 2):
                chunk = x//constants.CHUNK_SIZE # which chunk the entity is in
                chunk_coords = [x%constants.CHUNK_SIZE, y] # where in the chunk it is
                
                # update the x coord if it's out of range of the chunk
                if chunk_coords[0] >= constants.CHUNK_SIZE:
                    chunk += 1
                    chunk_coords[0] -= constants.CHUNK_SIZE
                elif chunk_coords[0] < 0:
                    chunk -= 1
                    chunk_coords[0] += constants.CHUNK_SIZE
                
                chunk_coords = constants.tuple_to_string(chunk_coords)
                
                # if the chunk is loaded and the tile exists, and if the tile is solid,
                # add it to the list of blocks to check for collisions
                if chunk in loaded_chunks:
                    if chunk_coords in loaded_chunks[chunk].tiles:
                        if '0' in loaded_chunks[chunk].tiles[chunk_coords]:
                            if loaded_chunks[chunk].tiles[chunk_coords]['0'].solid == True:
                                to_collide[(x, y)] = loaded_chunks[chunk].tiles[chunk_coords]['0'].rect 
        
        return self.get_collisions(to_collide)
