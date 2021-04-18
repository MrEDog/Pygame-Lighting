from chonk import Map
import init_blocks
import player
import constants

import pygame as pg
import numpy as np

# the entire world
class World:
    def __init__(self, current_map):
        self.loaded_chunks = {}
        
        self.block_list = init_blocks.InitBlocks().block_list
        self.current_map = Map(current_map, self.block_list)
        
        # finds where the player is
        player_coords = constants.string_to_tuple(self.current_map.map["world"]["players"]["player"]["coords"])
        player_chunk = int(self.current_map.map["world"]["players"]["player"]["chunk"])
        
        self.player = player.Player(player_coords[0]*constants.BLOCK_SIZE+(player_chunk*constants.CHUNK_SIZE*constants.BLOCK_SIZE), player_coords[1]*constants.BLOCK_SIZE)
        
        # TODO: all this stuff
        self.sun = self.current_map.map["world"]["sun"]
        self.particles = self.current_map.map["world"]["particles"]
        
        self.lights = []
        
        self.render_queue = {}
        
        screen_rect = pg.display.get_surface().get_rect()
        
        self.left_chunk = None
        self.right_chunk = None
        
        self.segments = {}
        self.points = {}
        
        # loads a few starter chunks around the player
        # TODO: auto load chunks as the player moves around
        for x in range(player_chunk-1, player_chunk+2):
            self.load_chunk(x)
            
            if not self.left_chunk or x < self.left_chunk:
                self.left_chunk = x
                
            if not self.right_chunk or x > self.right_chunk:
                self.right_chunk = x
        
        self.update_surf_polygon()            
        self.update_render_queue()
        
    def update_surf_polygon(self):
        
        """
        if self.left_chunk:
            left = self.left_chunk * constants.CHUNK_SIZE  
        else:
            left = 0
            
        if self.right_chunk:
            right = self.right_chunk * constants.CHUNK_SIZE
        else:
            right = 0
        
        
        top = 0
        bottom = 1000
        """
        
        screen = pg.display.get_surface().get_rect()
        left = -500
        right = 1000+screen.right
        top = -500
        bottom = 1000+screen.bottom
        
        self.segments['screen'] = [
            {'a': {'x':  left, 'y': top}, 'b': {'x':  right, 'y': top}},
            {'a': {'x':  right, 'y': top}, 'b': {'x':  right, 'y': bottom}},
            {'a': {'x':  right, 'y': bottom}, 'b': {'x':  left, 'y': bottom}},
            {'a': {'x':  left, 'y': bottom}, 'b': {'x':  left, 'y': top}}
        ]
        
        self.points['screen'] = [
            {'x': left, 'y': top, 'angle': None},
            {'x': right, 'y': top, 'angle': None},
            {'x': left, 'y': bottom, 'angle': None},
            {'x': right, 'y': bottom, 'angle': None}            
        ]
    
    def load_chunk(self, coord):
        chunk = self.current_map.load_chunk(self, coord)
        
        if chunk:
            self.loaded_chunks[coord] = chunk
    def get_chunk(self, coords):
        chunk = self.loaded_chunks[coords]
        return chunk
    
    def move_player(self, key):
        self.player.move_player(key)
        
    def update_render_queue(self):
        self.render_queue = {}
    
        # get the render queue of each chunk, then add them to the parent render_queue, not by chunk
        # but by layer so everything is rendered in the correct order
        for chunk in self.loaded_chunks:
            chunk_queue = self.loaded_chunks[chunk].render_queue()     
            for layer in chunk_queue:
                if not layer in self.render_queue:
                    self.render_queue[layer] = {}
            
                for tile in chunk_queue[layer]:
                    self.render_queue[layer][tile] = chunk_queue[layer][tile]
            
