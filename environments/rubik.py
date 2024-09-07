'''create a rubik cube env
reset and step method
only 6 moves. 
1 representation would be 6 (n,n) numpy array
another would connect each piece. So there would be 20 unique game objects.'''


import numpy as np

# RGB color values
COLOR = [(0, 0, 255),      # Blue
          (255, 165, 0),    # Orange
          (255, 255, 255),  # White
          (255, 0, 0),      # Red 
          (0, 255, 0),      # Green
          (255, 255, 0)]    # Yellow
COLOR = np.array(COLOR)

def render_flat(rubik: np.ndarray, wait: int = 3000):
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((270,360))
    screen.fill((245, 245, 220)) # beige background

    s = 90
    coords = [(s,0), (0,s), (s,s), (2*s,s), (s,2*s), (s,3*s)]
    coords = np.array(coords)
    face_size = np.array([90,90])
    tile_size = face_size // rubik.shape[1]
    BLACK = (0,0,0)
    '''render a rubik's cube flat by unboxing the faces'''
    counter = -1
    for face in range(rubik.shape[0]):
        counter += 1
        for i in range(rubik.shape[1]):
            for j in range(rubik.shape[2]):
                offset = tile_size * np.array([i,j])
                pos = coords[counter] + offset
                rect_shape = np.concatenate((pos, tile_size))

                pygame.draw.rect(screen, COLOR[rubik[face,i,j]], rect_shape)
                pygame.draw.rect(screen, BLACK, rect_shape, 3)

        PURPLE = (108, 59, 170)
        # pygame.draw.rect(screen, PURPLE, np.concatenate((coords[counter], face_size)), 3) # face border
    
    pygame.display.update()
    pygame.time.wait(wait)
    pygame.quit()


def rubik_starting_pos(n: int) -> np.array:
    rubik = np.zeros((6, n, n), dtype=int)
    for idx in range(6):
        face = np.full((n,n), idx)
        rubik[idx] = face
    return rubik




def step(rubik: np.ndarray, action: int) -> np.ndarray:
    '''
    Define a cube orientation. I define as white pointing up, with green facing me.
    x and y are defined on the white plane. z is perpendicular to both. 

    Circle 0 -- rotate on the x-z plane
    Circle 1 -- rotate on the y-z plane
    Circle 2 -- rotate on the x-y plane

    Each circle has n possible actions. 
    Reference global COLOR array for a mapping of ints to colors. 

    3-tuple Coord System:
        I use 3-tuples to define tiles on the cube. 
        axis-0 describes face. axis-1 index horizontally. axis-2 index vertically.

        Ex: (2,1,0) == white face. middle-up tile (edge piece; white-blue)
    '''

    assert rubik.shape[1] == rubik.shape[2]
    n = rubik.shape[1]
    # (circle #, row, forwards/backwards)
    action = (action // (2*n), (action%(2*n))//2, action%2)     
    '''
    # clockwise (cw) and ccw are a matter of perspective.
    # So I use forewards and backwards with respect to this ordering
    # even is forward. odd is backward.'''
    circle_paths = np.array([
        [2,4,5,0],
        [2,3,5,1],
        [4,3,0,1],
    ])

    row = action[1]
    starting_pos = np.array([
        [(row, i) for i in range(n)],
        [(i, row) for i in range(n)],
        [(i, row) for i in range(n)],
    ])

    def rot0(x,y):
        return (x,y)
    def rot90(x,y):
        return (y, (n-1)-x)
    def rot180(x,y):
        return ((n-1)-x, (n-1)-y)
    def rot270(x,y):
        return ((n-1)-y, x)

    circle_functs = [
        [rot0, rot0, rot0, rot0],
        [rot0, rot0, rot180, rot0],
        [rot0, rot90, rot180, rot270],
    ]
    start = starting_pos[action[0]]
    functions = circle_functs[action[0]]
    swap_tuples = np.array([[f(x,y) for x,y in start] for f in functions])

    # Add a dimension to the tuples describing its face. 
    face_dim = np.repeat(circle_paths[action[0]][:, np.newaxis], n, axis=1).reshape(4,n,1)
    move_arr = np.concatenate((face_dim, swap_tuples), axis=2)
    copied_tiles = np.copy([rubik[*tile] for tile in move_arr[0]])
    '''
    perform the axis rotation along a line of pieces.
    this code block rotates all pieces not on the plane of rotation.'''
    order = np.array([[3,0,-1], [1,4,1]])
    shift = 2*action[2] - 1
    for f in range(*order[action[2]]):
        target = move_arr[(f-shift)%4]
        new_tiles = move_arr[f]
        for idx in range(n):
            rubik[*target[idx]] = rubik[*new_tiles[idx]]
    for idx in range(n):
        rubik[*new_tiles[idx]] = copied_tiles[idx]

    # rotate the face of the cube when neccessary
    if action[1] == 0 or action[1] == n-1:
        face_rotation_ref = np.array([[1, 3], [0, 4], [2, 5]])
        face = face_rotation_ref[action[0], action[1] // (n-1)]
        rubik[face] = np.rot90(rubik[face])

    return rubik

if __name__ == '__main__':
    N = 4
    rubik = rubik_starting_pos(N)
    rubik = step(rubik, 0)
    render_flat(rubik, 3_000)
    rubik = step(rubik, 8)
    render_flat(rubik, 3_000)
    rubik = step(rubik, 0)
    render_flat(rubik, 3_000)
    rubik = step(rubik, 8)
    render_flat(rubik, 3_000)
