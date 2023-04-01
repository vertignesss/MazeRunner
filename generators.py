import random

wall = 'w'
clear = 'c'
unvisited = 'u'
goal = 'g'
def init_maze(width, height):
    maze = []
    for i in range(0, width):
        line = []
        for j in range(0, height):
            line.append(unvisited)
        maze.append(line)
    return maze
surrounding = [[0, 1], [0, -1], [1, 0], [-1, 0]]
def surroundingCells(maze, wall):
    s_cells = 0
    for transform in surrounding:
        if (maze[wall[0] + transform[0]][wall[1] + transform[1]] == clear):
            s_cells += 1
    return s_cells
def RandomisedPrim(width, height, starting_width, starting_height):
    maze = init_maze(height, width)
    maze[starting_height][starting_width] = clear
    walls_in_processing = []
    for transform in surrounding:
        walls_in_processing.append([starting_height+transform[0], starting_width+transform[1]])
        maze[starting_height+transform[0]][starting_width+transform[1]] = wall

    while walls_in_processing:
        to_change = walls_in_processing[random.randint(0, len(walls_in_processing) - 1)]
        walls_in_processing.remove(to_change)
        if to_change[0] == 0 or to_change[0] == height - 1 or to_change[1] == 0 or to_change[1] == width - 1:
            continue
        horizontal_clears = (maze[to_change[0]][to_change[1] - 1] == 'c') + (maze[to_change[0]][to_change[1] + 1] == 'c')
        vertical_clears = (maze[to_change[0] - 1][to_change[1]] == 'c') + (maze[to_change[0] + 1][to_change[1]] == 'c')

        if (horizontal_clears == 1 or vertical_clears == 1) and surroundingCells(maze, to_change) < 2:
            maze[to_change[0]][to_change[1]] = clear
            for transform in surrounding:
                if (maze[to_change[0] + transform[0]][to_change[1] + transform[1]] == 'u'):
                    maze[to_change[0] + transform[0]][to_change[1] + transform[1]] = 'w'
                    if ([to_change[0] + transform[0], to_change[1] + transform[1]] not in walls_in_processing):
                        walls_in_processing.append([to_change[0] + transform[0], to_change[1] + transform[1]])
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            if maze[i][j] == unvisited:
                maze[i][j] = wall
    return maze
