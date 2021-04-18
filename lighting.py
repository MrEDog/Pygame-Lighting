import pygame as pg
from pygame import gfxdraw

import numpy as np
import math, copy, time, random

from shapely.geometry import Polygon, Point

import constants, particles

class RayOrigin(pg.sprite.Sprite):
    def __init__(self, position, color=(0,0,255), antialiasing=False, bloom=False, shadows=True, particles=False):
        """
        Light source that Raycasts.
        
        Parameters
        ----------
        position : tuple
            location of the light source.
        color : pg.Color
            Tint of the lighted area. Default to None.
        """
        
        # Light source, this surface at this time isn't used
        self.image = pg.Surface((20,20)).convert()
        self.image.fill((50,50,255))
        
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        
        # angles to send out rays to
        self.unique_angles = np.array([])
        
        self.color = color
        self.antialiasing = antialiasing
        self.bloom = bloom
        self.colorkey = (0,0,255)
        self.shadows = shadows
        
        self.particles = particles
        
        if particles:
            self.particle_list = np.array([])
        else:
            self.particle_list = None
            
        self.max_particle_count = 100
        
        # init color surface
        if color:
            self.color_surf = pg.Surface((1,1))
            self.color_surf.fill(self.color)
        else:
            self.color_surf = None
        
        self.polygons = []
        self.bloom_surfs = np.array([])
        self.light_surfs = np.array([])
        
        self.particle_color = list(copy.copy(self.color))
        
        # make brighter color for the particles
        for value in range(len(self.particle_color)):
            self.particle_color[value] += 75
            
            if self.particle_color[value] > 255:
                self.particle_color[value] = 255
                
        # add transparency for the particle color
        self.particle_color.append(100)
        
    def screen_size_change(self, screen, world):
        """
        
        Call this every time the screen changes size
        
        Parameters
        ----------
        screen : pygame.Surface
            pygame display
        world : world.World
            The current world

        Returns
        -------
        None.
        """
        self.polygons = []
        
        self.update_location(world)
        self.update(world)
        self.update_light_surf(world)
        
    def update_light_surf(self, world):
        """
        This creates the light and bloom surfaces

        Parameters
        ----------
        world : world.World
            The current world

        Returns
        -------
        None.

        """
        self.light_surfs = np.array([])
        self.bloom_surfs = np.array([])
        
        # to determine the size of each light surface
        lowest_val = None
        highest_val = None
        
        for chunk in world.loaded_chunks:
            if not lowest_val or int(chunk) < lowest_val:
                lowest_val = int(chunk)
            if not highest_val or int(chunk) > highest_val:
                highest_val= int(chunk)
    
        for polygon in self.polygons:                    
            light_surf = pg.Surface(((highest_val+2)*constants.BLOCK_SIZE*constants.CHUNK_SIZE, 800)).convert()
            light_surf.set_alpha(50)
            
            # render the polygon
            # TODO: fix no color with bloom
            if self.shadows:
                light_surf.fill((0,0,0))
                
            if self.antialiasing:
                gfxdraw.aapolygon(light_surf, polygon, self.color)

            gfxdraw.textured_polygon(light_surf, polygon, self.color_surf, 0, 0)
            
            # set up a bloom surf for each main surface
            if self.bloom:
                bloom_surf = copy.copy(light_surf)
                
                start_size = bloom_surf.get_size()
                small_size = (start_size[0]//10, start_size[1]//10)
                
                # Shrink the surface then put it back to the normal size, which blurs it
                bloom_surf = pg.transform.smoothscale(bloom_surf, small_size)
                bloom_surf = pg.transform.smoothscale(bloom_surf, start_size)
                
                light_surf.blit(bloom_surf, (0,0), special_flags=pg.BLEND_RGBA_MULT)
                
            self.light_surfs = np.append(self.light_surfs, light_surf)
        
    def render(self, scroll, screen):
        """
        Renders the lights and particles to the screen

        Parameters
        ----------
        scroll : list
            How much to shift the rendering by
        screen : pygame.Surface
            the main pygame display

        Returns
        -------
        None.

        """
        screen_size = screen.get_size()
        
        # Render the light surface
        for light_surf in self.light_surfs:
            screen.blit(light_surf, (0,0), area=(scroll[0], scroll[1], screen_size[0], screen_size[1]))
        
        # Render particles to the main light surface
        if self.particles:
            for particle in self.particle_list:
                pg.gfxdraw.box(screen, (particle.rect[0]-scroll[0], particle.rect[1]-scroll[1], particle.rect[2], particle.rect[3]), self.particle_color)
          
    def new_light_particle(self):
        """
        Adds a single new light particle if there is space.

        Returns
        -------
        None.

        """
        if self.particles and len(self.particle_list) <= self.max_particle_count:
            particle_pos = []
            
            current_time = time.time()
            
            poly = Polygon(self.polygons[0])
            
            min_x, min_y, max_x, max_y = poly.bounds
            
            # Runs until it gets a position inside the polygon, if it is then it sets the particle position to it.
            while True:
                random_coords = [round(random.uniform(min_x, max_x)), round(random.uniform(min_y, max_y))]
                random_point = Point(random_coords)
                
                if random_point.within(poly):
                    particle_pos = random_coords
                    break
                
            particle_size = [4,4] # size of the particle
            particle_dir = [random.uniform(-2, 2),random.uniform(-2, 2)] # movement direction of it (float)
            particle_decay = 3 # how many seconds the particle stays
            
            particle = particles.Particle(particle_pos, self.color, particle_size, particle_decay, last_decay=current_time, alpha=100, direction=particle_dir)
            
            self.particle_list = np.append(self.particle_list, particle)
        
    def update_particles(self):
        """
        Updates the particles movement and decay.

        Returns
        -------
        None.

        """
        if self.particles:
            current_time = time.time()
            
            self.particle_list = particles.update_particles(self.particle_list, current_time)
            
            # checks to see if there is space, and if so add a particle dependant on the parameters
            count = 0
            while len(self.particle_list) <= self.max_particle_count and count < 1:
                self.new_light_particle()
                count += 1
        
    def update_location(self, world):
        """
        Updates the unique angles, only neccesary to do if the light was moved,
        or if there were blocks loaded.

        Parameters
        ----------
        world : world.World
            The current map            
        """
        
        x, y = self.rect.center
        
        self.unique_angles = np.array([]) # resets the list
        
        
        unique_points = []
        
        for chunk in world.points:
            for point in world.points[chunk]:
                if not point in unique_points:
                    unique_points.append(point)
                    
        for point in unique_points:
            angle = math.atan2(point['y']-y, point['x']-x)
            point['angle'] = angle
            
            # Adds 3 rays per point, to make sure the polygon goes around blocks properly
            for offset in (-0.0001, 0.0, 0.0001):
                if not angle+offset in self.unique_angles:
                    self.unique_angles = np.append(self.unique_angles, angle+offset)
       
    def update(self, world):
        """
        Takes the rays and gets where they intersect the segments listed in world.segments.
        Only needed if the light was moved or if there were blocks loaded.

        Parameters
        ----------
        world : world.World
            The current map.
        """
        
        start_pos = self.rect.center
        
        # sets up the numpy array intersects, structured for sorting later.
        dtype = [('x', 'int'), ('y', 'int'), ('param', 'float'), ('angle', 'float')]
        intersects = np.array([], dtype=dtype)
        
        # Ray casting
        for angle in self.unique_angles:
            dx = math.cos(angle)
            dy = math.sin(angle)
            
            ray = {
                'a': {'x': start_pos[0], 'y': start_pos[1]},
                'b': {'x': start_pos[0] + dx, 'y': start_pos[1]+dy}
            }
        
            closest_intersect = np.array([])
            
            # check if it intersects a segment
            # TODO: only check specific segments?
            for chunk in world.segments:
                for segment in world.segments[chunk]:                    
                    intersect = self.get_intersection(ray, segment)
                
                    # if it's the closest intersect set it as such.
                    if intersect.size > 0 and (not closest_intersect.size > 0 or intersect[2] < closest_intersect[2]):
                        closest_intersect = intersect
            
            # add the closest intersect to the list of intersects.
            if closest_intersect.size > 0 and not closest_intersect in intersects:
                closest_intersect[3] = angle
                closest_intersect = np.array([tuple(closest_intersect)], dtype=dtype)
                intersects = np.append(intersects, closest_intersect)
        
        # Sort the intersects clockwise and add the coordinates to the polygon
        if intersects.size > 0:
            intersects = np.sort(intersects, order='angle')
            
            polygon = []
            
            for intersect in intersects:
                if not [intersect['x'], intersect['y']] in polygon:
                    polygon.append([intersect['x'], intersect['y']])
                    
            self.polygons.append(polygon)

        
    def get_intersection(self, ray, segment):
        """
        Checks if a ray and a segment intersect.

        Parameters
        ----------
        ray : dict
            The ray to cast.
        segment : dict
            The segment to check.

        Returns
        -------
        Numpy Array
            Returns an empty array if it does not intersect, returns x, y, param, 0 if intersects.

        """
        
        # Segment
        s_x = segment['a']['x']
        s_y = segment['a']['y']
        s_dx = segment['b']['x'] - segment['a']['x']
        s_dy = segment['b']['y'] - segment['a']['y']
        
        # Ray
        r_x = ray['a']['x']
        r_y = ray['a']['y']
        r_dx = ray['b']['x'] - ray['a']['x']
        r_dy = ray['b']['y'] - ray['a']['y']
        
        # Slopes
        r_mag = math.sqrt(r_dx*r_dx+r_dy*r_dy)
        s_mag = math.sqrt(s_dx*s_dx+s_dy*s_dy)
        
        # If the segment and ray are parrallel then they will never intersect so exit here
        if r_dx/r_mag == s_dx/s_mag and r_dy/r_mag == s_dy/s_mag:
            return np.array([])
        
        try:
            t2 = (r_dx*(s_y-r_y) + r_dy*(r_x-s_x))/(s_dx*r_dy - s_dy*r_dx)
            t1 = (s_x+s_dx*t2-r_x)/r_dx
        except ZeroDivisionError:
            return np.array([])
        
        if t1 < 0:
            return np.array([])
        
        if t2 < 0 or t2 > 1:
            return np.array([])
        
        # If it reaches here, there was an intersection
        intersection = np.array((
            r_x + r_dx * t1,
            r_y + r_dy * t1,
            t1,
            0.0
        ))

        return intersection
