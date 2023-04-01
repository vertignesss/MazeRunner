import pygame, time, keyboard
import generators
import maze_parts
import utility
import queue
import constants

Maze = []
Buttons = []
Orbs = []
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
        if (
                player.centery - self.y) * 3 > constants.height * 2 and self.y < constants.maze_height * constants.wall_size - constants.height:
            self.y = self.y + 1
        if (player.centerx - self.x) * 3 < constants.width and self.x > 0:
            self.x = self.x - 1
        if (
                player.centerx - self.x) * 3 > constants.width * 2 and self.x < constants.maze_width * constants.wall_size - constants.width:
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
            cell_to_go = [current_vertice[0] + to_go[0]][current_vertice[1] + to_go[1]]
            if maze_dists[current_vertice[0]][current_vertice[1]] == maze_dists[cell_to_go[0]][cell_to_go[1]] + 1:
                way.append(cell_to_go)
                current_vertice = cell_to_go
    way = reversed(way)
    return way

def nextLevel(x, y):
    global levelsCompleted
    levelsCompleted = levelsCompleted + 1
    global Buttons
    global Orbs
    global Maze
    global goal
    Buttons.clear()
    Orbs.clear()
    Maze.clear()
    selected_generator = generators.RandomisedPrim
    generated_maze = selected_generator(constants.maze_width, constants.maze_height, x, y)
    distanced_maze = findDists(generated_maze, y, x)
    current_goal = [y, x]
    for i in range(len(distanced_maze)):
        for j in range(len(distanced_maze[i])):
            if isinstance(distanced_maze[i][j], int):
                if distanced_maze[i][j] > distanced_maze[current_goal[0]][current_goal[1]]:
                    current_goal = [i, j]
    goal_way = findPathToGoal(distanced_maze, y, x)

    generated_maze[current_goal[0]][current_goal[1]] = generators.goal
    for i in range(constants.maze_height):
        for j in range(constants.maze_width):
            if generated_maze[i][j] == generators.wall:
                Maze.append(maze_parts.WallBlock(j, i))
            if generated_maze[i][j] == generators.goal:
                goal = maze_parts.Goal(j, i)


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
        lifetime_counter = utility.font.render(str(player.lifetime // 100), True, (0, 0, 0))
        counter_center = lifetime_counter.get_rect()
        counter_center = (constants.width - 72, 12)
        utility.quitChecker()
        if utility.contains(goal.rect, player.rect):
            nextLevel(int(int(player.rect.left) // constants.wall_size),
                      int(int(player.rect.top) // constants.wall_size))
        keyState = pygame.key.get_pressed()
        print(levelsCompleted)
        if keyState[pygame.K_ESCAPE]:
            running = False
        screen.fill((127, 127, 127))
        goal.draw(camera, screen)
        player.draw(camera, screen)
        for wall in Maze:
            wall.draw(camera, screen)
        for orb in Orbs:
            orb.draw(camera, screen)
        for button in Buttons:
            button.draw(camera, screen)
            button.update(player)
        screen.blit(lifetime_counter, counter_center)
        player.handle_keys()
        player.update()
        pygame.display.update()
        camera.update(player.rect)
        clock.tick(120)
    screen.fill((255, 255, 255))

    print("I'm here")
    if not endGame:
        player = Player(1, 1)
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
