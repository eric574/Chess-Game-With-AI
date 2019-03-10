from collections import defaultdict
import move
import widget


# An enumeration class that contains possible chess pieces' colors.
class COLOR:
    BLACK = -1
    WHITE = 1


# An enumeration class that contains possible chess piece types.
class PIECE:
    KING = 1
    QUEEN = 2
    BISHOP = 3
    KNIGHT = 4
    ROOK = 5
    PAWN = 6


# A Piece base class that provides the necessary representation and the interface of classes that will be inherited from this class.
class Piece:
    pieceType = 0
    moves = list()
    
    # An __init__ member function that gets called as the Piece instance is created. It creates the representation of the object.
    def __init__(self, chessboard, color, r, c, image):
        self.chessboard = chessboard
        self.color = color
        self.r = r
        self.c = c
        self.actualR = r
        self.actualC = c
        self.image = image
        self.forward = -chessboard.orientation * color
        self.neverMoved = True
        self.cached = False
        self.lastMoved = -1
        
        self.nextPositions = dict()
        
    # A member function that caches the possible positions of the chess piece.
    def cacheNextPositions(self, disregardCheck=False):
        self.nextPositions = dict()
        self.cached = True
        
        for move in self.moves:
            for position in move.getNextPositions(self.chessboard, self, disregardCheck):
                self.nextPositions[position] = move
                
    # A member function that deletes the cache of the chess piece.
    def deleteCache(self):
        self.nextPositions = dict()
        self.cached = False
        
    # A member function that returns the possible next positions of the piece.
    def getNextPositions(self):
        if not self.cached:
            self.cacheNextPositions()
        
        return self.nextPositions.keys()
        
    # A member function that gets the position of the piece, in the form of cell row and column.
    def getPosition(self):
        return self.r, self.c
    
    # A member function that sets the position of the piece, in the form of cell row and column.
    def setPosition(self, r, c):
        self.r = r
        self.c = c
        
    # A member function that makes a move.
    def move(self, r, c):
        self.nextPositions[r, c].makeMove(self.chessboard, self, r, c)
        self.neverMoved = False
        self.nextPositions = dict()
    
    # A member function that updates the piece. This is unnecessary for most implementation of Piece classes. This runs every time a move is made on the chessboard.
    def update(self):
        pass
    
    # A member function that moves the actual location of the chess piece image.
    def moveImage(self):
        self.actualR += (self.r - self.actualR) * min(1, 15 / frameRate)
        self.actualC += (self.c - self.actualC) * min(1, 15 / frameRate)
        
    # A member function that displays the chess piece.
    def display(self):
        self.moveImage()
        coord = self.chessboard.cellToCoord(self.actualR, self.actualC)
        image(self.image, coord[0], coord[1], 0.95 * self.chessboard.cellWidth, 0.95 * self.chessboard.cellHeight)
        
    # A member function that determines if a piece is vulnerable. Since this will only be invoked in
    # instances of King class (which is inherited from Piece class), it is named "isInCheck".
    def isInCheck(self):
        possibleEnemyPositions = defaultdict(set)
        
        for move_ in move.moves:
            if move_.isCheckable:
                for position in move_.getNextPositions(self.chessboard, self, True):
                    possibleEnemyPositions[position].add(move_)

        for position, moves in possibleEnemyPositions.items():
            for move_ in moves:
                if self.chessboard.isOccupied(*position) and self.chessboard.cellColor(*position) == -self.color and move_ in self.chessboard.get(*position).moves:
                    return position
        
        return None
    
    # A member function that changes the piece into another piece. So far, this is only used for pawn promotion.
    def changeTo(self, chessPiece):
        newChessPiece = numToPiece[abs(chessPiece)](self.chessboard, chessPiece / abs(chessPiece), self.r, self.c, self.chessboard.master.chessPieceImages[chessPiece])
        newChessPiece.neverMoved = False
        newChessPiece.actualR = self.actualR
        newChessPiece.actualC = self.actualC
        self.chessboard.set(self.r, self.c, newChessPiece)
        self.chessboard.master.destroyPopUp()
        self.chessboard.checkForCheck()
        self.chessboard.deleteCache()
        self.chessboard.checkResults()
        self.chessboard.master.sendPromotionToAI(symbols[abs(chessPiece)])


# Implementation of individual piece type classes follow. Each contains possible moves and overrides member function from base Piece class if necessary.


class King(Piece):
    pieceType = PIECE.KING
    moves = [move.Adjacent, move.Castling]
    
    def __init__(self, chessboard, color, r, c, image):
        Piece.__init__(self, chessboard, color, r, c, image)


class Queen(Piece):
    pieceType = PIECE.QUEEN
    moves = [move.RankFile, move.Diagonal]
    
    def __init__(self, chessboard, color, r, c, image):
        Piece.__init__(self, chessboard, color, r, c, image)
    
    
class Bishop(Piece):
    pieceType = PIECE.BISHOP
    moves = [move.Diagonal]
    
    def __init__(self, chessboard, color, r, c, image):
        Piece.__init__(self, chessboard, color, r, c, image)
    
    
class Knight(Piece):
    pieceType = PIECE.KNIGHT
    moves = [move.LJump]
    
    def __init__(self, chessboard, color, r, c, image):
        Piece.__init__(self, chessboard, color, r, c, image)
    
    
class Rook(Piece):
    pieceType = PIECE.ROOK
    moves = [move.RankFile]
    
    def __init__(self, chessboard, color, r, c, image):
        Piece.__init__(self, chessboard, color, r, c, image)
    
    
class Pawn(Piece):
    pieceType = PIECE.PAWN
    moves = [move.Forward, move.DoubleForward, move.ForwardDiagonal, move.EnPassant]
    
    def __init__(self, chessboard, color, r, c, image):
        Piece.__init__(self, chessboard, color, r, c, image)
        
    # This checks if a pawn can be promoted. If so, it creates a pop up that allows the user to choose.
    def update(self):
        if self.r == (0 if self.forward == -1 else self.chessboard.rows - 1) and self.color in self.chessboard.master.settings["playAs"]:
            xC, yC = self.chessboard.cellToCoord(self.r, self.c)
            imageWidth = 0.95 * self.chessboard.cellWidth
            imageHeight = 0.95 * self.chessboard.cellHeight
            cellYOffset = self.chessboard.cellHeight
            fC = color(255) if self.color == COLOR.BLACK else color(0)
            sC = color(0) if self.color == COLOR.BLACK else color(255)
            
            if self.chessboard.master.boardAngle != 0:
                xC = width / 2.0 + (width / 2.0 - xC)
                yC = height / 2.0 + (height / 2.0 - yC)
                cellYOffset *= -1
            
            self.chessboard.master.createPopUp([widget.Rect(width / 2.0, height / 2.0, width, height, color(1, 200), color(1, 200), 0, False), \
                                                widget.Ellipse(xC, yC - self.forward * cellYOffset, self.chessboard.cellWidth, self.chessboard.cellHeight, fC, sC, 5, True), \
                                                widget.Ellipse(xC, yC - self.forward * 2 * cellYOffset, self.chessboard.cellWidth, self.chessboard.cellHeight, fC, sC, 5, True), \
                                                widget.Ellipse(xC, yC - self.forward * 3 * cellYOffset, self.chessboard.cellWidth, self.chessboard.cellHeight, fC, sC, 5, True), \
                                                widget.Ellipse(xC, yC - self.forward * 4 * cellYOffset, self.chessboard.cellWidth, self.chessboard.cellHeight, fC, sC, 5, True), \
                                                widget.ImageButton(xC, yC - self.forward * cellYOffset, imageWidth, imageHeight, \
                                                                   self.chessboard.master.chessPieceImages[self.color * PIECE.QUEEN], lambda: self.changeTo(self.color * PIECE.QUEEN), False), \
                                                widget.ImageButton(xC, yC - self.forward * 2 * cellYOffset, imageWidth, imageHeight, \
                                                                   self.chessboard.master.chessPieceImages[self.color * PIECE.KNIGHT], lambda: self.changeTo(self.color * PIECE.KNIGHT), False), \
                                                widget.ImageButton(xC, yC - self.forward * 3 * cellYOffset, imageWidth, imageHeight, \
                                                                   self.chessboard.master.chessPieceImages[self.color * PIECE.ROOK], lambda: self.changeTo(self.color * PIECE.ROOK), False), \
                                                widget.ImageButton(xC, yC - self.forward * 4 * cellYOffset, imageWidth, imageHeight, \
                                                                   self.chessboard.master.chessPieceImages[self.color * PIECE.BISHOP], lambda: self.changeTo(self.color * PIECE.BISHOP), False)])


# A list that contains piece types that corresponds to the index.
numToPiece = [None,
              King,
              Queen,
              Bishop,
              Knight,
              Rook,
              Pawn]
        
symbols = ["", "k", "q", "b", "n", "r", "p"]

def main():
    print("Please run the Chess_by_Eric_Liu.pyde file to run the program.")


if __name__ == "__main__":
    main()
