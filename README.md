# All Ball Extended
* Initially part of the PHYS-Final-Project
* Original code development ended May 2022

# Goals for this project
- Visual changes (Rework the project to include further intergration with Tiled)
  * Game scene rework
    - Background has 5 layers; 2 color-changing
    - Game layer has 1 layer. The sole one the player plays on
    - Foreground has 3 layers; 1 color-changing
      - Foreground allows for more platform apperance customization. Tiled integration includes the level layout to improve the level creation process. 
  * HUD/Info still remains below the game screen
    - Is considered a layer of the background. Changes with one of the background layers.
  * Player color can be changed
   
- Create a functional menu and pause system
  * Main menu has 4 options:    
    - play the game from the start
    - select a level
    - adjust screen size 
    - quit
  * Pause menu pauses game completely
    - Main game is in a loop (prev works have similar pause system)
    - Game can be exited from pause
    - Display controls on screen with a prompt

- Gameplay adjustments
  * Add more levels (main goal is 30)
  * Rework some block functionality

- Code cleanup
 * Seperate level creation from the main loop using more files
 * Cleanup the main loop so everything isn't cluttered 