import json
import constants
import numpy as np

# Each coordinate in a chunk is a tile, each tile has a layer, the layer used for collisions
# and the same layer as the player is 0
class Tile:
    def __init__(self, tile, coords, chunk_coord, block_list):        
        self.tile = {}
        self.coords = constants.string_to_tuple(coords)
        self.chunk_coord = chunk_coord
        
        # set up each block based on layers
        for layer in tile:
            new_block = block_list[tile[layer]].copy()
            new_block.x = self.coords[0]
            new_block.y = self.coords[1]
            
            new_block.rect.x = constants.COORD_TO_PIX(new_block.x + (constants.CHUNK_SIZE * self.chunk_coord))
            new_block.rect.y = constants.COORD_TO_PIX(new_block.y)
            
            self.tile[str(layer)] = new_block

# the entire map
class Map:
    def __init__(self, map_name, block_list):
        self.map_file = 'resources/maps/' + map_name + '.json'
        self.block_list = block_list
        
        # loads the map file
        with open(self.map_file) as f:
            self.map = json.load(f)
    
    # loads a chunk if it exists
    def load_chunk(self, world, coord):
        string_coord = str(coord)
        if string_coord in self.map:
            chunk = Chunk(coord)
            
            # loads the tiles for each chunk
            for tile_coords in self.map[string_coord]:
                new_tile = Tile(self.map[string_coord][tile_coords], tile_coords, coord, self.block_list)
                chunk.add_tile(new_tile, world, tile_coords)
        
            return chunk
        return None
    
    # TODO: unload a chunk
    def unload_chunk(self, coords):
        self.loaded_chunks.pop(constants.string_to_tuple(coords))
    
# each individual chunk, the size is default to a number determined in constants 
class Chunk:
    def __init__(self, coord, width=constants.CHUNK_SIZE):
        self.tiles = {}
        self.coord = coord
        self.width = width
        self.all = {}
    
    def add_tile(self, tile, world, coords):
        self.tiles[coords] = tile.tile
        
        for layer in tile.tile:          
            block = tile.tile[layer]
                
            if not self.coord in world.segments:
                world.segments[self.coord] = []
                
            if not self.coord in world.points:
                world.points[self.coord] = []
            
            if layer == '0':
                segments = world.segments[self.coord]
                points = world.points[self.coord]
                
                segments.append({'a': {"x": block.rect.left, 'y': block.rect.top}, 'b': {"x": block.rect.right, "y": block.rect.top}})
                segments.append({'a': {"x": block.rect.right, 'y': block.rect.top}, 'b': {"x": block.rect.right, "y": block.rect.bottom}})
                segments.append({'a': {"x": block.rect.right, 'y': block.rect.bottom}, 'b': {"x": block.rect.left, "y": block.rect.bottom}})
                segments.append({'a': {"x": block.rect.left, 'y': block.rect.bottom}, 'b': {"x": block.rect.left, "y": block.rect.top}})
                
                points.append({'x': block.rect.left, 'y': block.rect.top, 'angle': None})
                points.append({'x': block.rect.right, 'y': block.rect.top, 'angle': None})
                points.append({'x': block.rect.left, 'y': block.rect.bottom, 'angle': None})
                points.append({'x': block.rect.right, 'y': block.rect.bottom, 'angle': None})
                
                #print(world.segments[self.coord])
                #print(segments)

            
        
        
    def get_tiles(self, coords):
        return self.tiles[coords]  
    
    # returns a dictionary seperated by layers of what to render
    # TODO: entity rendering
    def render_queue(self):
        render_queue = {}
        for tile in self.tiles:
            for layer in self.tiles[tile]:
                if not layer in render_queue:
                    render_queue[layer] = {}
                
                to_render = self.tiles[tile][layer]
                render_x = constants.COORD_TO_PIX(to_render.x + (self.coord * self.width))
                render_y = constants.COORD_TO_PIX(to_render.y)
                to_render_coords = (to_render.x, to_render.y)
                
                # dictionary for each tile in the layer
                render_queue[layer][to_render_coords]  = {
                        'x': render_x,
                        'y': render_y,
                        'render': to_render
                    }
                
        return render_queue
