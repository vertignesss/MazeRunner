import pygame
pygame.font.init()
font = pygame.font.Font("Singkong.ttf", 24)

def contains(rect1, rect2):
    return rect1.top <= rect2.top < rect2.bottom <= rect1.bottom and rect1.left <= rect2.left < rect2.right <= rect1.right


def quitChecker():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            quit()


def draw(object, camera, screen):
    draw_rect = object.rect.copy()
    draw_rect.move_ip(-camera.x, -camera.y)
    pygame.draw.rect(screen, object.color, draw_rect)
