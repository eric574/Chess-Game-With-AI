import piece
from copy import deepcopy


# A Variant base class that provides a representation and interface of each classes that will be inherited from this class.
class Variant:
    rows = 0
    cols = 0
    template = list()
    
    # A class method that returns the chessboard matrix built from the variant template.
    @classmethod
    def getChessboard(cls, board):
        template = deepcopy(cls.template)
        
        if board.orientation == -1:
            template.reverse()
            for row in template:
                row.reverse()
        
        chessboard = [[None] * cls.cols for r in xrange(cls.rows)]
        
        for r in xrange(cls.rows):
            for c in xrange(cls.cols):
                if template[r][c]: 
                    chessboard[r][c] = piece.numToPiece[abs(template[r][c])](board, template[r][c] / abs(template[r][c]), r, c, board.master.chessPieceImages[template[r][c]] if board.master is not None else None)
                    
        return chessboard
    
    # A class method that determines if a position is valid position on the board. 
    @classmethod
    def isValidPosition(cls, r, c):
        return 0 <= r < cls.rows and 0 <= c < cls.cols


# Implementation of individual variant type classes follow. Each contains templates and overrides member function from base Variant class if necessary.
                

class Standard(Variant):
    rows = 8
    cols = 8
    template = [[-5, -4, -3, -2, -1, -3, -4, -5],
                [-6, -6, -6, -6, -6, -6, -6, -6],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [6, 6, 6, 6, 6, 6, 6, 6],
                [5, 4, 3, 2, 1, 3, 4, 5]]


class Horde(Variant):
    rows = 8
    cols = 8
    template = [[-5, -4, -3, -2, -1, -3, -4, -5],
                [-6, -6, -6, -6, -6, -6, -6, -6],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 6, 6, 0, 0, 6, 6, 0],
                [6, 6, 6, 6, 6, 6, 6, 6],
                [6, 6, 6, 6, 6, 6, 6, 6],
                [6, 6, 6, 6, 6, 6, 6, 6],
                [6, 6, 6, 6, 6, 6, 6, 6]]
    
    
class Chess960(Variant):
    rows = 8
    cols = 8
    template = [[-5, -4, -3, -2, -1, -3, -4, -5],
                [-6, -6, -6, -6, -6, -6, -6, -6],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [6, 6, 6, 6, 6, 6, 6, 6],
                [5, 4, 3, 2, 1, 3, 4, 5]]
        
    # Chess960 shuffles the back row, so the "getChessboard" class method needs to be overridden.
    @classmethod
    def getChessboard(cls, board):
        template = deepcopy(cls.template)
        
        if board.orientation == -1:
            template.reverse()
            for row in template:
                row.reverse()
                
        cls.shuffle(template[0])
        cls.shuffle(template[cls.rows - 1])
        
        chessboard = [[None] * cls.cols for r in xrange(cls.rows)]
        
        for r in xrange(cls.rows):
            for c in xrange(cls.cols):
                if template[r][c]: 
                    chessboard[r][c] = piece.numToPiece[abs(template[r][c])](board, template[r][c] / abs(template[r][c]), r, c, board.master.chessPieceImages[template[r][c]] if board.master is not None else None)
                    
        return chessboard
    
    # A static method that shuffles a list.
    @staticmethod
    def shuffle(lst):
        for i in xrange(1, len(lst)):
            randomIndex = int(random(i))
            lst[i], lst[randomIndex] = lst[randomIndex], lst[i]
        

def main():
    print("Please run the Chess_by_Eric_Liu.pyde file to run the program.")


if __name__ == "__main__":
    main()
