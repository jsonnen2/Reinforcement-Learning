'''create a rubik cube env
reset and step method
only 6 moves. 
1 representation would be 6 (n,n) numpy array
another would connect each piece. So there would be 20 unique game objects.'''


import numpy as np
import pygame

# RGB color values
COLOR = [(0, 0, 255),      # Blue
          (255, 165, 0),    # Orange
          (255, 255, 255),  # White
          (255, 0, 0),      # Red 
          (0, 255, 0),      # Green
          (255, 255, 0)]    # Yellow
COLOR = np.array(COLOR)

screen = None


def render_flat(rubik: np.ndarray, wait: int = 3000):
    '''
    Display the rubik's cube "unpacked" in a pygame window.
    The cube is flattened to show each face at once.
    My numpy matrices are all orientated such that (0,0) occurs at the upper-left tile of this flattened cube.
    
       [ ]
    [ ][ ][ ]
       [ ]
       [ ]
    '''
    cube_size = 90
    global screen
    if screen is None:
        pygame.init()
        screen = pygame.display.set_mode((3*cube_size, 4*cube_size))

    screen.fill((245, 245, 220)) # beige background

    coords = np.array([
        [cube_size,0], [0,cube_size], 
        [cube_size,cube_size], [2*cube_size,cube_size], 
        [cube_size,2*cube_size], [cube_size,3*cube_size],
    ])
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


def rubik_starting_pos(n: int) -> np.ndarray:
    rubik = np.zeros((6, n, n), dtype=int)
    for idx in range(6):
        face = np.full((n,n), idx)
        rubik[idx] = face
    return rubik

def rubik_cube_scrambled(n: int, scramble=40) -> np.ndarray:
    '''perform random actions on a solved rubik cube'''
    rubik = rubik_starting_pos(n)
    for _ in range(scramble):
        action = np.random.randint(0, 6*n)
        rubik = step(rubik, action)
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
    great_circle = action // (2*n)
    row = (action % (2*n) // 2)
    '''
    # clockwise (cw) and ccw are a matter of perspective.
    # So I use forewards and backwards with respect to this ordering
    # even actions are forwards. odd are backwards.'''
    circle_paths = np.array([
        [2,4,5,0],
        [2,3,5,1],
        [4,3,0,1],
    ])
    # row exists in set [0, n-1]. 
    # It describes which row of the great circle to rotate
    # these coordinates are in reference to face 2 
    starting_pos = np.array([
        [(row, i) for i in range(n)],
        [(i, row) for i in range(n)],
        [(i, row) for i in range(n)],
    ])

    def rot0(arr):
        return arr
    def rot90(arr):
        x = (n-1)-arr[:,0]
        y = arr[:,1]
        return np.stack((y, x), axis=1)
    def rot180(arr):
        x = (n-1)-arr[:,0]
        y = (n-1)-arr[:,1]
        return np.stack((x,y), axis=1)
    def rot270(arr):
        x = arr[:,0]
        y = (n-1)-arr[:,1]
        return np.stack((y,x), axis=1)

    circle_functs = [
        [rot0, rot0, rot0, rot0],
        [rot0, rot0, rot180, rot0],
        [rot0, rot90, rot180, rot270],
    ]
    start = starting_pos[great_circle]
    functions = circle_functs[great_circle]
    swap_tuples = np.array([f(start) for f in functions])

    '''
    the swap_tuples data are missing an axis to describe which face of the cube it belongs to.
    this data describes a rotation along 1 of 3 great circles.
    I can use circle_paths to give me the correct face.''' 
    face_dim = np.repeat(circle_paths[great_circle][:, np.newaxis], n, axis=1).reshape(4,n,1)
    move_arr = np.concatenate((face_dim, swap_tuples), axis=2)
    copied_tiles = np.copy([rubik[*tile] for tile in move_arr[0]])
    '''
    perform the axis rotation along a line of pieces.
    this code block rotates all pieces not on the plane of rotation.
    '''
    order = np.array([[3,0,-1], [1,4,1]]) # for loop indices 
    parity = action % 2     # is action even or odd?
    shift = 2*parity - 1    # even = +1  ;  odd = -1
    '''shift the source data into the target indices on the rubik's cube'''
    for f in range(*order[parity]):
        target = move_arr[(f-shift)%4]
        source = move_arr[f]
        for idx in range(n):
            rubik[*target[idx]] = rubik[*source[idx]]
    for idx in range(n):
        rubik[*source[idx]] = copied_tiles[idx]

    # rotate the face of the cube when neccessary
    if row == 0 or row == n-1:
        face_rotation_ref = np.array([[1, 3], [0, 4], [2, 5]])
        face = face_rotation_ref[great_circle, row // (n-1)]
        rubik[face] = np.rot90(rubik[face])

    return rubik


if __name__ == '__main__':
    N = 3
    rubik = rubik_starting_pos(N)
    
    import time
    start=time.time()
    for _ in range(100_000):
        action = np.random.randint(0, 18)
        rubik = step(rubik, action)
    print(time.time() - start)
