import pygame as pg
import constants, settings
import world, lighting
import sys, time

import cProfile, pstats, io
from pstats import SortKey

profile = False

if profile:
    pr = cProfile.Profile()
    pr.enable()

map_to_load = 'test_map' # TODO: add map picking system

#flags = pg.SCALED | pg.RESIZABLE
flags = pg.RESIZABLE
screen = pg.display.set_mode((settings.SCREEN_WIDTH,settings.SCREEN_HEIGHT), flags)

true_scroll = [0,0] # render offset so everything is around the player

shadows = False
lights = []

check_fps = 0

day_time = 'day'

def main():
    global check_fps
    
    current_map = init()
    
    screen_size = screen.get_size()
    last_time = time.time()
    last_update = time.time()
    
    for light in current_map.lights:
        light.screen_size_change(screen, current_map)
        light.new_light_particle()
    
    while True:        
        current_time = time.time()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if profile:
                    pr.disable()
                    s = io.StringIO()
                    sortby = SortKey.CUMULATIVE
                    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
                    ps.print_stats()
                    print(s.getvalue())

                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                current_map.move_player(event)
        
        if screen.get_size() != screen_size:
            screen_size = screen.get_size()
            
            current_map.update_surf_polygon()
            
            for light in current_map.lights:
                light.screen_size_change(screen, current_map)
        
        update_interval = current_time - last_update
        update_interval *= 1000
        
        if update_interval >= constants.UPDATE_INTERVAL:
            last_update = current_time
            
            current_map.player.update(current_map.loaded_chunks)
        
            for light in current_map.lights:
                light.update_particles()
        
        render(current_map)
        
        if check_fps == 1000:
            print(clock.get_fps())
            check_fps = 0
        else:
            check_fps += 1
        
def render(current_map):   
    screen.fill(constants.BLACK) 
    
    # TODO: background
    
    if day_time == 'day':
        screen.fill((200,255,255))
    elif day_time == 'night':
        screen.fill((0,0,0))
    else:
        print('not valid time')
    
    player = current_map.player
    
    # calculate render offset
    # TODO: don't allow scroll to go outside farthest chunk
    true_scroll[0] += (player.x-true_scroll[0]-screen.get_width()//2)/20
    true_scroll[1] += (player.y-true_scroll[1]-screen.get_height()//2)/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])
    
    render_queue = current_map.render_queue
    
    # renders each layer at a time in order
    # TODO: test if the layers are rendering in correct order
    for layer in render_queue:
        for tile in render_queue[layer]:
            to_render = render_queue[layer][tile]
            
            render = to_render['render']
            screen.blit(render.current_image, (to_render['x']-scroll[0], to_render['y']-scroll[1]))
    
    # render lights
    for light in current_map.lights:
        light.render(scroll, screen)
    
    # render the player
    screen.blit(player.current_image, (player.x-scroll[0], player.y-scroll[1])) # renders the player
    
    # render the player's collision rectangles
    for rect in player.collide_rects:
        new_rect = pg.Rect(player.collide_rects[rect].left-scroll[0], player.collide_rects[rect].top-scroll[1], player.collide_rects[rect].width, player.collide_rects[rect].height)
        pg.draw.rect(screen, (255,255,255), new_rect)
    
    # TODO: make fps cap changeable/removeable
    pg.display.flip()
    #clock.tick(constants.FPS)
    clock.tick()

# initiate pygame, the screen, and create the world
def init():
    pg.init()
    
    new_world = world.World(map_to_load)
    
    if day_time == 'day':
        light = lighting.RayOrigin((100, 100), color=(255,175,50), bloom=True, antialiasing=True, particles=True) # yellow color
    else:
        light = lighting.RayOrigin((100, 100), color=(255,255,255), bloom=True, antialiasing=True, particles=True) # moon color
    #light = lighting.RayOrigin((100, 1), bloom=False,antialiasing=False) # no color

    new_world.lights.append(light)
    
    return new_world

clock = pg.time.Clock()      

if __name__ == "__main__":
    main()
