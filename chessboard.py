from copy import deepcopy
import piece
import move
import variant
import chess
import widget


# A RESULT enumeration class that holds the possible results.
class RESULT:
    BLACK = -1
    STALEMATE = 0
    WHITE = 1
    UNDETERMINED = 2


# A Chessboard class that controls each pieces.
class Chessboard:
    # An __init__ member function that gets called when a Chessboard instance is created. It creates the representation of the object.
    def __init__(self, master=None, x=0, y=0, w=0, h=0, orientation=1, variant=variant.Standard, copyFrom=None):
        self.master = master
        self.orientation = orientation
        self.variant = variant
        self.turn = piece.COLOR.WHITE
        self.copyFrom = copyFrom
        self.isTemporary = copyFrom is not None
        self.count = 1
        
        self.createChessboard()
        
        if not self.isTemporary:  # If it is just created just to check if the move cause enemy check, there is no need to create unneccesarily member variables.
            self.alpha = "abcdefghijklmnopqrstuvwxyz"
            self.x = x
            self.xL = x - w / 2.0
            self.xR = x + w / 2.0
            self.y = y
            self.yU = y - h / 2.0
            self.yD = y + h / 2.0
            self.w = w
            self.h = h
            self.selected = None
            self.highlighted = None
            self.result = RESULT.UNDETERMINED
            self.isInCheck = False
            
            self.calculateGeometry()
            self.getColors()
            self.checkResults()
        
    # A member function that creates the chessboard using the variant chosen by the user.
    def createChessboard(self):
        self.chessboard = self.variant.getChessboard(self) if not self.isTemporary else self.copyChessboard(self.copyFrom)
        self.rows = self.variant.rows
        self.cols = self.variant.cols
        
        self.vulnerabilityTable = [[False] * self.cols for r in xrange(self.rows)]
        
        if not self.isTemporary:
            self.alertTable = [[False] * self.cols for r in xrange(self.rows)]
            self.hintTable = [[False] * self.cols for r in xrange(self.rows)]
            self.effectTable = [[False] * self.cols for r in xrange(self.rows)]
            self.history = list()

    # A member function that returns a copy of the chessboard matrix.
    def copyChessboard(self, other):
        chessboard = [[None] * other.cols for r in xrange(other.rows)]

        for r in xrange(other.rows):
            for c in xrange(other.cols):
                if other.isOccupied(r, c):
                    chessboard[r][c] = piece.numToPiece[other.get(r, c).pieceType](self, other.cellColor(r, c), r, c, None) 

        return chessboard
        
    # A member function that calculates the cell width and height of the chessboard.
    def calculateGeometry(self):
        self.cellWidth = float(self.w) / self.cols
        self.cellHeight = float(self.h) / self.rows
        
    # A member function that creates the color representation based on the game's selected theme.
    def getColors(self):
        if self.master is not None:
            if self.master.settings["theme"] == chess.THEME.CLASSIC:
                self.color1 = color(153, 102, 51)
                self.color2 = color(255, 204, 153)
                self.borderColor = color(102, 51, 0)
            elif self.master.settings["theme"] == chess.THEME.MODERN:
                self.color1 = color(255,255,240)
                self.color2 = color(105)
                self.borderColor = color(0)
        
    # A member frunction that converts from mouse coordinates to the cell row and column.
    def coordToCell(self, x, y):  # Here, (0, 0) is the top left of the chessboard.
        r = int(float(y - self.yU) / self.h * self.rows)
        c = int(float(x - self.xL) / self.w * self.cols)
        return r, c
    
    # A member function that converts from the cell row and column to mouse coordinates.
    def cellToCoord(self, r, c):  # Here, (0, 0) is the top left of the chessboard. 
        x = (c + 0.5) * self.cellWidth + self.xL
        y = (r + 0.5) * self.cellHeight + self.yU
        return x, y
    
    # A member function that converts from cell row and column to chess position notation.
    def cellToPos(self, r, c):
        if self.orientation == 1:
            return self.alpha[c], str(self.rows - r)
        else:
            return self.alpha[self.cols - c - 1], str(r + 1)
        
    # A member function that converts from chess position notation to cell row and column.
    def posToCell(self, a, n):
        n = int(n)
        if self.orientation == 1:
            return self.rows - n, self.alpha.index(a)
        else:
            return n - 1, self.cols - self.alpha.index(a) - 1
        
    # A member function that determines if the chessboard contains the passed coordinates.
    def containsCoord(self, x, y):
        return self.xL <= x < self.xR and self.yU <= y < self.yD
    
    # A member function that determines of the chessboard contains a cell.
    def containsCell(self, r, c):
        return self.variant.isValidPosition(r, c)
    
    # A member function that determines if a cell in the chessboard is occupied by a piece.
    def isOccupied(self, r, c):
        return self.chessboard[r][c] is not None    
    
    # A member function that determines if a cell in the chessboard is empty (unoccupied by any piece).
    def isEmpty(self, r, c):
        return self.chessboard[r][c] is None
    
    # A member function that returns the color of the piece occupying a particular cell. If unoccupied, it returns 0.
    def cellColor(self, r, c):
        return 0 if self.chessboard[r][c] is None else self.chessboard[r][c].color
        
    # A member function that gets the piece from a cell of the chessboard.
    def get(self, r, c):
        return self.chessboard[r][c]
        
    # A member function that sets a cell to a piece value in a chessboard.
    def set(self, r, c, piece):
        self.chessboard[r][c] = piece
        
    # A member function that, based on the first and second location, determines of a path is obstructed or not
    def obstructed(self, r1, c1, r2, c2):
        if r1 == r2:
            step = 1 if c1 < c2 else -1
            
            r = r1
            for c in xrange(c1 + step, c2, step):
                if self.chessboard[r][c] is not None:
                    return True
        elif c1 == c2:
            step = 1 if r1 < r2 else -1
            
            c = c1
            for r in xrange(r1 + step, r2, step):
                if self.chessboard[r][c] is not None:
                    return True
        else:
            rStep = 1 if r1 < r2 else -1
            cStep = 1 if c1 < c2 else -1
            
            for r, c in zip(xrange(r1 + rStep, r2, rStep), xrange(c1 + cStep, c2, cStep)):
                 if self.chessboard[r][c] is not None:
                     return True
        
        return False
    
    # A member function that clears the table that flags all the cells that can be attacked.
    def clearVulnerabilityTable(self):
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                self.vulnerabilityTable[r][c] = False
                
    # A member function that caches the next positions of all possible pieces.
    def cacheNextPositions(self, disregardCheck=False):
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                if self.chessboard[r][c] is not None:
                    self.chessboard[r][c].cacheNextPositions(disregardCheck)
                    
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                if self.isOccupied(r, c) and self.chessboard[r][c].color == self.turn:
                    for nextPosition in self.chessboard[r][c].getNextPositions():
                        if self.chessboard[r][c].nextPositions[nextPosition].isCheckable:
                            self.vulnerabilityTable[nextPosition[0]][nextPosition[1]] = True
                    
    # A member function that finds the cell occupied by a King piece of a particular color.
    def getKingCell(self, color):
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                if self.isOccupied(r, c) and self.cellColor(r, c) * self.chessboard[r][c].pieceType == color * piece.PIECE.KING:
                    return r, c
        return None
    
    # A member function that determines if a cell is vulnerable or not (can be attacked).
    def isVulnerable(self, r, c):
        return self.vulnerabilityTable[r][c]
                    
    # A member function that returns a copy the chessboard object.
    def copy(self):
        newBoard = Chessboard(orientation=self.orientation, variant=self.variant, copyFrom=self)
        newBoard.turn = self.turn
        newBoard.count = self.count
        return newBoard
        
    # A member function that displays the chessboard.
    def display(self):
        pushMatrix()
        pushStyle()
        self.displayFrame()
        self.displayCells()
        self.displayPieces()
        self.displayAlerts()
        self.displayEffects()
        self.displayHints()
        self.displayHighlight()
        popStyle()
        popMatrix()
        
    # A member function that displays the frame of the chessboard.
    def displayFrame(self):
        fill(self.borderColor)
        stroke(self.borderColor)
        strokeWeight(50)
        rect(self.x, self.y, self.w, self.h)
        
    # A member function that displays all the individual cells of the chessboard.
    def displayCells(self):
        strokeWeight(0)
        
        for r in xrange(self.rows):
            for c in xrange(self.rows):
                if r + c & 1:
                    fill(self.color1)
                    stroke(self.color1)
                else:
                    fill(self.color2)
                    stroke(self.color2)
                
                coord = self.cellToCoord(r, c)
                
                rect(coord[0], coord[1], self.cellWidth, self.cellHeight)
                
    # A member function that displays all the pieces on the board.
    def displayPieces(self):
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                if self.isOccupied(r, c):
                    self.get(r, c).display()
                    
    # A member function that displays the alerted cells on the board.
    def displayAlerts(self):
        strokeWeight(0)
        
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                if self.alertTable[r][c]:
                    self.alertTable[r][c] = max(100, self.alertTable[r][c] - 255 / frameRate)
                    
                    fill(255, 0, 0, self.alertTable[r][c])
                    stroke(255, 0, 0, self.alertTable[r][c])
                    x, y = self.cellToCoord(r, c)
                    rect(x, y, self.cellWidth, self.cellHeight)
        
    # A member function that displays the possible moves of a selected piece. It does not display anything if no piece is selected.
    def displayHints(self):
        fill(0, 255, 0, 100)
        stroke(0, 255, 0, 100)
        strokeWeight(0)
        
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                if self.hintTable[r][c]:
                    x, y = self.cellToCoord(r, c)
                    rect(x, y, self.cellWidth, self.cellHeight)
        
    # A member function that displays the board's effects.
    def displayEffects(self):
        strokeWeight(0)

        for r in xrange(self.rows):
            for c in xrange(self.cols):
                if self.effectTable[r][c]:
                    self.effectTable[r][c] = max(0, self.effectTable[r][c] - 255 / frameRate)
                    fill(0, 0, 255, self.effectTable[r][c])
                    stroke(0, 0, 255, self.effectTable[r][c])
                    
                    x, y = self.cellToCoord(r, c)
                    rect(x, y, self.cellWidth, self.cellHeight)
                    
    # A member function that displays the highlight a highlighted cell on the board.
    def displayHighlight(self):
        if self.highlighted is not None:
            x, y = self.cellToCoord(*self.highlighted)
            fill(1, 50)
            stroke(1, 50)
            noStroke()
            rect(x, y, self.cellWidth, self.cellHeight)
                    
    # A member function that selects a cell for highlighting.
    def highlight(self, r, c):
        self.highlighted = r, c
        
    # A member function that deselects a highlighted cell.
    def dehighlight(self):
        self.highlighted = None
    
    # A member function that clears all the alerts on the board.
    def clearAlerts(self):
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                self.alertTable[r][c] = False
                
    # A member function that clears the hints (possible next moves) on the board.
    def clearHints(self):
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                self.hintTable[r][c] = False
                
    # A member function that creates an effect on a cell.
    def createEffect(self, r, c):
        self.effectTable[r][c] = 255
    
    # A member function that creates an alert on a cell.
    def createAlert(self, r, c):
        self.alertTable[r][c] = 255
      
    # A member function that selects a cell. If the cell is occupied, its possible next moves are marked in the hintTable member variable.
    def select(self, r, c):
        self.clearHints()
        
        if self.cellColor(r, c) == self.turn and (r, c) != self.selected:
            self.selected = r, c
    
            if self.isOccupied(r, c):
                nextPositions = self.get(r, c).getNextPositions()
                
                for r, c in nextPositions:
                    self.hintTable[r][c] = True
        else:
            self.selected = None

    # A member function that makes a move in the chesstable.
    def makeMove(self, r, c):
        self.recordMove(r, c)
        self.get(*self.selected).lastMoved = self.count
        self.get(*self.selected).move(r, c)
        self.update()
        
    # A member function that records a move in the history member variable.
    def recordMove(self, r, c):
        record = {
                "from": self.selected,
                "to": (r, c),
                "move": self.get(*self.selected).nextPositions[r, c],
                "chessPiece": self.get(*self.selected),
                "captured": self.get(r, c)
                }
        
        self.history.append(record)
        
    # A member function that updates all the pieces on the chessboard.
    def updatePieces(self):
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                if self.isOccupied(r, c):
                    self.get(r, c).update()

    # A member function that updates the chessboard. This is called after each move.
    def update(self):
        self.clearVulnerabilityTable()
        self.turn *= -1
        
        if not self.isTemporary:
            self.deleteCache()
            self.clearAlerts()
            self.clearHints()
            self.count += 1
            self.updatePieces()
            self.checkForCheck()
            self.checkResults()
            self.master.takeCareOfMove(self.history[-1])
            
    # A member function that checks if a king is in check.
    def checkForCheck(self):
        self.isInCheck = False
        kingCell = self.getKingCell(self.turn)
        if kingCell is not None:
            checkingPieceCell = self.get(*kingCell).isInCheck()
            if checkingPieceCell is not None:
                self.createAlert(*kingCell)
                self.createAlert(*checkingPieceCell)
                self.isInCheck = True
        
    # A member function that counts the pieces of each color.
    def getChessPieceCount(self):
        self.numPieces = {
                          piece.COLOR.BLACK: 0,
                          piece.COLOR.WHITE: 0
                          }
        
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                if self.isOccupied(r, c):
                    self.numPieces[self.cellColor(r, c)] += 1
                    
    # A member function that checks if the game is finished, as the king is checkmated or there is a draw.
    def checkResults(self):
        self.getChessPieceCount()
        
        if self.numPieces[piece.COLOR.BLACK] == 0 and self.numPieces[piece.COLOR.WHITE] == 0:
            self.result = RESULT.STALEMATE
        elif self.numPieces[piece.COLOR.BLACK] == 0:
            self.result = RESULT.WHITE
        elif self.numPieces[piece.COLOR.WHITE] == 0:
            self.result = RESULT.BLACK
        
        if self.result == RESULT.UNDETERMINED:
            hasNoValidMove = not self.canMakeMove()
    
            if hasNoValidMove and self.isInCheck:
                self.result = -self.turn
            elif hasNoValidMove:
                self.result = RESULT.STALEMATE
            
        if self.result != RESULT.UNDETERMINED:
            self.createResultPopUp()
            
    # A member function that creates a pop up notifying that the game is over and displaying the results.
    def createResultPopUp(self):
        if self.result == RESULT.BLACK:
            heading = "Black Wins!"
        elif self.result == RESULT.WHITE:
            heading = "White Wins!"
        else:
            heading = "Stalemate"
        
        self.master.createPopUp([widget.Rect(width / 2.0, height / 2.0, width, height, color(1, 200), color(1, 200), 0, False), \
                    widget.TXT(width / 2.0, self.master.yUnit * 2, heading, 1 * self.master.yUnit, color(255), False), \
                    widget.Button(width / 2.0, height / 2.0, 5 * self.master.xUnit, 1.5 * self.master.yUnit, "Return to Menu", 0.7 * self.master.yUnit, color(0), \
                                color(255, 200), color(0), 5, lambda: self.master.destroyPopUp() or self.master.switchTo(chess.GUI.MAIN), True)])
            
    # A member function that returns if it a player is able to make a move.
    def canMakeMove(self):
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                if self.cellColor(r, c) == self.turn:
                    if len(self.get(r, c).getNextPositions()):
                        return True
        return False
    
    # A member function that deletes all the cached moves.
    def deleteCache(self):
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                if self.isOccupied(r, c):
                    self.get(r, c).deleteCache()
    
    # A member function that invokes different member function based on the coordinates where the action occurred (as in mouse being pressed).
    def actionAtCoord(self, x, y, status):
        if self.result != RESULT.UNDETERMINED: return

        r, c = self.coordToCell(x, y)
        
        if self.hintTable[r][c]:
            self.makeMove(r, c)
        elif status:
            self.select(r, c)
    
    # A member function that instantly selects a piece
    def instantlyMakeMove(self, r1, c1, r2, c2):
        self.select(r1, c1)
        self.makeMove(r2, c2)


def main():
    print("Please run the Chess_by_Eric_Liu.pyde file to run the program.")


if __name__ == "__main__":
    main()
