import pygame as pg
import gameobject
import os
import copy

class Block(gameobject.GameObject):
    def __init__(self, name, solid=True, images=None, light_level=False, translucent=False):
        super().__init__(None, None, images)
        
        self.solid = solid
        self.light_level = light_level
        self.translucent = translucent
        self.images = images
        self.current_image = None
        self.name = name
        
        # if no animation, TODO: animations
        if not self.images:
            self.current_image = pg.image.load(os.path.join(os.path.dirname(__file__), "resources/images/blocks/" + name + ".png")).convert()
            
        # get rect from the image
        self.rect = self.current_image.get_rect()
        
    # Copy a block
    def copy(self):
        copyobj = Block(self.name)
        
        # copies attributes
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj
