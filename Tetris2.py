# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license
import random, time, pygame, sys, copy
from pygame.locals import *
#awesomeweights = [-0.034704844360260084, 0.05891846092397469, -0.15570194128016532, -0.06833823623848678]
awesomeweights = [-0.19567054051713773, 0.4646625751995018, -0.003907222955622618, -0.8603928073654508]
weighting = [1, 2, 3 ,4]
FPS = 25
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '.'

MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.1

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS      = (     BLUE,      GREEN,      RED,      YELLOW)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
assert len(COLORS) == len(LIGHTCOLORS) # each color must have light color

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}

#function that runs at the start of the game.
def main():
    #idgaf
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetromino')
    #opening screen
    showTextScreen('Tetromino')
    #calls the weighting variable
    global weighting
    #creates a set of trained weights
    #bob = train(10, 10);
    #set's trained weights to global weights
    weighting = awesomeweights;
    while True: # game loop
        #final game, run it, game over, restart
        runGame()
        showTextScreen('Game Over')

def scoreWeights(weights):
    #the sum so far
    sumz = 0;
    global weighting;
    weighting = weights;
    # ^ editing global weights
    #go 5 times, and average out the stuff u get
    for i in range(5):
        score = runGameTest();
        sumz += score;
    return sumz/5;


def runGame():
    # setup variables for the start of the game
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False # note: there is no movingUp variable
    movingLeft = False
    movingRight = False
    score = 0
    level, fallFreq = calculateLevelAndFallFreq(score)

    fallingPiece = getNewPiece()
    nextPiece = getNewPiece()

    while True: # game loop
        if fallingPiece == None:
            # No falling piece in play, so start a new piece at the top
            fallingPiece = nextPiece
            nextPiece = getNewPiece()
            lastFallTime = time.time() # reset lastFallTime
            if not isValidPosition(board, fallingPiece):
                return # can't fit a new piece on the board, so game over
        movePlay = bestMove(fallingPiece, board, 0, nextPiece, True);
        print movePlay
        fallingPiece['rotation'] = movePlay[1];
        while isValidPosition(board, fallingPiece, adjX=-1):
            fallingPiece['x'] -= 1
        fallingPiece['x'] += movePlay[0]
        while isValidPosition(board, fallingPiece, adjY=1):
            fallingPiece['y'] += 1;
        addToBoard(board, fallingPiece)
        score += removeCompleteLines(board)**2
        fallingPiece = None;

  
        # drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(board)
        drawStatus(score, level)
        drawNextPiece(nextPiece)
        if fallingPiece != None:
            drawPiece(fallingPiece)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def runGameTest():
    # setup variables for the start of the game
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False # note: there is no movingUp variable
    movingLeft = False
    movingRight = False
    score = 0;
    blocks = 0;
    level, fallFreq = calculateLevelAndFallFreq(score)

    fallingPiece = getNewPiece()
    nextPiece = getNewPiece()

    while True: # game loop
        if fallingPiece == None:
            # No falling piece in play, so start a new piece at the top
            fallingPiece = nextPiece
            blocks = blocks + 1;
            nextPiece = getNewPiece()
            lastFallTime = time.time() # reset lastFallTime
            if not isValidPosition(board, fallingPiece):
                return blocks + score*10;# can't fit a new piece on the board, so game over
        movePlay = bestMove(fallingPiece, board, 0, nextPiece, False);
        fallingPiece['rotation'] = movePlay[1];
        while isValidPosition(board, fallingPiece, adjX=-1):
            fallingPiece['x'] -= 1
        fallingPiece['x'] += movePlay[0]
        while isValidPosition(board, fallingPiece, adjY=1):
            fallingPiece['y'] += 1;
        addToBoard(board, fallingPiece)
        score += removeCompleteLines(board)
        fallingPiece = None;
        # drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(board)
        drawStatus(score, level)
        drawNextPiece(nextPiece)
        if fallingPiece != None:
            drawPiece(fallingPiece)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()


def checkForKeyPress():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    checkForQuit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def showTextScreen(text):
    # This function displays large text in the
    # center of the screen until a key is pressed.
    # Draw the text drop shadow
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the text
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the additional "Press a key to play." text.
    pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    while checkForKeyPress() == None:
        pygame.display.update()
        FPSCLOCK.tick()


def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def calculateLevelAndFallFreq(score):
    # Based on the score, return the level the player is on and
    # how many seconds pass until a falling piece falls one space.
    level = int(score / 10) + 1
    fallFreq = 0.27 - (level * 0.02)
    return level, fallFreq

def getNewPiece():
    # return a random new piece in a random rotation and color
    shape = random.choice(list(PIECES.keys()))
    newPiece = {'shape': shape,
                'rotation': random.randint(0, len(PIECES[shape]) - 1),
                'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                'y': -2, # start it above the board (i.e. less than 0)
                'color': random.randint(0, len(COLORS)-1)}
    return newPiece


def addToBoard(board, piece):
    # fill in the board based on piece's location, shape, and rotation
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                try:
                    board[x + piece['x']][y + piece['y']] = piece['color']
                except:
                    pass;


def getBlankBoard():
    # create and return a new blank board data structure
    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
    return board

def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


def isValidPosition(board, piece, adjX=0, adjY=0):
    # Return True if the piece is within the board and not colliding
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                return False
    return True

def isCompleteLine(board, y):
    # Return True if the line filled with boxes with no gaps.
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False
    return True


def removeCompleteLines(board):
    # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1 # start y at the bottom of the board
    while y >= 0:
        if isCompleteLine(board, y):
            # Remove the line and pull boxes down by one line.
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pullDownY] = board[x][pullDownY-1]
            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            numLinesRemoved += 1
            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1 # move on to check next row up
    return numLinesRemoved


def convertToPixelCoords(boxx, boxy):
    # Convert the given xy coordinates of the board to xy
    # coordinates of the location on the screen.
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))


def drawBox(boxx, boxy, color, pixelx=None, pixely=None):
    # draw a single box (each tetromino piece has four boxes)
    # at xy coordinates on the board. Or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece).
    if color == BLANK:
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = convertToPixelCoords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def drawBoard(board):
    # draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)

    # fill the background of the board
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    # draw the individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            drawBox(x, y, board[x][y])


def drawStatus(score, level):
    # draw the score text
    scoreSurf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 150, 20)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    # draw the level text
    levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(levelSurf, levelRect)


def drawPiece(piece, pixelx=None, pixely=None):
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    if pixelx == None and pixely == None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])

    # draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shapeToDraw[y][x] != BLANK:
                drawBox(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


def drawNextPiece(piece):
    # draw the "next" text
    nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 120, 80)
    DISPLAYSURF.blit(nextSurf, nextRect)
    # draw the "next" piece
    drawPiece(piece, pixelx=WINDOWWIDTH-120, pixely=100)

def bestMove(piece, board, depth, np, bool):
    bestMovee = -1;
    bestScore = -10000000;
    rot = 0;
    for z in range(len(PIECES[piece['shape']])):
        rot = z;
        myPiece = copy.deepcopy(piece);
        myBoard = copy.deepcopy(board);
        myPiece['rotation'] = z;
        while isValidPosition(myBoard, myPiece, adjX=-1):
            myPiece['x'] -= 1
        counter = 0;
        while isValidPosition(myBoard, myPiece):
            tempPiece = copy.deepcopy(myPiece);
            tempBoard = copy.deepcopy(myBoard);
            while isValidPosition(tempBoard, tempPiece, adjY=1):
                tempPiece['y'] += 1;
            addToBoard(tempBoard, tempPiece);
            if depth == 1 or bool == False:
                score = evaluate(tempBoard);
            else:
                score = bestMove(copy.deepcopy(np), tempBoard, depth + 1, tempPiece, True);
            if score > bestScore:
                bestScore = score;
                bestMovee = [counter, z];
            
            counter += 1;
            myPiece['x'] += 1;
    if depth == 0:
        return bestMovee;
    else:
        return bestScore;

def _calc_height(board):
    aggre_height=0;
    begin = False;
    for i in board:
        begin = False;
        for j in i:
            if j != '.':
                begin = True;
            if begin == True:
                aggre_height+=1;
    return aggre_height;


def _calc_holes(board,aggregate_height_num):
    num_occupied = 0;
    for i in board:
        for j in i:
            if j != '.':
                num_occupied+=1;

    return aggregate_height_num - num_occupied;

def _complete_lines(board):
    #Input: board  
    #Output: num_complete_lines
    num_complete_lines = 0;
    start = False;
    for row in xrange(len(board[0][:])): #gives row num
        start = True; 
        for column in xrange(len(board)):
            if start == True:
                if board[column][row] == '.':
                    start = False;
            else:
                break;
        if start == True:
            num_complete_lines +=1;
    return num_complete_lines;

def _blockiness(board):
    #Input: board
    #Output: return 0 if not blocky. else some integer
    prev = -1; #record height of previous row
    curr_height = 0; 
    blockiness_score = 0;
    begin = False;
    for i in board:
        begin = False;
        curr_height=0;
        for j in i:
            if j != '.':
                begin = True;
            if begin == True:
                curr_height+=1;
        #found curr_height of the row 
        #compare to prev
        if prev != -1:
            blockiness_score+=abs(prev-curr_height);
        prev = curr_height;
    return blockiness_score


def evaluate(board):
    global weighting;
    aggregate_height_num = _calc_height(board);
    a = weighting[0];
    b = weighting[1];
    c = weighting[2];
    d = weighting[3];
    return a*_blockiness(board)+b*_complete_lines(board)**2+c*_calc_holes(board, aggregate_height_num)+d*aggregate_height_num;

def train(genes, evolutions):    
    weights = [];
    #Randomly generates weights
    a = range(4);
    for r in range(len(a)):
        a[r] = 0;
    for r in range(len(a)):
        a[r] = 1;
        weights = weights + [a[:]];
        a[r] = -1;
        weights = weights + [a[:]];
        a[r] = 0;
    # for r in range(genes):
    #     for t in range(len(a)):
    #         a[t] = random.random()*2 - 1;
    #     weights = weights + [a[:]];
    #evolves;
    for i in range(evolutions):
        print "Gen: " + str(i);
        scores = []
        for j in range(len(weights)):
            scr = scoreWeights(weights[j]);
            print scr;
            weights[j] = weights[j] + [scr];
            scores = scores + [scr];
        minz = min(scores);
        for j in range(len(weights)):
            weights[j][4] -= minz;
            scores[j] -= minz;
        sumz = sum(scores);
        for j in range(len(weights)):
            weights[j][4] = float(weights[j][4]) / float(sumz);
            for s in range(len(weights[j]) - 1):
                weights[j][s] *= weights[j][4];
        newWeights = range(4);
        for ji in range(len(newWeights)):
            newWeights[ji] = 0;
        for k in range(len(weights)):
            for l in range(len(newWeights)):
                newWeights[l] += weights[k][l];
        weights.sort(grtr);
        print weights;
        bestWeights = weights[0];
        weights = []
        for b in range(genes):
            weights = weights + [newWeights[:]];
        for g in range(len(weights)):
            for h in range(len(weights[g])):
                weights[g][h] +=  (random.random()*0.4 - 0.2)/(i + 1);
                if weights[g][h] > 1:
                    weights[g][h] = 1;
                elif weights[g][h] < -1:
                    weights[g][h] = -1;
        weights = weights + [bestWeights[:4]];
        print weights;

    for j in range(len(weights)):
        scr = scoreWeights(weights[j]);
        weights[j] = weights[j] + [scr];
    weights.sort(grtr);

    return weights[0];

def grtr(x, y):
    if x[4] < y[4]:
        return 1;
    else:
        return -1;



    #move all the way to the left
    #drop
    #eval

if __name__ == '__main__':
    main()