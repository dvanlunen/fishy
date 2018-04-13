# Fishy
*Author: Dan VanLunen*
![Screenshot][img/Screenshot.png]

A python game that demonstrates OOP. The player is a fish that moves with the arrow keys or WASD. When the player collides with a smaller fish, she gets larger. When the player collides with a larger fish, she gets hurt. The objective of the game is to become almost as large as the screen.

The game's components are broken into two main python files.

## game.py
This file contains the main game logic. It starts the game, draws the background, health bar, text, and fish.  It also keeps track of all the fish, updates their movement, and notifies the player of a game over or a win condition.

## fish.py
This file includes class definitions for each type of fish in the game.

### Fish
Fish is an abstract class that all other Fish are sub-classes of.

### Player(Fish)
Player is a class that listens to keyboard events to move the player.

### EnemyFish(Fish)
EnemyFish is a fish that moves randomly.

### Shark(EnemyFish)
Shark is a fish that moves towards the player.
