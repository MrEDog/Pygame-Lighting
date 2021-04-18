# super class of all entities and blocks etc.
class GameObject:
    def __init__(self, x, y, images=None):
        self.x = x
        self.y = y
        self.images = images
    
    # check if the object collides with anything in the list, needs to be a collision object
    # TODO: add way to check if it isnt a collision object
    def get_collisions(self, object_list):
        collisions = {}
        
        # get each collision rectangle and check if it intersects with anything in the list
        for collision_rect in self.collide_rects:
            object_collisions = self.collide_rects[collision_rect].collidedictall(object_list, True)
            if object_collisions:
                collisions[collision_rect] = True
        return collisions
      
    # this ensures that if it's called it dosen't crash
    # overide as neccesary in sub classes.
    def update(self):
        pass
