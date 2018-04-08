#!/usr/bin/env python
import random
import time
import pygame
from fish import Player, EnemyFish, Shark

# Set Game Constants
WINDOW_WIDTH = 640   # width of the program's window, in pixels
WINDOW_HEIGHT = 480  # height in pixels
HALF_WINDOW_WIDTH = int(WINDOW_WIDTH / 2)
HALF_WINDOW_HEIGHT = int(WINDOW_HEIGHT / 2)
CAMERASLACK = 90     # how far from the center before moving the camera

WATER_COLOR = (0, 141, 199)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

FPS = 30            # frames per second to update the screen
TEXTTIME = 2        # how long text messages appear for in s

# tweak the difficulty
INVULNTIME = 2       # how long the Player is invulnerable after being hit in s
WINSIZE = 275        # how big the Player needs to be to win
NUMENEMYFISH = 30    # number of EnemyFish in the active area
NUMSHARKS = 1        # number of Sharks in the active area


def main():
    """Initializes main game variables and starts game"""
    global FPSCLOCK, SCREEN, BASICFONT
    # set up the game window
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('.\img\gameicon.png'))
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Fishy')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    # start the game
    while True:
        runGame()


def runGame():
    """Starts a new game"""
    # set up variables for the start of a new game
    invulnerableMode = False   # if the player is invulnerable
    invulnerableStartTime = 0  # time the player became invulnerable
    gameOverMode = False       # if the player has lost
    gameOverStartTime = 0      # time the player lost used to restart game
    winMode = False            # if player has won
    winStartTime = 0           # time the player won used to restart game
    startTime = time.time()    # time game starts used to display instructions

    # create the surfaces to hold game text
    howToSurf = BASICFONT.render(
        'Use arrows to move', True, WHITE)
    howToRect = howToSurf.get_rect()
    howToRect.center = (HALF_WINDOW_WIDTH, HALF_WINDOW_HEIGHT - 30)

    howToSurf2 = BASICFONT.render(
        'Eat smaller fish to win', True, WHITE)
    howToRect2 = howToSurf.get_rect()
    howToRect2.center = (HALF_WINDOW_WIDTH, HALF_WINDOW_HEIGHT + 50)

    gameOverSurf = BASICFONT.render('Game Over', True, WHITE)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINDOW_WIDTH, HALF_WINDOW_HEIGHT)

    winSurf = BASICFONT.render(
        'You are the biggest fish in the pond!', True, WHITE)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINDOW_WIDTH, HALF_WINDOW_HEIGHT)

    # initialize player, camera, and enemy information
    player = Player(HALF_WINDOW_WIDTH, HALF_WINDOW_HEIGHT)
    camera = Camera()   # handles visible area
    enemies = []        # stores all the non-player fish
    num_enemyfish = 0   # how many EnemyFish are currently active
    num_sharks = 0      # how many Sharks are currently active

    while True:  # main game loop
        # add background, healthbar, enemies, and player to the screen
        SCREEN.fill(WATER_COLOR)
        drawHealthMeter(player.health)
        for enemy in enemies:
            enemy.draw(SCREEN, camera)
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not (invulnerableMode and flashIsOn):
            player.draw(SCREEN, camera)

        # add more enemies if we don't have enough.
        while num_enemyfish < NUMENEMYFISH:
            size = random.randint(int(player.size - 2 * player.size ** 0.5),
                                  int(player.size + player.size ** 0.5))
            x, y = camera.getRandomOffCameraPos(size)
            enemies.append(EnemyFish(x, y, size))
            num_enemyfish += 1
        while num_sharks < NUMSHARKS:
            size = player.size + 75
            x, y = camera.getRandomOffCameraPos(size)
            enemies.append(Shark(x, y, size, player))
            num_sharks += 1

        # If the game just started show the instructions
        if time.time() - TEXTTIME < startTime:
            SCREEN.blit(howToSurf, howToRect)
            SCREEN.blit(howToSurf2, howToRect2)
        # If the player won show win text
        elif winMode:
            SCREEN.blit(winSurf, winRect)
            if time.time() - winStartTime > TEXTTIME:
                return  # restart game after waiting TEXTTIME

        # move all Fish and check for collisions
        elif not gameOverMode:
            # Check if we should turn off invulnerability
            if (invulnerableMode and
                    time.time() - invulnerableStartTime > INVULNTIME):
                invulnerableMode = False

            player.move()  # move the player
            camera.adjust(player)  # adjust camera to follow player

            # loop through enemies list backwards because some may get deleted
            for i in range(len(enemies) - 1, -1, -1):
                enemy = enemies[i]
                enemy.move()  # move each enemy

                # Remove enemies far from the player
                if camera.isOutsideActiveArea(enemy):
                    del enemies[i]
                    num_enemyfish, num_sharks = updateEnemyCts(num_enemyfish,
                                                               num_sharks,
                                                               enemy)
                    continue

                # check if the player has collided with an enemy
                if player.colrect.colliderect(enemy.colrect):
                    # player eats smaller fish
                    if enemy.size < player.size:
                        # grow the player
                        player.eat(enemy)
                        # remove eaten fish
                        del enemies[i]
                        num_enemyfish, num_sharks = updateEnemyCts(num_enemyfish,
                                                                   num_sharks,
                                                                   enemy)
                        # check if won
                        if player.size > WINSIZE:
                            winMode = True
                            winStartTime = time.time()

                    # otherwise player is smaller and takes damage
                    elif not invulnerableMode:
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        player.health -= 1
                        if player.health == 0:
                            gameOverMode = True  # turn on "game over mode"
                            gameOverStartTime = time.time()
        else:
            # game is over, show "game over" text
            SCREEN.blit(gameOverSurf, gameOverRect)
            if time.time() - gameOverStartTime > TEXTTIME:
                return  # restart game after waiting TEXTTIME

        # update display and clock
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawHealthMeter(currentHealth):
    """Adds the health meter to the display"""
    for i in range(currentHealth):  # draw red health bars
        pygame.draw.rect(SCREEN, RED,
                         (15, 35 - i * 10, 20, 10))
    for i in range(3):  # draw the white outlines
        pygame.draw.rect(SCREEN, WHITE,
                         (15, 35 - i * 10, 20, 10), 1)


def updateEnemyCts(NEnemyFish, NSharks, removedenemy):
    """Update the enemy counts when an enemy is removed from the game"""
    if removedenemy.etype == "fish":
        NEnemyFish -= 1
    elif removedenemy.etype == "shark":
        NSharks -= 1
    return NEnemyFish, NSharks


class Camera(object):
    """Camera class handles items related to the visible area

    Attributes:
        x, y: top left coordinates of the visible area

    Key Methods
        adjust: Moves the camera (visible area) based on player location
        getRandomOffCameraPos: Returns position to spawn enemies off-screen
        isOutsideActiveArea: Returns boolean if enemy is far from player
    """

    def __init__(self):
        # top left of camera
        self.x, self.y = 0, 0

    def adjust(self, player):
        """Moves the camera if the player is close to the edge"""
        halfPlayerSize = int(player.size / 2)
        playerCenterx = player.x + halfPlayerSize
        playerCentery = player.y + halfPlayerSize
        if (self.x + HALF_WINDOW_WIDTH) - playerCenterx > CAMERASLACK:
            self.x = playerCenterx + CAMERASLACK - HALF_WINDOW_WIDTH
        elif playerCenterx - (self.x + HALF_WINDOW_WIDTH) > CAMERASLACK:
            self.x = playerCenterx - CAMERASLACK - HALF_WINDOW_WIDTH
        if (self.y + HALF_WINDOW_HEIGHT) - playerCentery > CAMERASLACK:
            self.y = playerCentery + CAMERASLACK - HALF_WINDOW_HEIGHT
        elif playerCentery - (self.y + HALF_WINDOW_HEIGHT) > CAMERASLACK:
            self.y = playerCentery - CAMERASLACK - HALF_WINDOW_HEIGHT

    def getRandomOffCameraPos(self, ObjSize):
        """returns x, y coordinates outside the camera view
        (to find where it is ok to draw new enemies)
        """
        # object where the camera view is
        cameraRect = pygame.Rect(self.x, self.y,
                                 WINDOW_WIDTH, WINDOW_HEIGHT)

        while True:
            # randomly choose a point within 1 width/height of the camera
            x = random.uniform(self.x - WINDOW_WIDTH,
                               self.x + (2 * WINDOW_WIDTH))
            y = random.uniform(self.y - WINDOW_HEIGHT,
                               self.y + (2 * WINDOW_HEIGHT))
            # only return x, y if an ObjSize object placed there
            # would not collide with (be seen in) the camera view
            objRect = pygame.Rect(x, y, ObjSize, ObjSize)
            if not objRect.colliderect(cameraRect):
                return x, y

    def isOutsideActiveArea(self, fish):
        """Returns boolean indicating if fish is far from camera
        (more than a window length beyond edge of window)
        Used to determine if fish should be removed.
        """
        boundsLeftEdge = self.x - WINDOW_WIDTH
        boundsTopEdge = self.y - WINDOW_HEIGHT
        boundsRect = pygame.Rect(
            boundsLeftEdge, boundsTopEdge, WINDOW_WIDTH * 3, WINDOW_HEIGHT * 3)
        return not boundsRect.colliderect(fish.colrect)


if __name__ == '__main__':
    main()
