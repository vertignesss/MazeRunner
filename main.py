import random
import pygame, time, keyboard
import generators
import maze_parts
import utility
import queue
import constants
debug = False
ticksTillDebug = 0
ticksTillScale = 0
ticksTillDifficulty = 0
Maze = []
Buttons = []
Orbs = []
__Highlighted = []
running = True
startingLifetime = 19099
endGame = False
pygame.init()
screen = pygame.display.set_mode((constants.width, constants.height))


class Camera(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, player):
        if (player.centery - self.y) * 3 < constants.height and self.y > 0:
            self.y = self.y - 1
        if (player.centery - self.y) * 3 > constants.height * 2 and self.y < constants.maze_height * constants.wall_size - constants.height:
            self.y = self.y + 1
        if (player.centerx - self.x) * 3 < constants.width and self.x > 0:
            self.x = self.x - 1
        if (player.centerx - self.x) * 3 > constants.width * 2 and self.x < constants.maze_width * constants.wall_size - constants.width:
            self.x = self.x + 1


camera = Camera(0, 0)


class Player(object):
    def __init__(self, x, y):
        self.rect = pygame.rect.Rect((x, y, constants.player_size, constants.player_size))
        self.lifetime = startingLifetime;
        self.color = (0, 255, 0)

    def check_collision(self, to_check):
        for object in to_check:
            if pygame.Rect.colliderect(self.rect, object.rect):
                return True
        return False

    def handle_keys(self):

        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT]:
            self.rect.move_ip(-1, 0)
            if self.check_collision(Maze):
                self.rect.move_ip(1, 0)

        if key[pygame.K_RIGHT]:
            self.rect.move_ip(1, 0)
            if self.check_collision(Maze):
                self.rect.move_ip(-1, 0)

        if key[pygame.K_UP]:
            self.rect.move_ip(0, -1)
            if self.check_collision(Maze):
                self.rect.move_ip(0, 1)

        if key[pygame.K_DOWN]:
            self.rect.move_ip(0, 1)
            if self.check_collision(Maze):
                self.rect.move_ip(0, -1)
        if key[pygame.K_BACKSLASH]:
            global debug
            global ticksTillDebug
            if ticksTillDebug <=0:
                debug = (debug ^ True)
                ticksTillDebug = 10
            else:
                ticksTillDebug = ticksTillDebug - 1
        if running:
            return
        global ticksTillScale
        if ticksTillScale <= 0:
            if key[pygame.K_u]:
                constants.maze_height = int(constants.maze_height * 1.1)
                constants.maze_width = int(constants.maze_width * 1.1)
                ticksTillScale = 10
            if key[pygame.K_d]:
                constants.maze_width = int(constants.maze_width / 1.1)
                constants.maze_height = int(constants.maze_height / 1.1)
                ticksTillScale = 10
        else:
            ticksTillScale = ticksTillScale - 1
        global ticksTillDifficulty
        if ticksTillDifficulty <= 0:
            if key[pygame.K_q]:
                constants.difficultyMultiplier = constants.difficultyMultiplier * 1.1
                ticksTillDifficulty = 10
            if key[pygame.K_e]:
                constants.difficultyMultiplier = constants.difficultyMultiplier / 1.1
                ticksTillDifficulty = 10
        else:
            ticksTillDifficulty = ticksTillDifficulty - 1
    def update(self):
        self.lifetime = self.lifetime - 1
        if self.check_collision(Orbs):
            for orb in Orbs.copy():
                if pygame.Rect.colliderect(self.rect, orb.rect):
                    Orbs.remove(orb)
                    self.lifetime = self.lifetime + constants.orbHPboost * 100 / constants.difficultyMultiplier
        if self.lifetime < 0:
            # toDO endgame screen
            global running
            running = False

    def getHit(self, amount):
        self.lifetime = self.lifetime - amount * constants.difficultyMultiplier

    def draw(self, camera, screen):
        utility.draw(self, camera, screen)


clock = pygame.time.Clock()
levelsCompleted = -1
player = Player(constants.wall_size, constants.wall_size)
pygame.display.set_caption("MazeRunner")
goal = maze_parts.Goal(4, 4)


def findDists(maze_char, x, y):
    thePath = []
    q = queue.Queue()
    q.put([x, y])
    distances = maze_char.copy()
    distances[x][y] = 0
    while not q.empty():
        current_vertice = q.get()
        for to_go in generators.surrounding:
            cell_to_go = [current_vertice[0] + to_go[0], current_vertice[1] + to_go[1]]
            if maze_char[cell_to_go[0]][cell_to_go[1]] == generators.clear and type(
                    distances[cell_to_go[0]][cell_to_go[1]]) == type('c'):
                distances[cell_to_go[0]][cell_to_go[1]] = distances[current_vertice[0]][current_vertice[1]] + 1
                q.put(cell_to_go)
    return distances
def findPathToGoal(maze_dists, x, y):
    way = []
    way.append([x,y])
    current_vertice = [x,y]
    while maze_dists[current_vertice[0]][current_vertice[1]] != 0:
        for to_go in generators.surrounding:
            cell_to_go = [current_vertice[0] + to_go[0], current_vertice[1] + to_go[1]]
            if isinstance(maze_dists[cell_to_go[0]][cell_to_go[1]], int):
                if maze_dists[current_vertice[0]][current_vertice[1]] == maze_dists[cell_to_go[0]][cell_to_go[1]] + 1:
                    way.append(cell_to_go)
                    current_vertice = cell_to_go
    way = list(reversed(way))
    return way

def nextLevel(x, y):
    global levelsCompleted
    levelsCompleted = levelsCompleted + 1
    global Buttons
    global Orbs
    global Maze
    global goal
    global __Highlighted
    Buttons.clear()
    Orbs.clear()
    Maze.clear()
    __Highlighted.clear()
    selected_generator = generators.RandomisedPrim
    generated_maze = selected_generator(constants.maze_width, constants.maze_height, x, y)
    distanced_maze = findDists(generated_maze, y, x)
    current_goal = [y, x]
    for i in range(len(distanced_maze)):
        for j in range(len(distanced_maze[i])):
            if isinstance(distanced_maze[i][j], int):
                if distanced_maze[i][j] > distanced_maze[current_goal[0]][current_goal[1]]:
                    current_goal = [i, j]
    goal_way = findPathToGoal(distanced_maze, current_goal[0], current_goal[1])
    for cell in goal_way:
        __Highlighted.append(maze_parts.__Highlighter(cell[1], cell[0]))
    orbStep = int(constants.blocksPerSecond * constants.orbHPboost * (0.8 * constants.difficultyMultiplier))
    for cell in range(0, len(goal_way), orbStep):
        generated_maze[goal_way[cell][0]][goal_way[cell][1]] = generators.orb
    generated_maze[current_goal[0]][current_goal[1]] = generators.goal
    unoccupied = []
    occupied = []
    for i in range(len(generated_maze)):
        for j in range(len(generated_maze[i])):
            if isinstance(generated_maze[i][j], int):
                unoccupied.append([i, j])
            if generated_maze[i][j] == generators.wall and 0 < i * j and i != len(generated_maze) - 1 and j != len(generated_maze[i]) - 1:
                occupied.append([i, j])
    random.shuffle(unoccupied)
    random.shuffle(occupied)
    amountOfSpikesUnoccupied = int(len(unoccupied) * constants.baseAdditionalSpikesUnoccupied * constants.difficultyMultiplier // 100)
    amountOfSpikesOccupied = int(len(occupied) * constants.baseAdditionalSpikesOccupied // 100)
    amountOfOrbsUnoccupied = int(len(unoccupied) * constants.baseAdditionalSpikesUnoccupied / constants.difficultyMultiplier // 100)
    for i in range(amountOfSpikesUnoccupied):
        generated_maze[unoccupied[i][0]][unoccupied[i][1]] = generators.spikedButton
    for i in range(amountOfSpikesOccupied):
        generated_maze[occupied[i][0]][occupied[i][1]] = generators.spikedButton
    for i in range(amountOfOrbsUnoccupied):
        generated_maze[unoccupied[i + amountOfSpikesUnoccupied][0]][unoccupied[i + amountOfOrbsUnoccupied][1]] = generators.orb
    for i in range(constants.maze_height):
        for j in range(constants.maze_width):
            if generated_maze[i][j] == generators.wall:
                Maze.append(maze_parts.WallBlock(j, i))
            if generated_maze[i][j] == generators.goal:
                goal = maze_parts.Goal(j, i)
            if generated_maze[i][j] == generators.spikedButton:
                Buttons.append(maze_parts.SpikedButton(j, i))
            if generated_maze[i][j] == generators.orb:
                Orbs.append(maze_parts.Orb(j, i))

def gameInit(x, y):
    global clock
    global player
    global screen
    global camera
    nextLevel(x, y)
    clock = pygame.time.Clock()
    player = Player(constants.wall_size * x, constants.wall_size * y)
    screen = pygame.display.set_mode((constants.width, constants.height))
    camera = Camera(0, 0)

gameInit(1, 1)
while True:
    while running:
        lifetime_counter = utility.font.render(str(int(player.lifetime) // 100), True, (0, 0, 0))
        counter_center = lifetime_counter.get_rect()
        counter_center = (constants.width - 72, 12)
        utility.quitChecker()
        if utility.contains(goal.rect, player.rect):
            nextLevel(int(int(player.rect.left) // constants.wall_size),
                      int(int(player.rect.top) // constants.wall_size))
        keyState = pygame.key.get_pressed()
        if keyState[pygame.K_ESCAPE]:
            running = False
        screen.fill((127, 127, 127))
        for wall in Maze:
            wall.draw(camera, screen)
        for orb in Orbs:
            orb.draw(camera, screen)
        for button in Buttons:
            button.draw(camera, screen)
            button.update(player)
        if debug:
            for highlighted in __Highlighted:
                highlighted.draw(camera, screen)
        screen.blit(lifetime_counter, counter_center)
        goal.draw(camera, screen)
        player.draw(camera, screen)
        player.handle_keys()
        player.update()
        pygame.display.update()
        camera.update(player.rect)
        clock.tick(120)
    screen.fill((255, 255, 255))

    if not endGame:
        player = Player(1, 1)
        camera = Camera(0,0)
        Maze.clear()
        goal = maze_parts.Goal(20, 20)
        endGame = True
    player.lifetime = 9999999999
    player.handle_keys()
    player.update()
    goal.draw(camera, screen)
    player.draw(camera, screen)
    endMessage = utility.font.render("Your score is : " + str(levelsCompleted), True, (0, 0, 0))
    message_center = endMessage.get_rect()
    message_center = (constants.width / 2, constants.height / 2)
    screen.blit(endMessage, message_center)
    clock.tick(120)
    utility.quitChecker()
    pygame.display.update()
    if utility.contains(goal.rect, player.rect):
        utility.quitChecker()
        gameInit(1, 1)
        running = True
        endGame = False
        levelsCompleted = 0
