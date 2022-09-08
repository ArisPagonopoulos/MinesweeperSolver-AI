# MinesweeperSolver-AI
A python program that solves a minesweeper game. Made using opencv, autogui and implemanting an ai agent.
<p align = "center"><img src = "https://github.com/ArisPagonopoulos/MinesweeperSolver-AI/blob/main/Readme/minesweeper_demo.gif"> </p>

# Explanation:
I get information about the game by taking screenshots dynamically. Then, i draw contours in the image and recognize the blocks and their respective pixel position from their contours.
<p align = "center"><i>The board at the start looks like this.</i></p>
<p align = "center"> <img src = "https://github.com/ArisPagonopoulos/MinesweeperSolver-AI/blob//main/Readme/start_contours.png"> </p>
I save their pixel coordinates in a 16x16 array so i can tell the mouse to click on them using the pyautogui library.
So, for example when -after some clicks- the board is at this state:
<p align ="center"> <i> Using the contours i can deduce which blocks are open.</i></p>
<p align = "center"><img src = "https://github.com/ArisPagonopoulos/MinesweeperSolver-AI/blob/main/Readme/contours.jpg"> </p>
<p> After that, i compare each block's image with the images of 1,2 etc and save their values in the board array.</p>
<p align = "center"> <i> The space symbol (" ") represents a closed block, the * symbol represents a mine that the ai agent has found.</i>
<p align = "center"> <img src = "https://github.com/ArisPagonopoulos/MinesweeperSolver-AI/blob/main/Readme/game-board.jpg"></p>
<p> Finally, the ai agent that i have created can tell which block is safe to click next and after some time wins the game. </p>

