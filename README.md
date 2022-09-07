# MinesweeperSolver-AI
A python program that solves a minesweeper game. Made using opencv, autogui and implemanting an ai agent.
<p align = "center"><img src = "https://github.com/ArisPagonopoulos/MinesweeperSolver-AI/blob/main/minesweeper_demo.gif"> </p>

# Explanation:
I get information about the game by taking a screenshot. Then, i draw contours in the image and recognize the blocks and their respective pixel position from their contours.
<p align = "center"><i>The board at the start looks like this.</i></p>
<p align = "center"> <img src = "https://github.com/ArisPagonopoulos/MinesweeperSolver-AI/blob/main/start_contours.png"> </p>
I save their pixel coordinates in a array so i can tell the mouse to click on them using the pyautogui library.
So, for example when -after some clicks- the board is at this state
<p align = "center"> <img src = "https://github.com/ArisPagonopoulos/MinesweeperSolver-AI/blob/main/game.jpg"> </p>
Using the contours i can deduce which blocks are open. 
<p align = "center"> <img src = "https://github.com/ArisPagonopoulos/MinesweeperSolver-AI/blob/main/contours.png"> </p>
After that, i compare each block's image with the images of 1,2 etc and save their values in the board array.
Finally, the ai agent that i have created can tell which block is safe to click next and after some time wins the game.

# Room for improvement:
<p>The program is designed to run on my computer. The pixel coordinates for the screenshot were put manually, but from the boards contour we could get it's pixels coordinates so it can run on pc's with different resolutions than mine.</p>

