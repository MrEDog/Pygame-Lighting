import pygame as pg
import block

# create a block list from which things can be copied from
# TODO: change to init_objects and include items, or do seperate class idk
class InitBlocks:
    def __init__(self):
        self.block_list = {}
        
        self.block_list["dirt"] = block.Block("dirt")
        self.block_list["grass"] = block.Block("grass")
        self.block_list["sand"] = block.Block("sand")
