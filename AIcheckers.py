from typing import Text
import pygame
from pygame import display
from copy import deepcopy
import random
from datetime import datetime

width,height = 700,700

rowcount=8
colcount=8

sqsize=80

white = (243,242,237)
black=(0,0,0)
gray= (119,136,153)
green=(127,255,0)

fps=60 

clock=pygame.time.Clock()

cremetile = pygame.transform.scale(pygame.image.load('creme.jpg'),(80,80))
darktile = pygame.transform.scale(pygame.image.load('dark.jpg'),(80,80))
background=pygame.transform.scale(pygame.image.load('frame.jpg'),(700,700))
crown=pygame.transform.scale(pygame.image.load('crown.png'),(45,22))
whitetransp = pygame.transform.scale(pygame.image.load('white_transp.png'),(600,200))
blacktransp = pygame.transform.scale(pygame.image.load('black_transp.png'),(600,200))
drawtransp=pygame.transform.scale(pygame.image.load('draw_transp.png'),(600,200))

class Piece:
    padding = 13
    outline = 3

    #initializer
    def __init__(self,row,col,color):
        self.row=row
        self.col=col
        self.color=color
        self.isKing=False        
        self.x=0
        self.y=0
        self.selected= False

    #calculate coordinates of position
    def positioncal(self):
        self.x = 30 + sqsize*self.col + sqsize/2
        self.y = 30 + sqsize*self.row + sqsize/2
    
    #make piece a king
    def makeKing(self):
        self.isKing=True

    #change coordinates of piece after oves
    def move(self, newrow, newcol):
        self.row=newrow
        self.col=newcol
        self.positioncal()
    
    #prints the piece onto window
    def print(self,window):
        radius = sqsize/2 - self.padding
        self.positioncal()
        if not self.selected:
            pygame.draw.circle(window, gray , (self.x,self.y),radius + self.outline)
        else:
            pygame.draw.circle(window, green , (self.x,self.y),radius + self.outline)
        pygame.draw.circle(window,self.color,(self.x,self.y), radius)
        if self.isKing:
            window.blit(crown,(self.x-crown.get_width()/2,self.y-crown.get_height()/2))

class Boardstruc:
    #initializer
    def __init__(self):
        self.board = []
        self.selected = None
        self.posmoves = {}
        self.validmovecolor={}
        self.whitepieces=self.blackpieces=12
        self.whitekings=self.blackkings=0
        self.createboard()
    
    #prints the squares onto the board
    def draw_squares(self,window):
        window.blit(background,(0,0))
        for row in range(rowcount):
            for col in range(row%2,rowcount,2):
                window.blit(cremetile,(30+row*sqsize,30+col*sqsize))
                if row%2 == 0:
                    window.blit(darktile,(30+row*sqsize,30+(col+1)*sqsize))
                else:
                    window.blit(darktile,(30+row*sqsize,30+(col-1)*sqsize))
    
    #initializes the starting state of the board
    def createboard(self):
        # i denotes row and j denotes coloumn
        #[[0,w,0,w,0,w,0,w]]
        for i in range(rowcount):
            self.board.append([])
            for j in range(colcount):
                if j%2 == ((i+1)%2):
                    if i<3:
                        self.board[i].append(Piece(i,j,white))
                    elif i>4:
                        self.board[i].append(Piece(i,j,black))
                    else:
                        self.board[i].append(0)
                else:
                    self.board[i].append(0)
            
    def returnpiece(self,row,col):
        return self.board[row][col]

    #evaluate the board state
    def evaluate(self):
        return self.whitepieces-self.blackpieces +(self.whitekings*0.5-self.blackkings*0.5)
    
    def getallpieces(self,color):
        pieces = []
        for row in range(rowcount):
            for col in range(colcount):
                if self.board[row][col]!=0:
                    if self.board[row][col].color==color:
                        pieces.append(self.board[row][col])
        return pieces

    #moves piece to specified row and col
    def move(self,piece,row,col):
        temp = self.board[row][col] 
        self.board[row][col] = self.board[piece.row][piece.col]
        self.board[piece.row][piece.col] = temp
        del temp
        piece.move(row,col)
        piece.selected = False

        if row==(rowcount-1) or row==0:
            if (piece.isKing):
                pass
            else:
                piece.makeKing()
                if piece.color == white:
                    self.whitekings+=1
                else:
                    self.blackkings+=1

    #draws the board onto the window
    def draw(self,window):
        self.draw_squares(window)
        # i denotes row and j denotes coloumn
        for i in range(rowcount):
            for j in range(colcount):
                piece = self.board[i][j]
                if piece!=0:
                    piece.print(window)

    #returns capture moves that can be made by a color
    def returncapturemovesforcolor(self,color,validchecker=[]):
        moves={}
        for i in range(rowcount):
            for j in range(colcount):
                if(self.board[i][j]==0):
                    pass
                elif(self.board[i][j].color==color):
                    moves=self.getposmoves(self.board[i][j])
                    for move in moves:
                        if(len(moves[move])>0):
                            validchecker.append((self.board[i][j].row,self.board[i][j].col))
                            break
        
        return validchecker
    
    #forces the user to capture a piece if there is a oppurtunity available
    def forcecapture(self,piece):
        valid=[]
        valid = self.returncapturemovesforcolor(piece.color,valid)
        if(len(valid)<=0):
            return self.getposmoves(piece)
        else:
            #posmovescopy={}
            #posmovescopy={**self.posmoves}
            keyslist=[]
            if((piece.row,piece.col) in valid):
                self.getposmoves(piece)
                for move in self.posmoves:
                    if(len(self.posmoves[move])<1):
                        keyslist.append(move)
                for move in keyslist:
                    del self.posmoves[move]
                return self.posmoves
            else:
                return {}

    #returns possible moves of a piece by traversing through left and right positions
    def getposmoves(self,piece):
        self.posmoves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == black or piece.isKing:
            self.lefttraverse(row-1,max(row-3,-1),-1,piece.color,left)
            self.righttraverse(row-1,max(row-3,-1),-1,piece.color,right)
        if piece.color == white or piece.isKing:
            self.lefttraverse(row+1,min(row+3,rowcount),1,piece.color,left)
            self.righttraverse(row+1,min(row+3,rowcount),1,piece.color,right)
        
        return self.posmoves           

    def lefttraverse(self,start,stop,step,color,left,skipped= []):
        last = []
        for cr in range(start,stop,step):
            # check off the board or we're back where we started
            if(left<0):
                break
            currentele = self.board[cr][left]
            if currentele==0:  # an empty square
                if skipped and not last: # We've jumped before and not currently
                    break
                elif skipped:
                    self.posmoves[(cr,left)]=last+skipped
                else:
                    self.posmoves[(cr,left)]=last # keeping track of last jumped piece at current new valid square

                if last:# Did we just jump an opponent's piece before landing on valid square?
                    # Check valid moves from current valid square
                    # if selected piece is a king check opposition direction for additional valid moves
                    if step==-1:
                        row=max(cr-3,-1)
                    else:
                        row=min(cr+3,rowcount)
                    self.lefttraverse(cr+step,row,step,color,left-1,skipped=last)
                    self.righttraverse(cr+step,row,step,color,left+1,skipped=last)
                break
            elif currentele.color == color:
                break
            else:
                last = [currentele]  # We're jumping opponent's piece
            
            left-=1
    
    def righttraverse(self,start,stop,step,color,right,skipped=[]):
        last = []
        for cr in range(start,stop,step):
             # if selected piece is a king check opposition direction for additional valid moves
            if(right>=colcount):
                break
            currentele = self.board[cr][right]
            if currentele==0:
                if skipped and not last:
                    break
                elif skipped:
                    self.posmoves[(cr,right)]=last+skipped
                else:
                    self.posmoves[(cr,right)]=last

                if last: # Did we just jump an opponent's piece before landing on valid square?
                    # Check valid moves from current valid square
                    # if selected piece is a king check opposition direction for additional valid moves
                    if step==-1:
                        row=max(cr-3,-1)
                    else:
                        row=min(cr+3,rowcount)
                    self.lefttraverse(cr+step,row,step,color,right-1,skipped=last)
                    self.righttraverse(cr+step,row,step,color,right+1,skipped=last)
                break
            elif currentele.color == color:
                break
            else:
                last = [currentele]
            
            right+=1

    #animates the moves 
    def animateMove(self,color,erow,ecol,srow,scol,window,skipped):
        prow=srow
        pcol=scol
        #cases in which none of pieces are captured
        if not skipped:
            dR=erow-srow
            dC=ecol-scol
            fps=5
            framecount=(abs(dR)+abs(dC))*fps
            self.draw(window)
            print("animation")
            pygame.display.flip()
            pygame.display.update()
            for frame in range(framecount+1):
                r,c=(srow+dR*frame/framecount,scol+dC*frame/framecount)
                self.draw(window)    
                #draw the piece in motion
                newpiece=Piece(r,c,color)
                newpiece.print(window)
                del newpiece
                pygame.display.flip()
                clock.tick(60)  
        #cases in which pieces are captured 
        else:
            for skip in reversed(skipped):
                drow= skip.row-prow
                dcol= skip.col-pcol
                trow= skip.row+drow
                tcol= skip.col+dcol
                dR=trow-prow
                dC=tcol-pcol
                fps=8
                framecount=(abs(dR)+abs(dC))*fps
                self.draw(window)
                print("animation")
                pygame.display.flip()
                pygame.display.update()
                for frame in range(framecount+1):
                    r,c=(prow+dR*frame/framecount,pcol+dC*frame/framecount)
                    self.draw(window)    
                    #draw the piece in motion
                    newpiece=Piece(r,c,color)
                    newpiece.print(window)
                    del newpiece
                    pygame.display.flip()
                    clock.tick(60)
                prow=trow
                pcol=tcol
            
    #removes the piece skipped on by the user during the move
    def removepiece(self,pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece.isKing and piece!=0:
                if piece.color==black:
                    self.blackkings -= 1
                else:
                    self.whitekings -= 1
            if piece!=0:
                if piece.color == black:
                    self.blackpieces -= 1
                else:
                    self.whitepieces -= 1

    #checks if there is a winner by either capturing all the moves
    #or by blocking all the opponent moves
    def winner(self):
        flag = True
        #for white
        for i in range(rowcount):
            for j in range(colcount):
                piece=self.board[i][j]
                if piece!=0:
                    if piece.color== white:
                        if self.getposmoves(piece):
                            flag=False
                            break
            if not flag:
                break
        if flag:
            return "Black"
        flag = True
        #for black
        for i in range(rowcount):
            for j in range(colcount):
                piece=self.board[i][j]
                if piece!=0:
                    if piece.color== black:
                        if self.getposmoves(piece):
                            flag=False
                            break
            if not flag:
                break
        if flag:
            return "White"

        if self.blackpieces<=0:
            return "White"
        elif self.whitepieces<=0:
            return "Black"
        
        return None

    def setselected(self,piece):
        self.selected=piece
        
class gameplay:
    def __init__(self,window):
        self.current = None
        self.board = Boardstruc()
        self.turn = black
        self.possiblemoves={}
        self.window=window
        self.previouswhite = 0
        self.previousblack = 0 
        self.count = 0 
        self.isdraw = False

    #updates the board
    def update(self):
        self.board.draw(self.window)
        self.drawpossiblemoves(self.possiblemoves)
        pygame.display.update()

    #ressts the game
    def reset(self):
        self.current = None
        self.board = Boardstruc()
        self.turn = black
        self.possiblemoves={}
    
    #called by selected tile function to move the piece as well as animate the move
    def move(self,row,col):
        piece=self.board.returnpiece(row,col)
        if self.current and piece==0 and (row,col) in self.possiblemoves:
            srow = self.current.row
            scol = self.current.col
            skipped = self.possiblemoves[(row,col)]
            self.board.animateMove(self.current.color,row,col,srow,scol,self.window,skipped)
            self.board.move(self.current,row,col)            
            if skipped:
                self.board.removepiece(skipped)            
            self.swapturns()
        else:
            return False
        
        return True

    #makes the move returned by the random class
    def randommove(self, piece, row, col):
        dpiece= self.board.returnpiece(row,col)
        posmoves={}
        posmoves = self.board.forcecapture(piece)
        if piece and dpiece==0 and (row,col) in posmoves:
            srow = piece.row
            scol = piece.col
            skipped = posmoves[(row,col)]
            self.board.animateMove(piece.color,row,col,srow,scol,self.window,skipped)
            self.board.move(piece,row,col)            
            if skipped:
                self.board.removepiece(skipped)
            self.swapturns()
        else:
            return False
        
        return True
    
    #swaps turns between the users
    def swapturns(self):
        self.possiblemoves={}
        self.drawcase(self.board.whitepieces,self.board.blackpieces)
        if self.turn==black:
            self.turn=white
        else:
            self.turn=black

    #makes the move from the current tile to the row and coloumn specified
    # checks if the selected tile is valid or not
    def selectedtile(self,row,col):
        if self.current:
            result = self.move(row,col)
            if not result:
                self.current.selected=False
                self.current=None
                self.selectedtile(row,col)
        
        piece = self.board.returnpiece(row,col)
        if piece!=0 and piece.color == self.turn:
            self.current = piece
            self.current.selected=True
            self.possiblemoves = self.board.forcecapture(piece)
            return True
        
        return False
    
    #makrs the moves that can be made by user
    def drawpossiblemoves(self, moves):
        for move in moves:
            row,col=move
            pygame.draw.circle(self.window, green, (30+col*sqsize + sqsize/2,30+row*sqsize + sqsize/2),12)
    
    #return whther there is a winner
    def win(self):
        return self.board.winner()
    
    #returns board for minimax
    def returnboard(self):
        return self.board

    #sets the board according to the choice made by the minimax algorithmn
    def minimaxmove(self, board):
        skippedblack=[]
        for i in range(rowcount):
            for j in range(colcount):
                if board.board[i][j]==0 and self.board.board[i][j]!=0:
                    if self.board.board[i][j].color == black:
                        skippedblack.append((self.board.board[i][j].row,self.board.board[i][j].row))
                    else:
                        piecemoved=self.board.board[i][j]
                if board.board[i][j]!=0 and self.board.board[i][j]==0:
                    endpos=(i,j)
        posmoves=self.board.getposmoves(piecemoved)
        skipped =posmoves[endpos]
        self.board.animateMove(piecemoved.color,endpos[0],endpos[1],piecemoved.row,piecemoved.col,self.window,skipped)     
        self.board=board
        self.swapturns()
    
    #checks the 50 move condition and draws the game if its satisfied
    def drawcase(self, currwhite, currblack):
        if (currwhite==self.previouswhite) and (currblack==self.previousblack):
            self.count+=1
        else:
            self.count = 0
        
        self.previouswhite=currwhite
        self.previousblack=currblack

        print("count ",self.count)
        if self.count >= 50:
            self.isdraw = True
        else:
            self.isdraw = False

#minimax algorithmn for AI
#The strategy followed here is that the computer sends 
# the list of all possible boards to be evaluated and 
# selects the board which has highest possible score
class minimax:
    #function that makes the best possible choice on behalf of the computer
    def minimaxalgo(self,boardstate, depth, shouldmaximize, game):
        if depth==0 or boardstate.winner() != None:
            return boardstate.evaluate(), boardstate
        
        #maximize the computer choice
        if shouldmaximize:
            maxevalyet = float('-inf')
            bestmove = None
            for move in self.getallmoves(boardstate, white, game):
                evaluation = self.minimaxalgo(move, depth-1, False, game)[0]
                maxevalyet= max(maxevalyet,evaluation)
                if maxevalyet == evaluation:
                    bestmove = move
                
            return maxevalyet, bestmove
        #minimize the users advantage
        else:
            minevalyet = float('inf')
            bestmove = None
            for move in self.getallmoves(boardstate, black, game):
                evaluation = self.minimaxalgo(move, depth-1, True, game)[0]
                minevalyet= min(minevalyet,evaluation)
                if minevalyet == evaluation:
                    bestmove = move
                
            return minevalyet, bestmove

    def getallmoves(self,board, color, game):
        moves=[]

        for piece in board.getallpieces(color):
            validmoves = board.forcecapture(piece)
            for move,skip in validmoves.items():
                tempboard = deepcopy(board)
                temppiece = tempboard.returnpiece(piece.row, piece.col)
                self.replicatemove(temppiece, move, tempboard, game,skip)
                moves.append(tempboard)
        
        return moves
    
    def replicatemove(self,piece, move, board, game, skip):
        board.move(piece, move[0], move[1])

        if skip:
            board.removepiece(skip)

class Random:
    def validpieces(self, boardst):
        listofvalidpieces = []
        for i in range(rowcount):
            for j in range(colcount):
                piece = boardst.board[i][j]
                if piece!=0:
                    if piece.color == white:
                        if boardst.forcecapture(piece):
                            listofvalidpieces.append(piece)
        return listofvalidpieces

    def validmovemaker(self, board, game):
        listofpieces= []
        listofpieces= self.validpieces(board)
        l= len(listofpieces)

        random.seed(datetime.now())
        if (l-1)==0:
            index=0
        else:
            index = random.randint(0,l-1)
        piece = listofpieces[index]
        listofmoves = {}
        listofmoves = board.forcecapture(piece)
        l1= len(listofmoves)
        keys=list(listofmoves.keys())
        
        if (l1-1)==0:
            index=0
        else:
            index = random.randint(0,l1-1)
        #{(2,3): [(1,1) [0,1]], (4,4):[(2,3),(1,1),(0,0)]}
        move = keys[index]
        game.randommove(piece,move[0],move[1])
        

def returnmouse(pos):
    x,y=pos
    row= (y-30)//sqsize
    col=(x-30)//sqsize
    return row,col


#All the execution, method calling and choice making happens in this function. 
# This function constantly checks if one of the users has won and
#  updates the board constantly when moves are being made
def main():
    keeprunning = True 
    wincase= False   
        
    m=minimax() 

    ran=Random()

    #take choice of the user
    choice = input("\nEnter \n1. For Random\n2. For Minimax Algorithmn \n3. For Multiplayer\n")

    displaywindow = pygame.display.set_mode((width,height))
    pygame.display.set_caption('Checkers Board')    
    game=gameplay(displaywindow)
    
    while keeprunning:
        #making sure the game is run at 60 fps
        clock.tick(fps)
               
        if game.turn == white and not wincase:
            if choice == "1":
                ran.validmovemaker(game.board,game)
            elif choice=="2":
                value, newboard = m.minimaxalgo(game.returnboard(), 4, white, game)
                game.minimaxmove(newboard)

        #check if the game is draw
        if game.isdraw:
            wincase=True
            pygame.display.flip()
            displaywindow.blit(drawtransp,(50,250))
            print("Its a draw")
            
        #check if the game is won by any of the user
        if game.win() !=None:
            wincase=True
            pygame.display.flip()
            if(game.win()=="White"):
                displaywindow.blit(whitetransp,(50,250))
            else:
                displaywindow.blit(blacktransp,(50,250))
            print(game.win()," wins the game")
        
        #listner for events
        for event in pygame.event.get():
            #close window if close button is pressed
            if event.type == pygame.QUIT:
                keeprunning=False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row,col = returnmouse(pos)
                piece = game.board.returnpiece(row,col)
                print(piece)
                game.selectedtile(row,col)

        #check if the game is won
        if game.win() !=None:
            wincase=True
            pygame.display.flip()
            if(game.win()=="White"):
                displaywindow.blit(whitetransp,(50,250))
            else:
                displaywindow.blit(blacktransp,(50,250))
            print(game.win()," wins the game")

        #check if a draw happens
        if game.isdraw:
            wincase=True
            pygame.display.flip()
            displaywindow.blit(drawtransp,(50,250))
            print("Its a draw")
                
        if not wincase:
            game.update()
    pygame.quit  


main()