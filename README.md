# Pygame-Lighting
A Pygame Lighting engine

The only sections you really need are lighting.py and particles.py, as well as the extra modules (numpy, shapley, etc.) 
The other stuff is just as an example, as they are part of the rest of the game engine I am working on, but I needed to
include them because everything relies on each other. I also have in the main section some profiling things at the top and
also in the main loop under the quit event, so if you dont those they arent neccesary at all.

On my system this usually runs at about 1000 fps in the default window size I set, and around 215 in maximised, and I am
working on improving the maximised performance but I may just be limited by pygame.

Clip: https://www.youtube.com/watch?v=9q7nr-6jXhI
