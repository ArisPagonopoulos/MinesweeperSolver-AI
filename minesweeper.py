import cv2
import numpy as np 
import sys
from PIL import ImageGrab
from matplotlib import pyplot as plt
import time
import random
import pyautogui
import os



def imageprocessing(img):
    """Get's an image array as input and returns the processed image"""

    #grayscale the image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #applying gaussianblur
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    #applying adaptivethreshold to the blurred image
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)
    return thresh


def is_similar(img1, img2):
    """Check if two images are equal, we need it to recognize the number of the block"""

    if np.sum(img1 == img2)/(img1.shape[0]*img1.shape[1]*img1.shape[2])>=0.89:
        return True
    return False


def get_centers():
        """We get the pixel coordinates of each block's center """

        #grab a screenshot from the browser
        img = cv2.imread("c:\\users\\aris\\desktop\\minesweeper\\start.png")
        cnts, _ = cv2.findContours(imageprocessing(img), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        centers = []
        for i in cnts:
            area = cv2.contourArea(i)
            M = cv2.moments(i)
            try:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            except:
                continue
            #this is the contour area the blocks have
            if area == 52.5:
                centers.append((cX+5, cY+5))
        #we have to reverse the list because they are in the reverse order
        centers.reverse()
        centers_array = np.array(centers)
        #reshape it to 16x16
        centers_array = np.reshape(centers_array,(16,16,2))
        return centers_array


def grab_board():
        """Grab a screenshot of the board, returns the state and the board"""

        scr = ImageGrab.grab(bbox = (445, 219, 859, 694))
        state = ImageGrab.grab(bbox=(632, 237, 666, 271))
        state = np.array(state)[:,:,::-1]
        scr = np.array(scr)[:, :, ::-1]
        return state, scr

def update_contours(img):
        """ Takes an image array as input and prints the board"""

        mask = np.zeros_like(img)
        cnts, _ = cv2.findContours(imageprocessing(img), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for i in cnts:
            area = cv2.contourArea(i)
            M = cv2.moments(i)
            try:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            except:
                continue
            if area == 52.5:
                #draw the contours in green color
                cv2.drawContours(mask, [i], -1, (0,255,0), -1)
                #if i just use cv2.cirlce(mask , (cX, cY)) the centers are in the uppercorner, so 
                #i just added the same number to both diagonals to move the centers diagonally
                cv2.circle(mask , (cX+5, cY+5), 4 , (0,0,255), -1)
            elif 90.5==area or (area==93):
                cv2.drawContours(mask, [i], -1, (0,255,0), -1)
                cv2.circle(mask, (cX-5, cY-5), 4, (0,0,255), -1)
            elif (area==64) or (area==75.5):
                cv2.drawContours(mask, [i], -1, (0,255,0), -1)
                cv2.circle(mask,(cX+5,cY+5), 4 , (0,0,255), -1)
        for i in range(16):
            for j in range(16):
                center = centers_array[i, j]
                if not (255 in mask[center[1]:center[1]+2, center[0]:center[0]+2, 2]):
                    #then the block has been clicked
                    cv2.circle(mask,(center[0],center[1]), 4, (255,255,255), -1)
                    #if it has already been played continue
                    if (i, j) in known:
                        continue
                    else:
                        #check if the block has a number on it and update the board array
                        block = img[center[1]-9:center[1]+9, center[0]-9:center[0]+9]
                        for k in templates.keys():
                            #what number is that block
                            known.add((i,j))
                            if is_similar(block, templates[k]):
                                #update the board
                                #print("The block that got clicked has value ",int(k))
                                board[i, j] = int(k)
                                ai.add_knowledge((i,j), board[i,j])
                                break
                        else:
                            #could be also a flag instead of a 5, but the game would be over if that's the case
                            known.add((i, j))
                            board[i, j] = 5
                            ai.add_knowledge((i, j), board[i, j])
                            
        print(board)

#now let's create the ai agent

class Sentence():
        """
        Logical statement about a Minesweeper game
        A sentence consists of a set of board cells,
        and a count of the number of those cells which are mines.
        """
    
        def __init__(self, cells, count):
            self.cells = set(cells)
            self.count = count
    
        def __eq__(self, other):
            return self.cells == other.cells and self.count == other.count
    
        def __str__(self):
            return f"{self.cells} = {self.count}"
    
        def known_mines(self):
            """
            Returns the set of all cells in self.cells known to be mines.
            """
            #if the count is the same as the length of the cell they are all mines
            if (len(self.cells) == self.count) and self.cells:
                return list(self.cells)
    
        def known_safes(self):
            """
            Returns the set of all cells in self.cells known to be safe.
            """
            #if count is 0 and we have a none empty cell they are all safe
            
            if (self.count == 0) and self.cells:
                return list(self.cells)
    
        def mark_mine(self, cell):
            """
            Updates internal knowledge representation given the fact that
            a cell is known to be a mine.
            """
            #we remove the cell that is a mine but now we have less mines in our cells, so we decrease count
            if cell in self.cells:
                self.cells.remove(cell)
                self.count -= 1
    
        def mark_safe(self, cell):
            """
            Updates internal knowledge representation given the fact that
            a cell is known to be safe.
            """
            #we just remove the cell, the number of mines in the cells remains the same
            if cell in self.cells: 
                self.cells.remove(cell)
    
    
class MinesweeperAI():
        """
        Minesweeper game player
        """
    
        def __init__(self, height=8, width=8):
    
            # Set initial height and width
            self.height = height
            self.width = width
    
            # Keep track of which cells have been clicked on
            self.moves_made = set()
    
            # Keep track of cells known to be safe or mines
            self.mines = set()
            self.safes = set()
    
            # List of sentences about the game known to be true
            self.knowledge = []
    
        def mark_mine(self, cell):
            """
            Marks a cell as a mine, and updates all knowledge
            to mark that cell as a mine as well.
            """
            #we add the cell in the mines set
            self.mines.add(cell)
            #we mark the cell to every sentence as mine
            for sentence in self.knowledge:
                sentence.mark_mine(cell)
    
        def mark_safe(self, cell):
            """
            Marks a cell as safe, and updates all knowledge
            to mark that cell as safe as well.
            """
            #same as above but for the safe cells
            self.safes.add(cell)
            for sentence in self.knowledge:
                sentence.mark_safe(cell)
    
        def add_knowledge(self, cell, count):
            """
            Called when the Minesweeper board tells us, for a given
            safe cell, how many neighboring cells have mines in them.
            """

            self.moves_made.add(cell)
            self.mark_safe(cell)
            i, j = cell
            #get the coordinates for the neighbor cell
            neighbors = [t for t in [(i-1, j-1), (i-1, j), (i-1, j+1), (i, j-1), (i, j+1), (i+1, j-1), (i+1, j), (i+1, j+1)] if (0 <= t[0] <= self.height-1) and (0 <= t[1] <= self.width-1)]
            #substract from the count the neighbors that are known to be mines because we won't include them in the sentence
            count = count - len([i for i in neighbors if i in self.mines])
            neighbors = [t for t in neighbors if t not in (self.safes.union(self.mines))]
            self.knowledge.append(Sentence(neighbors, count))
            kn_sf = []
            kn_mn = []
            for sentence in self.knowledge:
                #get the safe cells from the sentence
                if sentence.known_safes():
                    kn_sf.append(sentence.known_safes())
                #get the mine cells from the sentence
                if sentence.known_mines():
                    kn_mn.append(sentence.known_mines())
            #mark the safe and mine cells we got from the sentences
            for lst in kn_sf:
                for cell in lst.copy():
                    self.mark_safe(cell)
            for lst in kn_mn:
                for cell in lst.copy():
                    self.mark_mine(cell)
            #we create inference from knowledge
            temp = self.knowledge[-1]
            for sentence in self.knowledge[:-1]:
                if sentence.cells.issubset(temp.cells) and sentence.cells:
                    new_sentence_cells = (temp.cells).difference(sentence.cells)
                    new_sentence_count = temp.count - sentence.count
                    new_sentence = Sentence(new_sentence_cells, new_sentence_count)
                    self.knowledge.append(new_sentence)
                #we remove every sentence that has empty set of cells since we don't need them
                #otherwise the set gets too big
                if not sentence.cells:
                    self.knowledge.remove(sentence)
    
    
        def make_safe_move(self):
            """
            Returns a safe cell to choose on the Minesweeper board.
            The move must be known to be safe, and not already a move
            that has been made."""

            #first check if the list of available moves is non-empty
            if self.safes.difference(self.moves_made):
                print("making safe move")
                return list(self.safes.difference(self.moves_made))[0]
            else:
                return None
    
        def make_random_move(self):
            
            """Returns a move to make on the Minesweeper board."""

            moves = [(i, j) for i in range(self.height) for j in range(self.width)]
            available = set(moves).difference(self.moves_made.union(self.mines))
            #first check if the set is empty
            if available:
                print("making random move")
                return random.choice(list(available))
            return None

#we create the board of the game
board = -1*np.ones((16,16), dtype = np.uint8)
known = set()

#get the centers
centers_array = get_centers()
ai = MinesweeperAI(16,16)

#load the images for the numbers
pyautogui.FAILSAFE = False
empty = cv2.imread("c:\\users\\aris\\desktop\\empty.png")
one = cv2.imread("c:\\users\\aris\\desktop\\minesweeper\\1.png")
two = cv2.imread("c:\\users\\aris\\desktop\\minesweeper\\2.png")
three = cv2.imread("c:\\users\\aris\\desktop\\minesweeper\\3.png")
four = cv2.imread("c:\\users\\aris\\desktop\\minesweeper\\4.png")
templates = {"0":empty,"1":one, "2":two, "3":three, "4":four}
smiley = cv2.imread("c:\\users\\aris\\desktop\\minesweeper\\smiley.png")
sulky = cv2.imread("c:\\users\\aris\\desktop\\minesweeper\\sulky.png")
states = {"ongoing": smiley, "lost": sulky}


#grab the screen and run the game until it's over
state, img = grab_board()
while not (is_similar(state, states["lost"])):
    m = ai.make_safe_move()
    if m:
        h, w = centers_array[m[0], m[1]]
        move = (h+445, w + 219)
    else:
        m = ai.make_random_move()
        if m:
            h, w = centers_array[m[0], m[1]]
            move = (h + 445, w + 219)
        else:
            print("No move left to make")
            break
    print("Move is ",m)
    pyautogui.click(move)
    #pyautogui.moveTo(random.randint(0,10),random.randint(0, 10))
    state, img = grab_board()
    #time.sleep(1)
    update_contours(img)
    ai.add_knowledge(m, board[m])
if is_similar(state, states["lost"]):
    print("You lost! Good luck next time!")
else:
    print("You won! Congratulations!")
