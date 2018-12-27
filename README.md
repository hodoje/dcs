# dcs
Faculty subject - Distributed Computer Systems

# Assignment text

# Battle city (1985)

- Make a game similar to Battle City game. Make a scheme similar to the original game, through which the avatars can move.
- **Roles:**
  - Two players, move their avatars using cursor keys or with ASDW keys
    - They can move up-down, left-right
    - They can fire projectiles, projectiles can move in 4 directions, depending on the direction to which the avatar is turned to
    - Each player has 3 lives for a level
    - At the beginning of the level, they are located in the base on the bottom of the screen
  - Enemies:
    - Appear randomly on the top of the screen
    - At the beginning of the level there are 6 enemy tanks
    - They move randomly between the blocks
    - Randomly, independently from each other, they shoot projectiles
    
- **Rules:**
  - There are infinite number of levels
  - If a projectile hits a player, he loses a life
  - If a projectile of the player hits an enemy tank, the enemy disappears from the map
  - If a projectile hits a block from which the map is made of, the block disappears
  - After each level, projectiles, players and enemies are moving faster
  - After each level, the number of enemy tanks is increased
  - For passing to the next level, players need to destroy all the enemy tanks
  - The winner is the player that survives the most amount of time
  - The game is finished either when all the players are dead or the enemies have destroyed the base
  
- For realization use Python3, PyQt5, multiprocessing. Work in teams of 2-4 members. Write a documentation in which there is a general description of the game and rezime all the pros and cons of using Python language, PyQt5 framework and paralelization.
- Demo at the link: https://www.youtube.com/watch?v=MPsA5PtfdL0

- **NOTE**:
  - Assignment text is subjectable to changes (new requirements).
