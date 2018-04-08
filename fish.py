import pygame
from pygame.locals import *
import random
import math
import sys

# Constants
#   Player
MAXSPEEDPLAYER = 12  # fastest player speed
PLAYERACC = 2        # keydown accelaration
PLAYERDRAG = 1       # natural deceleration rate
STARTSIZE = 25       # starting player size
L_PLAYER_IMG = pygame.image.load('./img/Player.png')
R_PLAYER_IMG = pygame.transform.flip(L_PLAYER_IMG, True, False)

#   EnemyFish
MINSPEED = 2         # slowest other fish speed
MAXSPEED = 4         # fastest other fish speed
DIRCHANGEFREQ = 2    # % chance of direction change per frame
R_FISH_IMG = pygame.image.load('./img/EnemyFish.png')
L_FISH_IMG = pygame.transform.flip(R_FISH_IMG, True, False)

#   Shark
SHARKSPEED = 4  # speed the shark moves towards the player
L_SHARK_IMG = pygame.image.load('./img/Shark.png')
R_SHARK_IMG = pygame.transform.flip(L_SHARK_IMG, True, False)

# Confirm values won't cause issues
#   Confirm acceleration isn't equal to drag
#   assumption used so don't need a boolean to determine if player dragging
if PLAYERACC == PLAYERDRAG:
    raise ValueError('PLAYERACC Must Not Equal PLAYERDRAG')

#   pygame can only scale to integer sizes
if int(STARTSIZE) != STARTSIZE:
    raise ValueError('STARTSIZE must be a positive integer')

#    Values should be positive
if (MAXSPEEDPLAYER <= 0 or
    PLAYERACC <= 0 or
    PLAYERDRAG <= 0 or
    STARTSIZE <= 0 or
    MINSPEED <= 0 or
    MAXSPEED <= 0 or
    SHARKSPEED <= 0 or
        DIRCHANGEFREQ <= 0):
    raise ValueError('Check that all constants are positive')


class Fish(object):
    """Abstract superclass for player and enemies

    Attributes:
        L_image, R_image:   Left, Right facing images of the Fish
        image:              The current fish image that will be drawn
        size:               Sidelength size of square fish
        x, y:               Absolute position of the fish
        vx, vy:             Velocity components of the fish
        colrect:            A rectangle to check for collisions
        camrect:            A rectangle near the camera for drawing

    Key Methods:
        move:   Changes the fish's position based on its velocity
        draw:   Draws the fish on the screen
    """

    def __init__(self, L_image, R_image, x, y, size):
        self.L_image, self.R_image = L_image, R_image
        self.image = pygame.transform.scale(L_image, (size, size))
        self.size = size
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0
        self.colrect = pygame.Rect(x, y, size, size)
        self.camrect = None

    def move(self):
        """Move the fish according to its velocity & update collision rect"""
        self.y += self.vy
        self.x += self.vx
        self.colrect = pygame.Rect(self.x, self.y, self.size, self.size)

    def draw(self, screen, camera):
        """Draws the fish in the game"""
        self.camrect = pygame.Rect(self.x - camera.x,
                                   self.y - camera.y,
                                   self.size, self.size)
        screen.blit(self.image, self.camrect)


class Player(Fish):
    """The player fish that listens for keyboard events to determine movement

    Attributes(*denotes not part of parent Fish class):
        L_image, R_image:   Left, Right facing images of Fish
        image:              The current fish image that will be drawn
        size:               Sidelength size of square fish
        x, y:               Absolute position of the fish
        vx, vy:             Velocity components of the fish
        *accx, accy:        Acceleration components of the fish
        colrect:            A rectangle to check for collisions
        camrect:            A rectangle near the camera for drawing
        *health:            Times player hit by bigger fish for gameover
        *facing:            Left or right for drawing new size after eating

    Additional Methods:
        eat(Fish):  player eats a smaller fish and grows
    """

    def __init__(self, x, y):
        super(Player, self).__init__(L_PLAYER_IMG, R_PLAYER_IMG,
                                     x, y, STARTSIZE)
        self.accx, self.accy = 0, 0
        self.health = 3
        self.facing = 'left'

    def move(self):
        """Move the player

        If a directional key is being pressed, accelerate in that direction
        until reach MAXSPEEDPLAYER

        If directional key isn't pressed, slow fish down according
        to deceleration equal to PLAYERDRAG until velocity is 0
        """
        for event in pygame.event.get():  # event handling loop
            # if window is closed, terminate game processes and python
            if event.type == QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

            # Set accelaration if keys are pressed
            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    self.accy = -1 * PLAYERACC
                elif event.key in (K_DOWN, K_s):
                    self.accy = PLAYERACC

                # for left and right, update the image as well
                elif event.key in (K_LEFT, K_a):
                    self.facing = 'left'
                    self.accx = -1 * PLAYERACC
                    self.image = pygame.transform.scale(self.L_image,
                                                        (self.size,
                                                         self.size))
                elif event.key in (K_RIGHT, K_d):
                    self.facing = 'right'
                    self.accx = PLAYERACC
                    self.image = pygame.transform.scale(self.R_image,
                                                        (self.size,
                                                         self.size))

            # decelerate when keys are unpressed
            elif event.type == KEYUP:
                if event.key in (K_UP, K_w, K_DOWN, K_s):
                    self.accy = PLAYERDRAG if self.vy < 0 else -1 * PLAYERDRAG
                elif event.key in (K_LEFT, K_a, K_RIGHT, K_d):
                    self.accx = PLAYERDRAG if self.vx < 0 else -1 * PLAYERDRAG

        # update Velocity
        #       x direction
        # don't drag past 0 velocity
        if abs(self.accx) == PLAYERDRAG and abs(self.vx) < PLAYERDRAG:
            self.vx = 0
        # otherwise add the acceleration to the velocity
        else:
            self.vx += self.accx
            # snap the velocity back to the max if over the max
            if abs(self.vx) > MAXSPEEDPLAYER:
                self.vx = MAXSPEEDPLAYER * math.copysign(1, self.vx)

        #       y direction
        # don't drag past 0 velocity
        if abs(self.accy) == PLAYERDRAG and abs(self.vy) < PLAYERDRAG:
            self.vy = 0
        # otherwise add the acceleration to the velocity
        else:
            self.vy += self.accy
            # snap the velocity back to the max if over the max
            if abs(self.vy) > MAXSPEEDPLAYER:
                self.vy = MAXSPEEDPLAYER * math.copysign(1, self.vy)

        # move the fish according to its velocity
        super(Player, self).move()

    def eat(self, fish):
        """player grows according to size of eaten fish"""
        self.size += int(fish.size ** 0.3)
        # update display
        if self.facing == "left":
            self.image = pygame.transform.scale(self.L_image,
                                                (self.size,
                                                 self.size))
        else:
            self.image = pygame.transform.scale(self.R_image,
                                                (self.size,
                                                 self.size))


class EnemyFish(Fish):
    """Fish that move randomly
    Attributes(* denotes not part of parent Fish class):
        L_image, R_image:   Left, Right facing images of Fish
        image:              The current fish image that will be drawn
        size:               Sidelength size of square fish
        x, y:               Absolute position of the fish
        vx, vy:             Velocity components of the fish
        colrect:            A rectangle to check for collisions
        camrect:            A rectangle near the camera for drawing
        *etype:             Enemy type used for tracking in game file
    """

    def __init__(self, x, y, size):
        """Make a Fish with a random starting velocity"""
        super(EnemyFish, self).__init__(L_FISH_IMG, R_FISH_IMG, x, y, size)
        self.vx, self.vy = self.__getRandomVelocity()
        self.etype = 'fish'

    def __getRandomVelocity(self):
        """Returns a random velocity with x and y components"""
        vx = random.randint(MINSPEED, MAXSPEED)
        vy = random.randint(MINSPEED, MAXSPEED)
        if random.randint(0, 1) == 0:
            vx *= -1
        if random.randint(0, 1) == 0:
            vy *= -1
        return vx, vy

    def move(self):
        """Move EnemyFish after random chance of shifting velocity"""
        # random chance they change direction if a fish
        if self.etype == 'fish' and random.randint(0, 99) < DIRCHANGEFREQ:
            self.vx, self.vy = self.__getRandomVelocity()

        super(EnemyFish, self).move()
        # flip the image if necessary
        if self.vx > 0:
            self.image = pygame.transform.scale(self.R_image,
                                                (self.size, self.size))
        else:
            self.image = pygame.transform.scale(self.L_image,
                                                (self.size, self.size))


class Shark(EnemyFish):
    """Fish that moves towards player

    Attributes(* denotes not part of parent EnemyFish class):
        L_image, R_image:   Left, Right facing images of Fish
        image:              The current fish image that will be drawn
        size:               Sidelength size of square fish
        x, y:               Absolute position of the fish
        vx, vy:             Velocity components of the fish
        colrect:            A rectangle to check for collisions
        camrect:            A rectangle near the camera for drawing
        etype:              Enemy type used for tracking in game file
        *player:            The player fish to move towards

    TO DO:
        Add a shark collision group so that they don't stack if multiple
    """

    def __init__(self, x, y, size, player):
        # Setup with correct image (using Fish constructor)
        super(EnemyFish, self).__init__(L_SHARK_IMG, R_SHARK_IMG,
                                        x, y, size)
        # Shark has a player to track
        self.player = player
        self.etype = 'shark'

    def move(self):
        """Move Shark towards the player center"""
        # difference between player and shark centers
        xdiff = ((self.player.x + self.player.size / 2) -
                 (self.x + self.size / 2))
        ydiff = ((self.player.y + self.player.size / 2) -
                 (self.y + self.size / 2))

        if abs(xdiff) < SHARKSPEED:
            self.vx = xdiff
        else:
            self.vx = SHARKSPEED * math.copysign(1, xdiff)

        if abs(ydiff) < SHARKSPEED:
            self.vy = ydiff
        else:
            self.vy = SHARKSPEED * math.copysign(1, ydiff)

        super(Shark, self).move()
