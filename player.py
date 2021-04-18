import pygame as pg
import mob, constants
import os, copy

class Player(mob.Mob): # TODO: player states, animations, etc.
    def __init__(self, x, y, images=None, layer=0):
        self.layer = layer
        self.current_image = pg.image.load(os.path.join(os.path.dirname(__file__), "resources/images/blocks/" + "player" + ".png")).convert()
        
        self.rect = self.current_image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.jumps = 0
        
        super().__init__(self.rect, x, y, images)
    
    # updates the player's move variable when a key is pressed
    def move_player(self, event): # TODO: changeable controls, use the last pressed key for movement
        key = event.key
        
        if event.type == pg.KEYDOWN:
            if key == pg.K_w: # jump
                if self.jumps < constants.PLAYER_MAX_JUMPS:
                    self.move[1] = -constants.PLAYER_JUMP
                    self.jumps += 1
                    self.gravity_modifier = 0
                    
            elif key == pg.K_s: # ignore unless testing, moves down
                self.move[1] = constants.PLAYER_SPEED
                
            if key == pg.K_d: # move right
                self.move[0] = constants.PLAYER_SPEED
            elif key == pg.K_a: # move left
                self.move[0] = -constants.PLAYER_SPEED
        else:
            if key == pg.K_w or key == pg.K_s:
                self.move[1] = 0
            elif key == pg.K_d or key == pg.K_a:
                self.move[0] = 0
                
    def update(self, loaded_chunks):
        self.update_collisions(loaded_chunks)
        
        # applies gravity
        self.move[1] += self.gravity_modifier
        self.gravity_modifier += constants.GRAVITY
        
        # makes sure gravity isn't too strong
        if self.move[1] > constants.MAX_GRAV:
            self.move[1] = constants.MAX_GRAV
        
        # X move, moves 1 pixel at a time checking collisions each pixel to make sure collisions
        # don't go wack
        
        #x_move = copy.deepcopy(self.move[0]) * constants.dt
        #y_move = copy.deepcopy(self.move[1]) * constants.dt
        
        for x in range(abs(round(self.move[0]))):
            self.update_collisions(loaded_chunks)
                
            if self.move[0] == 0:
                break
            
            # moves player
            if self.move[0] > 0:
                self.x += 1
            else:
                self.x -= 1
        
        # same as above but for y
        for y in range(abs(round(self.move[1]))):
            self.update_collisions(loaded_chunks)
                
            if self.move[1] == 0:
                break
            
            # moves player
            if self.move[1] > 0:
                self.y += 1
            else:
                self.y -= 1
        
        self.update_rects()
    
    # sets the move variable to zero if there is a collision in the way,
    # also only does so if the player is trying to move in that direction
    def update_collisions(self, loaded_chunks):
        self.update_rects()
        collisions = self.check_collisions(loaded_chunks)
            
        if "left" in collisions and self.move[0] < 0:
            self.move[0] = 0
                
        if "right" in collisions and self.move[0] > 0:
            self.move[0] = 0
            
        if "up" in collisions and self.move[1] < 0:
            self.move[1] = 0
                
        if "down" in collisions:
            if self.move[1] > 0:
                self.move[1] = 0
            self.gravity_modifier = 0
            self.jumps = 0
            
        return collisions
