import pygame as pg
import numpy as np

import gameobject
                
class Particle(gameobject.GameObject):
    def __init__(self, position, color, size, decay, last_decay=0, decay_stages=0, alpha=None, direction=None, shape='rect'):
        super().__init__(position[0], position[1])
        
        self.color = color
        self.decay = decay
        self.alpha = alpha
        self.direction = direction
        self.shape = shape
        
        self.last_decay = last_decay
        self.decay_stages = decay_stages
     
        if shape == 'rect':
            self.rect = np.array([position[0], position[1], size[0], size[1]])
            
    def move_particle(self):
        # x and y are floats
        self.x += self.direction[0]
        self.y += self.direction[1]
        
        # round the pixel value so it dosen't crash
        self.rect[0] = round(self.x)
        self.rect[1] = round(self.y)
        
        return self
        
    def decay(self, current_time):
        dt = current_time - self.last_decay
        
        if dt >= self.decay:            
            if self.decay_stages <= 0:
                return None
            else:
                self.last_decay = current_time
                self.decay_stages -= 1
                
        return self
    
vec = np.vectorize(Particle.move_particle, otypes=[Particle])
vec2 = np.vectorize(Particle.decay, otypes=[Particle])

def update_particles(particle_list, current_time):    
    particle_list = vec(particle_list)
    particle_list = vec2(particle_list, current_time)
    
    particle_list = particle_list[particle_list != None]
    
    return particle_list
