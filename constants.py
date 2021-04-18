FPS = 60
BLACK= (0,0,0)
BLOCK_SIZE = 32

PLAYER_SPEED = 10
PLAYER_JUMP = 20
PLAYER_MAX_JUMPS = 2

GRAVITY = 0.2
MAX_GRAV = 7

CHUNK_SIZE = 8

UPDATE_INTERVAL = 10

def COORD_TO_PIX(coord):
    return int(coord * BLOCK_SIZE)

def string_to_tuple(coords):
    return tuple(map(int, coords.split(',')))

def tuple_to_string(coords):
    return str(coords[0]) + "," + str(coords[1])
