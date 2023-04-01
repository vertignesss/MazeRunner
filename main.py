import pygame, time, keyboard
import generators
Maze = []
Buttons = []
Orbs = []
player_size = 16
wall_size = player_size * 1.5
width = 1080
height = 720
maze_height = 30
maze_width = 45
orbHPboost = 10
difficultyMultiplier = 1.0
baseAdditionalOrbs = 10
blocksPerSecond = 4
running = True
pygame.init()
screen = pygame.display.set_mode((width, height))
font = pygame.font.Font("Singkong.ttf", 24)

class Camera(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def update(self, player):
        #print(self.x, self.y, player.centerx, player.centery)
        if (player.centery - self.y) * 3 < height and self.y > 0:
            self.y = self.y - 1
        if (player.centery - self.y) * 3 > height * 2 and self.y < maze_height * wall_size - height:
            self.y = self.y + 1
        if (player.centerx - self.x) * 3 < width and self.x > 0:
            self.x = self.x - 1
        if (player.centerx - self.x) * 3 > width * 2 and self.x < maze_width * wall_size - width:
            self.x = self.x + 1
camera = Camera(0, 0)
def contains(rect1, rect2):
   return rect1.top < rect2.top < rect2.bottom < rect1.bottom and rect1.left < rect2.left < rect2.right < rect1.right
def draw(object):
    global camera
    global screen
    draw_rect = object.rect.copy()
    draw_rect.move_ip(-camera.x, -camera.y)
    pygame.draw.rect(screen, object.color, draw_rect)
class Player(object):
    def __init__(self, x, y):
        self.rect = pygame.rect.Rect((x, y, player_size, player_size))
        self.lifetime = 1099;
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
                self.rect.move_ip(1,0)

        if key[pygame.K_RIGHT]:
            self.rect.move_ip(1, 0)
            if self.check_collision(Maze):
                self.rect.move_ip(-1,0)

        if key[pygame.K_UP]:
            self.rect.move_ip(0, -1)
            if self.check_collision(Maze):
                self.rect.move_ip(0,1)

        if key[pygame.K_DOWN]:
            self.rect.move_ip(0, 1)
            if self.check_collision(Maze):
                self.rect.move_ip(0,-1)

    def update(self):
        self.lifetime = self.lifetime - 1
        if self.check_collision(Orbs):
            for orb in Orbs.copy():
                if pygame.Rect.colliderect(self.rect, orb.rect):
                    Orbs.remove(orb)
                    self.lifetime = self.lifetime + orbHPboost * 100 / difficultyMultiplier
        if self.lifetime < 0:
            print("LOL") #toDO endgame screen
            global running
            running = False

    def getHit(self, amount):
        self.lifetime = self.lifetime - amount * difficultyMultiplier

    def draw(self):
        draw(self)

class WallBlock(object):
    def __init__(self, x, y):
        self.rect = pygame.rect.Rect((x * wall_size, y * wall_size, wall_size, wall_size))
        self.color = (200, 200, 200)
    def draw(self):
        draw(self)


class Button(object):
    def __init__(self, x, y):
        self.color = (191, 127, 127)
        self.pressed = False
        self.rect = pygame.rect.Rect(x * wall_size + wall_size/4,y * wall_size + wall_size / 4, wall_size/2, wall_size/2)

    def update(self, player):
        if pygame.Rect.colliderect(self.rect, player.rect) and not self.pressed:
            self.pressed = True
        if self.pressed:
            self.color = (255, 63, 63)
    def draw(self):
            draw(self)
class SpikedButton(Button):
    def __init__(self, x, y):
        self.color = (191, 127, 127)
        self.pressed = False
        self.rect = pygame.rect.Rect(x * wall_size + wall_size/4,y * wall_size + wall_size / 4, wall_size/2, wall_size/2)
        self.ticksTillUnspike = 0
    def update(self, player):
        if self.ticksTillUnspike < 0:
            self.pressed = False
            self.color = (191, 127, 127)
        if pygame.Rect.colliderect(self.rect, player.rect) and not self.pressed:
            self.pressed = True
            self.ticksTillUnspike = 100
        if self.pressed:
            self.color = (0, 0, 0)
            if pygame.Rect.colliderect(self.rect, player.rect):
                player.getHit(1)
        self.ticksTillUnspike = self.ticksTillUnspike - 1
class Orb(object):
    def __init__(self, x, y):
        self.rect = pygame.rect.Rect(x * wall_size + wall_size*2/8, y * wall_size + wall_size*2/8, wall_size /2, wall_size /2)
        self.color = (0, 0, 255)
    def draw(self):
        draw(self)
        
def quitChecker():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            quit()
class Goal(object):
    def __init__(self, x, y):
        self.rect = pygame.rect.Rect(x * wall_size, y * wall_size, wall_size, wall_size)
        self.color = (0, 0, 0)
    def draw(self):
        draw(self)
clock = pygame.time.Clock()
player = Player(wall_size, wall_size)
pygame.display.set_caption("MazeRunner")
goal = Goal(4, 4)
def gameInit(x, y):
    global clock
    global player
    global screen
    global camera
    global Buttons
    global Orbs
    global Maze
    Buttons.clear()
    Orbs.clear()
    Maze.clear()
    clock = pygame.time.Clock()
    player = Player(wall_size * x, wall_size * y)
    screen = pygame.display.set_mode((width, height))
    camera = Camera(0, 0)
    Buttons.append(Button(2, 2))
    Buttons.append(SpikedButton(3, 3))
    selected_generator = generators.RandomisedPrim
    generated_maze =  selected_generator(maze_width, maze_height, 1, 1)
    for i in range(maze_height):
        for j in range(maze_width):
            if generated_maze[i][j] == generators.wall:
                Maze.append(WallBlock(j, i))
while True:
    while running:
        lifetime_counter = font.render(str(player.lifetime//100), True, (255,255,255))
        counter_center = lifetime_counter.get_rect()
        counter_center = (width - 72, 12)
        quitChecker()

        keyState = pygame.key.get_pressed()

        if keyState[pygame.K_ESCAPE]:
            running = False

        screen.fill((127, 127, 127))
        player.draw()
        for wall in Maze:
            wall.draw()
        for orb in Orbs:
            orb.draw()
        for button in Buttons:
            button.draw()
            button.update(player)
        screen.blit(lifetime_counter, counter_center)

        player.handle_keys()
        player.update()
        pygame.display.update()
        camera.update(player.rect)
        clock.tick(120)
        print(player.lifetime)
    screen.fill((0, 0, 0))

    if True:
        quitChecker()
        gameInit(1, 1)
        running = True
