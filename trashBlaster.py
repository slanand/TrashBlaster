#T rashBlaster 
# By Swathi Anand (slanand)

from Tkinter import *
import random
import math

def mousePressed(canvas,event):
    # mouse press events on the homescreen
    if canvas.data.isHomeScreen == True:
        # start playing button 
        if ((event.x >= 236 and event.x <= 418) and
            (event.y >= 483 and event.y <= 518)):
            canvas.data.isHomeScreen = False
            init(canvas)
        # how to play button 
        if ((event.x >= 249 and event.x <= 401) and
            (event.y >= 533 and event.y <= 568)):
            canvas.data.howToPlay = True
            canvas.data.isHomeScreen = False
            howToPlay(canvas)
    # mouse press events on how to play screen
    if canvas.data.howToPlay == True:
        # start playing button 
        if ((event.x >= 236 and event.x <= 418) and
            (event.y >= 508 and event.y <= 543)):
            canvas.data.isHomeScreen = False
            init(canvas) 
    # mouse press events on game screen
    if canvas.data.isHomeScreen == False:
        # how to play button
        if ((event.x >= 502 and event.x <= 626) and
            (event.y >= 413 and event.y <= 440)):
            canvas.data.howToPlay = True
            canvas.data.isHomeScreen = True
            howToPlay(canvas)
        # exit button 
        if ((event.x >= 531 and event.x <= 597) and
            (event.y >= 453 and event.y <= 485)):
            canvas.data.isHomeScreen = True
            loadHomeScreen(canvas)

def keyPressed(canvas,event):
    # keys that work even if game is over
    if (event.char == "r"): # restarts game
        init(canvas)
    elif (event.char == "q"): # quits game and goes to home screen 
        canvas.data.isHomeScreen = True
        loadHomeScreen(canvas)
    # keys that work only if game is not over
    if ((canvas.data.isGameOver == False) and 
        (canvas.data.isSuccessfulGame == False)):
        if event.char == "p":
            canvas.data.isPaused = not canvas.data.isPaused
        # keys that work only when game is not paused
        if canvas.data.isPaused == False:
            dRadian = .05 # change in the angle of teh shooter
            # right arrow key moves shooter to the right
            if event.keysym == "Right": 
                furthestRight = .67
                if (canvas.data.radian - dRadian >= furthestRight): 
                    canvas.data.radian -= dRadian
                    drawShooter(canvas)
            # left arrow key moves shooter to the left
            elif event.keysym == "Left": 
                furthestLeft = 2.47
                if (canvas.data.radian + dRadian <= furthestLeft):
                    canvas.data.radian += dRadian
                    drawShooter(canvas)
            # spacebar shoots trash up 
            elif event.char == " ":
                # clears depths board for recycling
                clearDepths(canvas)
                canvas.data.isShooting = True
                canvas.data.tRadian = canvas.data.radian
    gameRedrawAll(canvas)
    
# timer fired for when an object has been shot and is moving    
def shootTimerFired(canvas):
    if ((canvas.data.isGameOver == False) and 
        (canvas.data.isSuccessfulGame == False) and 
        (canvas.data.isPaused == False)):
        if canvas.data.isShooting == True:
            moveTrash(canvas)
        gameRedrawAll(canvas)
    delay = 30 # milliseconds
    canvas.after(delay, shootTimerFired, canvas)

# clears the depths board before recycling
def clearDepths(canvas):
    canvas.data.depths =[([-1]*canvas.data.cols) for row in xrange(canvas.data.rows)]

# moves trash by changing its x and y coordinates
def moveTrash(canvas):
    dMove = 25
    # adjusts x and y coordinate based on angle given my tRadian 
    canvas.data.p3_x += dMove*math.cos(canvas.data.tRadian)
    canvas.data.p3_y += -dMove*(math.sin(canvas.data.tRadian))
    # if the move makes the trash hit a side wall, trash rebounds
    if hitSideWalls(canvas) == True:
        canvas.data.p3_x -= dMove*math.cos(canvas.data.tRadian)
        canvas.data.p3_y -= -dMove*(math.sin(canvas.data.tRadian))
        # angle is changed to 180 - current angle 
        canvas.data.tRadian = math.pi-canvas.data.tRadian
    # if move makes the trash hit another trash or the top wall,
    # undo the move and place the trash
    if (hitAnotherTrash(canvas) == True) or (hitTopWall(canvas) == True):
        canvas.data.isShooting = False
        canvas.data.p3_x -= dMove*math.cos(canvas.data.tRadian)
        canvas.data.p3_y -= -dMove*(math.sin(canvas.data.tRadian))
        placeTrash(canvas)
        # if trash is within the board,
        if ((canvas.data.trashRow < canvas.data.rows) and
            (canvas.data.trashCol< canvas.data.cols) and 
            (canvas.data.trashCol >= 0)):
        # recycle the trash 
            recycle(canvas,canvas.data.trashRow,canvas.data.trashCol)
        # calls false depths which would be used 
        # in the recursive function isolatedTrash
        falseDepths(canvas)
        board = canvas.data.board
        # isolated trash is called on every  cell in the top row of the board
        for col in xrange(canvas.data.cols):
            if board[0][col] > -1:
                trashR = 0
                trashC = col
                isolatedTrash(canvas,trashR,trashC)
        removeIsolatedTrash(canvas)
        # radian of the shooter is set back to its initial angle (90 degrees)
        canvas.data.radian = math.pi/2
        getAnotherTrash(canvas)
        nextTrash(canvas)
        # coordinates of moving trash are set back to its initial position
        canvas.data.p3_x = canvas.data.p3_initX
        canvas.data.p3_y = canvas.data.p3_initY
    gameRedrawAll(canvas)

# returns true if the trash hit the top wall
def hitTopWall(canvas):
    leeway = 10
    # if y coordinate of the moving trash is within 10 pixels
    # from the top margin, the trash hit the wall.
    if canvas.data.p3_y <= canvas.data.topMargin+leeway:
        return True
    return False

# returns true if the moving trash hits either of the side walls
def hitSideWalls(canvas):
    leeway = 10
    # if x coordinate of the moving trash is within 10 pixels
    # from the top margin, the trash hit the wall.
    if ((canvas.data.p3_x <= canvas.data.leftMargin + leeway) or
        (canvas.data.p3_x >= canvas.data.rightMargin - leeway)):
        return True
    return False 

# returns true if the moving trash hits a placed trash on the board
def hitAnotherTrash(canvas):
    rows,cols = canvas.data.rows,canvas.data.cols
    cellSize = canvas.data.cellSize
    halfCellSize = 20
    board = canvas.data.board
    canvas.data.allTrash = []
    # iterate through the board and take in the coordinates  
    # of the middle of every trash 
    for row in xrange(canvas.data.rows):
        for col in xrange(canvas.data.cols):
            if board[row][col] != -1: # if the location is a trash
                left = canvas.data.leftMargin + (cellSize * col) + cellSize/2
                top = canvas.data.topMargin + (cellSize * row) + cellSize/2
                # when top row is offset to the left
                if canvas.data.topRow == 0:
                    # for odd rows that are offset to the right
                    if (row%2 != 0): 
                        canvas.data.allTrash += [(left+(cellSize/2)+ \
                                                halfCellSize,top+halfCellSize)]
                    else: # for even rows that are offset to the left
                        canvas.data.allTrash += [(left+halfCellSize, \
                                                  top+halfCellSize)]
                # when top row is offset to the right
                elif canvas.data.topRow == 1: 
                    # for odd rows that are offset to the left
                    if row%2 != 0: 
                        canvas.data.allTrash += [(left+halfCellSize, \
                                                  top+halfCellSize)]
                    else: # for even rows that are offset to the right
                        canvas.data.allTrash += [(left+(cellSize/2)+ \
                                                halfCellSize,top+halfCellSize)]
    # check if the moving trash is within half a cell (20x20)
    # of any trash on the board 
    for trash in canvas.data.allTrash:
        if ((abs(trash[0]-(canvas.data.p3_x+halfCellSize))<=halfCellSize) and 
            (abs(trash[1]-(canvas.data.p3_y+halfCellSize))<=halfCellSize)):
            return True
    return False

# places trash on the board
def placeTrash(canvas):
    cellSize = canvas.data.cellSize
    leftMargin = canvas.data.leftMargin
    # calculates the row number the current trash is on
    canvas.data.trashRow = int(canvas.data.p3_y/cellSize)
    # if the trash is on the 14th row, game is over
    if canvas.data.trashRow >= canvas.data.rows:
        gameOver(canvas)
        addtoHighScores(canvas)
    if canvas.data.topRow == 0: # when the top row is offset to the left
        # for odd rows that are offset to the right
        if canvas.data.trashRow%2 != 0: 
            canvas.data.trashCol = int(((canvas.data.p3_x-leftMargin-
                                            (cellSize/2))/cellSize))
        else: # for even rows offset to the left
            canvas.data.trashCol = int(((canvas.data.p3_x-leftMargin)/
                                         cellSize))
    elif canvas.data.topRow == 1: # when the top row is offset to the right
        # for odd rows that are offset to the left
        if canvas.data.trashRow%2 != 0: 
            canvas.data.trashCol = int(((canvas.data.p3_x-leftMargin)/
                                         cellSize))
        else: # for even rows that are offset to the right
            canvas.data.trashCol = int(((canvas.data.p3_x-leftMargin-
                                            (cellSize/2))/cellSize))
    # if calculated location of the trash is within the board,
    if ((canvas.data.trashRow < canvas.data.rows) and 
        (canvas.data.trashCol < canvas.data.cols) and 
        (canvas.data.trashCol >= 0)):
        # but there is already a trash there,
        if canvas.data.board[canvas.data.trashRow][canvas.data.trashCol]!= -1:
            # move the trash to the row below
            canvas.data.trashRow +=1
    # if either the newly calulated row or column is out of bounds... 
    if canvas.data.trashRow >= canvas.data.rows:
        gameOver(canvas)
        addtoHighScores(canvas)
    elif canvas.data.trashCol == canvas.data.cols:
        canvas.data.trashCol -= 1
    elif canvas.data.trashCol < 0:
        canvas.data.trashCol += 1
    # otherwise place the trash on the board
    else:
        canvas.data.board[canvas.data.trashRow][canvas.data.trashCol] = \
        canvas.data.currentTrash
    gameRedrawAll(canvas)
    
# starts the process of recycling (removing) trash from the board      
def recycle(canvas,tRow,tCol):
    board = canvas.data.board
    trashType = board[tRow][tCol]
    groupTrash(canvas,tRow,tCol,trashType,depth=0)
    removeSimilarTrash(canvas,trashType)
                   
# uses floodfill method to recursively search around a 
# given location on the board for trash similar to the given trashtype     
def groupTrash(canvas,trashRow,trashCol,trashType,depth=0):
    board = canvas.data.board
    # if trashRow and trashCol are within the board,
    if ((trashRow >= 0) and (trashRow < canvas.data.rows) and
        (trashCol >= 0) and (trashCol < canvas.data.cols)):
        # if the trash is not the same as the trash type,
        if (board[trashRow][trashCol] != trashType):
            # set the location in depths to -1
            canvas.data.depths[trashRow][trashCol] = -1
        # if the trash is the same as the trash type and the location
        # was not visited in the depths board, set that location
        # to the current depth
        elif canvas.data.depths[trashRow][trashCol] == -1:
            canvas.data.depths[trashRow][trashCol] = depth
            groupTrash(canvas,trashRow,trashCol-1,trashType,depth+1) # left
            groupTrash(canvas,trashRow-1,trashCol,trashType,depth+1) # up
            groupTrash(canvas,trashRow+1,trashCol,trashType,depth+1) # down
            groupTrash(canvas,trashRow,trashCol+1,trashType,depth+1) # right
            if canvas.data.topRow == 0: # when top row is indented to the left
                if trashRow%2 == 0: # for even rows indented to the left
                    # check the upper left and lower left
                    groupTrash(canvas,trashRow-1,trashCol-1,trashType,depth+1)
                    groupTrash(canvas,trashRow+1,trashCol-1,trashType,depth+1)
                else: # for odd rows indented to the right
                    # check the upper right and lower right
                    groupTrash(canvas,trashRow-1,trashCol+1,trashType,depth+1)
                    groupTrash(canvas,trashRow+1,trashCol+1,trashType,depth+1)
            # when top row is indented to the right
            elif canvas.data.topRow == 1: 
                if trashRow%2 == 0: # for even rows indented to the right
                    # check the upper right and lower right
                    groupTrash(canvas,trashRow-1,trashCol+1,trashType,depth+1)
                    groupTrash(canvas,trashRow+1,trashCol+1,trashType,depth+1)
                else: # for odd rows indented to the left
                    # check the lower left and upper left
                    groupTrash(canvas,trashRow-1,trashCol-1,trashType,depth+1)
                    groupTrash(canvas,trashRow+1,trashCol-1,trashType,depth+1)

# removes trash from board, if there is more than three  
def removeSimilarTrash(canvas,trashType):
    board = canvas.data.board
    similarTrash = []
    # iterate throught every row and call in depths board
    for row in xrange(canvas.data.rows):
        for col in xrange(canvas.data.cols):
            if canvas.data.depths[row][col] != -1:
                # add location of depth to similar trash as a tuple
                similarTrash += [(row,col)]
    if len(similarTrash) >= 3:
        for trash in similarTrash:
            board[trash[0]][trash[1]] = -1 # set to empty location 
        # add 2 times number of trash removed to score
        canvas.data.score += 2*len(similarTrash) 
        # add number of trash removed to its respective material count
        canvas.data.materialCounts[trashType] += len(similarTrash)
        gameRedrawAll(canvas)

# makes false depths board before finding isolated trash
def falseDepths(canvas):
    canvas.data.falseDepths =[([-1]*canvas.data.cols) for row in xrange(canvas.data.rows)]
    board = canvas.data.board
    for row in xrange(canvas.data.rows):
        for col in xrange(canvas.data.cols):
            # sets location on false depth board to false,
            # if that spot on the board is a trash
            if board[row][col] > -1:
                canvas.data.falseDepths[row][col] = False

# recursively goes down every cell from the top row to check 
# each cell is attached to a cell at the top 
def isolatedTrash(canvas,trashRow,trashCol):
    board = canvas.data.board
    # if the trashRow and trashCol are within the board
    if ((trashRow >= 0) and (trashRow < canvas.data.rows) and
        (trashCol >= 0) and (trashCol < canvas.data.cols)):
        # if the spot is empty, set that location in falseDepths to -1
        if (canvas.data.falseDepths[trashRow][trashCol] == -1):
            canvas.data.falseDepths[trashRow][trashCol] = -1
        # if the spot is a trash (False), set that spot to True
        elif canvas.data.falseDepths[trashRow][trashCol] == False:
            canvas.data.falseDepths[trashRow][trashCol] = True
            isolatedTrash(canvas,trashRow+1,trashCol) # check down
            isolatedTrash(canvas,trashRow,trashCol-1) # check left
            isolatedTrash(canvas,trashRow,trashCol+1) # check right 
            # when top row is indented to the left
            if canvas.data.topRow == 0: 
                if trashRow%2 == 0: # for even rows indented left
                    # check bottom left 
                    isolatedTrash(canvas,trashRow+1,trashCol-1)
                else: # for odd rows indented right
                    # check bottom right
                    isolatedTrash(canvas,trashRow+1,trashCol+1)
            # when top row is indented to the right
            elif canvas.data.topRow == 1:
                if trashRow%2 == 0: # for even rows indented right
                    # check bottom right
                    isolatedTrash(canvas,trashRow+1,trashCol+1)
                else: # for odd rows indented left
                    # check bottom left
                    isolatedTrash(canvas,trashRow+1,trashCol-1)
            
# removes isolated from board (does not affect score)
def removeIsolatedTrash(canvas):
    board = canvas.data.board
    isolatedTrash = []
    # iterate through every row and col 
    for row in xrange(canvas.data.rows):
        for col in xrange(canvas.data.cols):
            # if spot wasn't visited, and spot was a trash,
            if canvas.data.falseDepths[row][col] == False:
                # add tupe of row and col to isolated trash
                isolatedTrash += [(row,col)]
    # set all spots on board to empty (-1)
    for trash in isolatedTrash:
        board[trash[0]][trash[1]] = -1
    gameRedrawAll(canvas)

# sets current trash to next trash after a trash has been shot
def getAnotherTrash(canvas):
    canvas.data.currentTrash = canvas.data.nextTrash
    
# gets the next trash at random
def nextTrash(canvas):
    canvas.data.nextTrash = random.randint(0,len(canvas.data.trash)-1)

# timer for adding a row of trash from the top
def addLineTimerFired(canvas):
    if (canvas.data.isPaused == False):
        if ((canvas.data.isGameOver == False) and 
            (canvas.data.isSuccessfulGame == False)):
            if isAddLineLegal(canvas) == True:
                addLine(canvas)
            else:
                gameOver(canvas)
                addtoHighScores(canvas)
            gameRedrawAll(canvas)
    delays = [15000,10000,5000] #milliseconds
    # how often row is added from the top depends on the level
    delay = delays[canvas.data.level-1]
    canvas.after(delay, addLineTimerFired, canvas)
    
# adds a line of random trash to the top of the board
def addLine(canvas):
    board = canvas.data.board
    # iterate through the board and move each row down one
    for row in xrange(canvas.data.rows-1,-1,-1):
        for col in xrange(canvas.data.cols):
            board[row][col] = board[row-1][col]
    # add a row to the top of the board
    for col in xrange(canvas.data.cols):
        indexTrash = random.randint(0,len(canvas.data.trash)-1)
        board[0][col] = indexTrash
    # switch the offset depending on the current offset 
    if canvas.data.topRow == 0:
        canvas.data.topRow = 1
    else:
        canvas.data.topRow = 0

# returns False if the last row is already filled 
def isAddLineLegal(canvas):
    cols = canvas.data.cols
    board = canvas.data.board
    for col in xrange(cols):
        if board[canvas.data.rows-1][col] != -1:
            return False
    return True
    
# displays 3 highest scores of current execution of TrashBlaster
# in the order that they are in highScores array after each game is over
def displayStatWindow(canvas):
    highScores = canvas.data.highScores
    top = canvas.data.topMargin + 200
    left = canvas.data.leftMargin + 7
    bottom = top + 300
    right = canvas.data.rightMargin-40
    canvas.create_image(left,top,image=canvas.data.chalkboard,anchor = NW)
    canvas.create_text((left+right)/2 + 15,top+35,text="High Scores:",
                        font=("Chalkduster",34,"bold"),fill="white")
    if len(highScores) == 0:
        canvas.create_text((left+right)/2+20,
                           (top+bottom)/2,
                            text="No High Scores Yet!",
                            font=("Chalkduster",20, "bold"),fill="white")
    # display every scroe in highScores array
    for score in xrange(len(highScores)):
        canvas.create_text((left+right)/2 + 15,
                            top+35+((score+1)*50),
                            text="#" + str(score+1)
                            + ": " + str(highScores[score]),
                            font=("Chalkduster",30, "bold"),fill="white")  

# displays phrases at the top of the game board at the end of a level
# depending on the level
def displayWordsForEndOfLevel(canvas):
    top = canvas.data.topMargin + 100
    left = (canvas.data.rightMargin + canvas.data.leftMargin)/2
    if canvas.data.level == 1:
        canvas.create_image(left,top,image=canvas.data.level2Words)
        canvas.data.nextLevel = 2
    elif canvas.data.level == 2:
        canvas.create_image(left,top,image=canvas.data.level3Words)
        canvas.data.nextLevel = 3
    elif canvas.data.level == 3:
        canvas.create_image(canvas.data.canvasWidth/2,
                            top-10,image=canvas.data.master1)
        canvas.create_image(canvas.data.canvasWidth/2,
                            top+50,image=canvas.data.master2)
        canvas.data.nextLevel=1

# displays the counts of each type of trash that was recycled
def displayMaterialCounts(canvas):
    trash = canvas.data.trash
    left = (canvas.data.rightMargin + canvas.data.canvasWidth)/2 - 20 
    top = canvas.data.topMargin + 130
    distanceApart = 60
    for trashType in xrange(len(trash)):
        canvas.create_image(left,top+(trashType*distanceApart),
                            image=trash[trashType])
        canvas.create_text(left+60,top+(trashType*distanceApart),
                           text=str(canvas.data.materialCounts[trashType]),
                           font=("Chalkduster",26),fill="white")

# displays the how to play and exit button on the game screen 
def displayHTPAndExitButton(canvas):
    left = (canvas.data.rightMargin + canvas.data.canvasWidth)/2 
    top1 = canvas.data.bottomMargin - 140
    top2 = top1 + 40
    canvas.create_image(left,top1,image=canvas.data.smallHTP)
    canvas.create_image(left,top2,image=canvas.data.exit)

# draws the shooter on the game screen
def drawShooter(canvas):
    # x coordinate of tip of shooter 
    canvas.data.p1_x = canvas.data.radius*math.cos(canvas.data.radian) + \
                       canvas.data.p2_x
    # y coordinate of tip of shooter
    canvas.data.p1_y = -1*(canvas.data.radius*math.sin(canvas.data.radian)) + \
                       canvas.data.p2_y
    # creater shooter using pivot point and calculated end points
    canvas.create_line(canvas.data.p2_x,canvas.data.p2_y,canvas.data.p1_x,
                       canvas.data.p1_y,fill="goldenrod",width=3)        
    
# sets canvas.data.isGameover to True
def gameOver(canvas):
    canvas.data.isGameOver = True

# piles material type on recycle bin if the required count has been achieved
def pileRecycleBin(canvas):
    for material in xrange(len(canvas.data.materialCounts)):
        # 3 for demo purposes, 10 for actual game
        if canvas.data.materialCounts[material] >= 3:
            if canvas.data.trash[material] not in canvas.data.recycleBin:
                canvas.data.recycleBin += [canvas.data.trash[material]]

# displays left recycle bin on the left with piled trash (if there is any)
def displayRecycleBin(canvas):
    recycleBin = canvas.data.recycleBin
    left = canvas.data.leftMargin/2
    canvas.create_image(left,canvas.data.bottomMargin-40,
                        image=canvas.data.bin)
    for trashType in xrange(len(recycleBin)):
        canvas.create_image(left,canvas.data.bottomMargin-80-(40*(trashType)),
                            image=recycleBin[trashType])
    # if all trash types are piled on recycle bin, go on to the next level
    if len(canvas.data.recycleBin) == 5:
        successfulGame(canvas)
        addtoHighScores(canvas)

# sets canvas.data.isSuccessfulGame to True
def successfulGame(canvas):
    canvas.data.isSuccessfulGame = True
    
# draws the garbage can and the next trash on the right of the game screen
def drawNextTrash(canvas):
    canvas.create_image(canvas.data.rightMargin+85,
                        canvas.data.bottomMargin+30,
                        image=canvas.data.trashCan)
    canvas.create_image(canvas.data.p4_x,canvas.data.p4_y-30,
                        image=canvas.data.trash[canvas.data.nextTrash])
    
# draws the current trash at the bottom of the shooter
def drawCurrentTrash(canvas):
    canvas.create_image(canvas.data.p3_x,canvas.data.p3_y,
                        image=canvas.data.trash[canvas.data.currentTrash])

# displays the score and level on the top right of the game screen 
def displayScoreAndLevel(canvas):
    canvasWidth = canvas.data.canvasWidth
    canvas.create_text((canvasWidth+canvas.data.rightMargin)/2,
                        canvas.data.topMargin+60,
                        text= "Score: " + str(canvas.data.score),
                        font=("Chalkduster",24,"bold"),fill="OliveDrab3")
    canvas.create_text((canvasWidth+canvas.data.rightMargin)/2,
                        canvas.data.topMargin+30,
                       text= "Level: " + str(canvas.data.level),
                       font=("Chalkduster",22),fill="goldenrod")

# keeps finished game score in highScores array under certain conditions
def addtoHighScores(canvas):
    highScores = canvas.data.highScores
    if canvas.data.score not in highScores:
        highScores += [canvas.data.score]
    # remove scores that are less than or equal to 0
    if canvas.data.score <= 0:
        highScores.pop()
    if len(highScores) > 3: # removes minimum score in highScores array
        highScores.remove(min(highScores))
    # sorts highScores array from greatest to least
    highScores.sort()
    highScores.reverse() 
    canvas.data.highScores = highScores
    
# draws game board
def drawTrashBlaster(canvas):
    canvas.create_image(0,0,image=canvas.data.bg,anchor=NW)
    canvas.create_rectangle(canvas.data.leftMargin,canvas.data.topMargin,
                            canvas.data.rightMargin,canvas.data.bottomMargin,
                            outline="goldenrod",width=2)
    board = canvas.data.board
    rows,cols = canvas.data.rows,canvas.data.cols
    # iterate through every row and col in board,
    for row in xrange(rows):
        for col in xrange(cols):
            # for every trash (#) on the board, draw it
            if board[row][col] != -1:
                drawTrash(canvas,board,row,col,board[row][col])
    
def drawTrash(canvas,board,row,col,pic):
    board = canvas.data.board
    cellSize = canvas.data.cellSize
    left = canvas.data.leftMargin + (cellSize * col) + cellSize/2
    top = canvas.data.topMargin + (cellSize * row) + cellSize/2
    if (canvas.data.topRow == 0): # when top row is indented to the left
        if row%2 == 0: # for even rows indented to the left
            canvas.create_image(left,top,image=canvas.data.trash[pic])
        else: # for odd rows indented to the right
            canvas.create_image(left+(cellSize/2),top,
                                image=canvas.data.trash[pic])
    elif (canvas.data.topRow == 1): # when top row is indented to the right
        if row%2 == 0: # for even rows indented to the right
            canvas.create_image(left+(cellSize/2),top,
                                image=canvas.data.trash[pic])
        else: # for odd rows indted to the left 
            canvas.create_image(left,top,image=canvas.data.trash[pic])        
    
# redraws the game board 
def gameRedrawAll(canvas):
    left = (canvas.data.leftMargin+canvas.data.rightMargin)/2
    top = canvas.data.topMargin+75
    if canvas.data.isHomeScreen == False:
        if (canvas.data.isGameOver == True):
            canvas.create_image(left,top,image=canvas.data.gameover)
            canvas.create_image(left,top+70,image=canvas.data.master2)
            displayStatWindow(canvas)
        elif (canvas.data.isSuccessfulGame == True):
            displayWordsForEndOfLevel(canvas)
            displayStatWindow(canvas)
        else:
            canvas.delete(ALL)
            drawTrashBlaster(canvas)
            drawShooter(canvas)
            displayRecycleBin(canvas)
            displayMaterialCounts(canvas)
            pileRecycleBin(canvas)
            displayScoreAndLevel(canvas)
            displayHTPAndExitButton(canvas)
            drawCurrentTrash(canvas)
            drawNextTrash(canvas)
            if canvas.data.isPaused == True:
                canvas.create_image(left,top,image=canvas.data.paused)
                displayStatWindow(canvas)
    
# sets canvas.data.board initially with 4 rows of 
# of random values from canvas.data.trash
def loadGameBoard(canvas):
    board = []
    initialNumRows = 4
    for row in xrange(canvas.data.rows):
        board += [[-1]*canvas.data.cols]
    canvas.data.board = board
    for row in xrange(initialNumRows):
        for col in xrange(canvas.data.cols):
            indexTrash = random.randint(0,len(canvas.data.trash)-1)
            board[row][col] = indexTrash

def init(canvas):
    # loading various gifs for the program
    canvas.data.gameover = PhotoImage(file="gameover.gif")
    canvas.data.paused = PhotoImage(file="paused.gif")
    canvas.data.plastic = PhotoImage(file="plasticBottle.gif")
    canvas.data.paper = PhotoImage(file="Newspaper.gif")
    canvas.data.glass = PhotoImage(file="beer-bottles-case.gif")
    canvas.data.metal = PhotoImage(file="soda.gif")
    canvas.data.electronic = PhotoImage(file="laptop.gif")
    canvas.data.bin = PhotoImage(file="recycleBin.gif")
    canvas.data.trashCan = PhotoImage(file="oscar.gif")
    canvas.data.level2Words = PhotoImage(file="level2.gif")
    canvas.data.level3Words = PhotoImage(file="level3.gif")
    canvas.data.master1 = PhotoImage(file="master1.gif")
    canvas.data.master2 = PhotoImage(file="master2.gif")
    canvas.data.smallHTP = PhotoImage(file="smallHowToPlay.gif")
    canvas.data.exit = PhotoImage(file="exit.gif")
    canvas.data.chalkboard = PhotoImage(file="chalkboard.gif")
    canvas.data.trash = [canvas.data.plastic,\
                         canvas.data.paper, \
                         canvas.data.glass,\
                         canvas.data.metal,\
                         canvas.data.electronic]
    canvas.data.countPlastic = 0
    canvas.data.countGlass = 0
    canvas.data.countMetal = 0
    canvas.data.countElec = 0
    canvas.data.countPaper = 0
    canvas.data.materialCounts = [canvas.data.countPlastic,\
                                  canvas.data.countPaper,\
                                  canvas.data.countGlass,\
                                  canvas.data.countMetal,\
                                  canvas.data.countElec]
    canvas.data.p2_x = 290 # pivot x coordinate of shooter
    canvas.data.p2_y = 670 # pivot y coordinate of shooter
    canvas.data.p3_initX = 290 # initial x coordinate of current trash
    canvas.data.p3_initY = 670 # initial y coordinate of current trash
    # moving x coordinate of current trash
    canvas.data.p3_x = canvas.data.p3_initX 
    # moving x coordinate of current trash
    canvas.data.p3_y = canvas.data.p3_initY 
    # next trash x coordinate
    canvas.data.p4_x = (canvas.data.canvasWidth+canvas.data.rightMargin)/2-39  
    canvas.data.p4_y = canvas.data.bottomMargin+15 # next trash y coordinate
    canvas.data.radius = 100
    canvas.data.radian = (math.pi)/2 # radian of the shooter
    canvas.data.tRadian = (math.pi)/2 # radian of the moving trash
    canvas.data.currentTrash = random.randint(0,len(canvas.data.trash)-1)
    canvas.data.nextTrash = random.randint(0,len(canvas.data.trash)-1)
    canvas.data.score = 0
    canvas.data.isHomeScreen = False
    canvas.data.isSuccessfulGame = False
    canvas.data.isGameOver = False
    canvas.data.recycleBin = []
    canvas.data.level = canvas.data.nextLevel
    canvas.data.displayHighScores = False
    canvas.data.totalPause = 0
    loadGameBoard(canvas)
    clearDepths(canvas)
    gameRedrawAll(canvas)

def homeScreen(canvas):
    canvas.create_image(0,0,image=canvas.data.bg,anchor=NW)
    canvas.create_image(canvas.data.canvasWidth/2,200,
                        image=canvas.data.welcome)
    canvas.create_image(canvas.data.canvasWidth/2,300,
                        image=canvas.data.title)
    canvas.create_image(canvas.data.canvasWidth/2,500,
                        image=canvas.data.startPlayingB)
    canvas.create_image(canvas.data.canvasWidth/2,550,
                        image=canvas.data.howToPlayB)

def howToPlay(canvas):
    canvas.delete(ALL)
    canvas.create_image(0,0,image=canvas.data.bg,anchor=NW)
    canvas.create_text(canvas.data.canvasWidth/2,75,
                       text="Recycling is an important habit to develop in order to",
                       fill="OliveDrab3",font=("Chalkduster",19))
    canvas.create_text(canvas.data.canvasWidth/2,100,
                       text="achieve a more sustainable Earth. Children can develop",
                       fill="OliveDrab3",font=("Chalkduster",19))
    canvas.create_text(canvas.data.canvasWidth/2,125,
                       text="these skills at an early age by playing TrashBlaster!",
                       fill="OliveDrab3",font=("Chalkduster",19))
    canvas.create_text(canvas.data.canvasWidth/2,150,
                       text="The rules are simple:",
                       fill="OliveDrab3",font=("Chalkduster",19))
    canvas.create_text(canvas.data.canvasWidth/2,200,
                       text="Use the 'left' & 'right' arrow keys to rotate the shooter.",
                       fill="goldenrod",font=("Chalkduster",20))
    canvas.create_text(canvas.data.canvasWidth/2,250,
                       text="Press the spacebar to shoot the trash.",
                       fill="goldenrod",font=("Chalkduster",20))
    canvas.create_text(canvas.data.canvasWidth/2,300,
                       text="Score points by recycling at least 3 objects of the same type!",
                       fill="goldenrod",font=("Chalkduster",18))
    canvas.create_text(canvas.data.canvasWidth/2,350,
                       text="Recycle 10 of each type (paper, plastic, electronic,",
                        fill="goldenrod",font=("Chalkduster",20))
    canvas.create_text(canvas.data.canvasWidth/2,375,
                       text="glass and metal) to move onto the next level!",
                       fill="goldenrod",font=("Chalkduster",20))
    canvas.create_text(canvas.data.canvasWidth/2,425,
                       text="Press 'p' to pause, 'r' to restart or 'q' to quit the game.",
                       fill="goldenrod",font=("Chalkduster",20))
    canvas.create_image(canvas.data.canvasWidth/2,525,
                        image=canvas.data.startPlayingB)

def loadHomeScreen(canvas):
    canvas.delete(ALL)
    canvas.data.bg = PhotoImage(file="recycleBG.gif")
    canvas.data.welcome = PhotoImage(file="welcome.gif")
    canvas.data.title = PhotoImage(file="tbtitle.gif")
    canvas.data.startPlayingB = PhotoImage(file="startPlaying.gif")
    canvas.data.howToPlayB = PhotoImage(file="howToPlay.gif")
    canvas.data.canvasWidth = 650
    canvas.data.canvasHeight = 700
    canvas.data.isGameOver = True
    canvas.data.isSuccessfulGame = True
    canvas.data.isShooting = False
    canvas.data.cols = 9
    canvas.data.rows = 14
    canvas.data.cellSize = 40
    canvas.data.howToPlay = False
    canvas.data.isPaused = False
    canvas.data.topRow = 0 # top row is indented to the left
    canvas.data.nextLevel = 1
    canvas.data.leftMargin = 100
    canvas.data.rightMargin = 480
    canvas.data.topMargin = 5
    canvas.data.bottomMargin = 566
    canvas.data.level = canvas.data.nextLevel
    homeScreen(canvas)

def run():
    # create the root and the canvas
    root = Tk()
    canvasWidth = 650
    canvasHeight = 700
    canvas = Canvas(root, width=canvasWidth, height=canvasHeight)
    canvas.pack()
    # Store canvas in root and in canvas itself for callbacks
    root.resizable(width=False, height=False)
    root.canvas = canvas.canvas = canvas
    # Set up canvas data
    class Struct: pass
    canvas.data = Struct()
    canvas.data.isGameOver = True
    canvas.data.canvasWidth = 650
    canvas.data.canvasHeight = 700
    canvas.data.isPaused = False
    canvas.data.isShooting = False
    canvas.data.isSuccessfulGame = True
    canvas.data.highScores = []
    canvas.data.cellSize = 40
    canvas.data.level = 1
    canvas.data.isHomeScreen = True
    addLineTimerFired(canvas)
    shootTimerFired(canvas)
    loadHomeScreen(canvas)
    # set up events
    root.bind("<Button-1>", lambda event: mousePressed(canvas,event))
    root.bind("<Key>", lambda event: keyPressed(canvas,event))
    root.mainloop()  # BLOCKS (program waits until you close the window!)
   
run()