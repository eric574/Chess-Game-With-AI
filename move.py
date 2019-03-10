import piece


# A Move base class that provides an interface for move type classes which would be inherited from this class.
class Move:
    possiblePositions = list()
    isCheckable = True
        
    # A class method that gets the next possible positions of the piece.
    @classmethod
    def getNextPositions(cls, chessboard, chessPiece, disregardCheck=False):
        nextPositions = list()
        
        for possiblePosition in cls.possiblePositions:
            position = chessPiece.r + chessPiece.forward * possiblePosition[0], chessPiece.c + possiblePosition[1]
            if chessboard.containsCell(*position) and chessboard.cellColor(*position) != chessPiece.color and \
                 (disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, position)):
                nextPositions.append(position)
                
        return nextPositions
        
    # A class method that determines if a move causes enemy check. 
    @classmethod
    def causeEnemyCheck(cls, chessboard, chessPiece, position):
        newBoard = chessboard.copy()
        newBoard.get(chessPiece.r, chessPiece.c).lastMoved = newBoard.count
        cls.makeMove(newBoard, newBoard.get(chessPiece.r, chessPiece.c), position[0], position[1])
        newBoard.update()
        newBoard.cacheNextPositions(True)
        kingCell = newBoard.getKingCell(chessPiece.color)
        
        if kingCell is not None and newBoard.isVulnerable(*kingCell):
            return True
            
        return False
        
    # A static method that makes a move of the chess piece, given the chessboard and the piece.
    @staticmethod
    def makeMove(chessboard, chessPiece, r, c,):
        chessboard.set(chessPiece.r, chessPiece.c, None)
        chessboard.set(r, c, chessPiece)
        chessPiece.r = r
        chessPiece.c = c
        

# Implementation of individual move type classes follow. Each contains possible positions and overrides member function from base Move class if necessary.


class Adjacent(Move):
    possiblePositions = [(1, -1), (1, 0), (1, 1), (0, -1), (0, 1), (-1, -1), (-1, 0), (-1, 1)]
        
    @staticmethod
    def makeMove(chessboard, chessPiece, r, c):
        Move.makeMove(chessboard, chessPiece, r, c)


class Castling(Move):
    possiblePositions = [(0, -2), (0, 2)]
    isCheckable = False

    @classmethod
    def getNextPositions(cls, chessboard, chessPiece, disregardCheck=False):

        nextPositions = list()
        
        for possiblePosition in cls.possiblePositions:
            position = chessPiece.r + chessPiece.forward * possiblePosition[0], chessPiece.c + possiblePosition[1]
            rookPosition = chessPiece.r, (7 if chessPiece.c < position[1] else 0)
            if chessPiece.c in (3, 4) and chessboard.containsCell(*position) and chessboard.containsCell(*rookPosition) and \
                 not chessboard.obstructed(chessPiece.r, chessPiece.c, *rookPosition) and (chessboard.isOccupied(*rookPosition) and \
                chessboard.get(*rookPosition).pieceType * chessboard.get(*rookPosition).color == chessPiece.color * piece.PIECE.ROOK) and \
                 chessboard.get(*rookPosition).neverMoved and chessPiece.neverMoved and \
                (disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, position)):
                nextPositions.append(position)

        return nextPositions     
        
    @staticmethod
    def makeMove(chessboard, chessPiece, r, c):
        currentRookPosition = chessPiece.r, (7 if chessPiece.c < c else 0)
        subsequentRookPosition = chessPiece.r, (c - 1 if chessPiece.c < c else c + 1)
        chessboard.set(subsequentRookPosition[0], subsequentRookPosition[1], chessboard.get(*currentRookPosition))
        chessboard.set(currentRookPosition[0], currentRookPosition[1], None)
        chessboard.get(*subsequentRookPosition).r = subsequentRookPosition[0]
        chessboard.get(*subsequentRookPosition).c = subsequentRookPosition[1]
        
        Move.makeMove(chessboard, chessPiece, r, c)                             


class RankFile(Move):
    possiblePositions = [(r, 0) for r in xrange(-7, 8) if r] + [(0, c) for c in xrange(-7, 8) if c]
    
    @classmethod
    def getNextPositions(cls, chessboard, chessPiece, disregardCheck=False):
        nextPositions = list()
        
        # Left
        for c in xrange(chessPiece.c - 1, -1, -1):
            if chessboard.isEmpty(chessPiece.r, c):  # Empty cell
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (chessPiece.r, c)):
                    nextPositions.append((chessPiece.r, c))
            elif chessboard.cellColor(chessPiece.r, c) == chessPiece.color:  # Cell occupied by a chessPiece of the same color
                break
            else:  # Cell occupied by a chessPiece of the different color
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (chessPiece.r, c)):
                    nextPositions.append((chessPiece.r, c))
                break
        
        # Right
        for c in xrange(chessPiece.c + 1, chessboard.cols):
            if chessboard.isEmpty(chessPiece.r, c):  # Empty cell
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (chessPiece.r, c)):
                    nextPositions.append((chessPiece.r, c))
            elif chessboard.cellColor(chessPiece.r, c) == chessPiece.color:  # Cell occupied by a chessPiece of the same color
                break
            else:  # Cell occupied by a chessPiece of the different color
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (chessPiece.r, c)):
                    nextPositions.append((chessPiece.r, c))
                break
        
        # Up
        for r in xrange(chessPiece.r - 1, -1, -1):
            if chessboard.isEmpty(r, chessPiece.c):  # Empty cell
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (r, chessPiece.c)):
                    nextPositions.append((r, chessPiece.c))
            elif chessboard.cellColor(r, chessPiece.c) == chessPiece.color:  # Cell occupied by a chessPiece of the same color
                break
            else:  # Cell occupied by a chessPiece of the different color
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (r, chessPiece.c)):
                    nextPositions.append((r, chessPiece.c))
                break
            
        # Down
        for r in xrange(chessPiece.r + 1, chessboard.rows):
            if chessboard.isEmpty(r, chessPiece.c):  # Empty cell
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (r, chessPiece.c)):
                    nextPositions.append((r, chessPiece.c))
            elif chessboard.cellColor(r, chessPiece.c) == chessPiece.color:  # Cell occupied by a chessPiece of the same color
                break
            else:  # Cell occupied by a chessPiece of the different color
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (r, chessPiece.c)):
                    nextPositions.append((r, chessPiece.c))
                break
        
        return nextPositions  
        
    @staticmethod
    def makeMove(chessboard, chessPiece, r, c):
        Move.makeMove(chessboard, chessPiece, r, c)
        

class Diagonal(Move):
    possiblePositions = [(r, c) for r in xrange(-7, 8) for c in xrange(-7, 8) if r and c and abs(r) == abs(c)]

    @classmethod
    def getNextPositions(cls, chessboard, chessPiece, disregardCheck=False):
        nextPositions = list()
        
        # Up Left
        for r, c in zip(xrange(chessPiece.r  - 1, -1, -1), xrange(chessPiece.c - 1, -1, -1)):
            if chessboard.isEmpty(r, c):  # Empty cell
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (r, c)):
                    nextPositions.append((r, c))
            elif chessboard.cellColor(r, c) == chessPiece.color:  # Cell occupied by a chessPiece of the same color
                break
            else:  # Cell occupied by a chessPiece of the different color
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (r, c)):
                    nextPositions.append((r, c))
                break
            
        # Up Right
        for r, c in zip(xrange(chessPiece.r - 1, -1, -1), xrange(chessPiece.c + 1, chessboard.cols)):
            if chessboard.isEmpty(r, c):  # Empty cell
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (r, c)):
                    nextPositions.append((r, c))
            elif chessboard.cellColor(r, c) == chessPiece.color:  # Cell occupied by a chessPiece of the same color
                break
            else:  # Cell occupied by a chessPiece of the different color
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (r, c)):
                    nextPositions.append((r, c))
                break
        
        # Down Left
        for r, c in zip(xrange(chessPiece.r + 1, chessboard.rows), xrange(chessPiece.c - 1, -1, -1)):
            if chessboard.isEmpty(r, c):  # Empty cell
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (r, c)):
                    nextPositions.append((r, c))
            elif chessboard.cellColor(r, c) == chessPiece.color:  # Cell occupied by a chessPiece of the same color
                break
            else:  # Cell occupied by a chessPiece of the different color
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (r, c)):
                    nextPositions.append((r, c))
                break
            
        # Down Right
        for r, c in zip(xrange(chessPiece.r + 1, chessboard.rows), xrange(chessPiece.c + 1, chessboard.cols)):
            if chessboard.isEmpty(r, c):  # Empty cell
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (r, c)):
                    nextPositions.append((r, c))
            elif chessboard.cellColor(r, c) == chessPiece.color:  # Cell occupied by a chessPiece of the same color
                break
            else:  # Cell occupied by a chessPiece of the different color
                if disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, (r, c)):
                    nextPositions.append((r, c))
                break
        
        return nextPositions  
        
    @staticmethod
    def makeMove(chessboard, chessPiece, r, c):
        Move.makeMove(chessboard, chessPiece, r, c)
        

class LJump(Move):
    possiblePositions = [(2, -1), (2, 1), (1, -2), (1, 2), (-1, -2), (-1, 2), (-2, -1), (-2, 1)]

    @staticmethod
    def makeMove(chessboard, chessPiece, r, c):
        Move.makeMove(chessboard, chessPiece, r, c)


class Forward(Move):
    possiblePositions = [(1, 0)]
    isCheckable = False

    @classmethod
    def getNextPositions(cls, chessboard, chessPiece, disregardCheck=False):
        nextPositions = list()
        
        for possiblePosition in cls.possiblePositions:
            position = chessPiece.r + chessPiece.forward * possiblePosition[0], chessPiece.c + possiblePosition[1]
            if chessboard.containsCell(*position) and chessboard.isEmpty(*position) and \
                 (disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, position)):
                nextPositions.append(position)
                
        return nextPositions

    @staticmethod
    def makeMove(chessboard, chessPiece, r, c):
        Move.makeMove(chessboard, chessPiece, r, c)


class DoubleForward(Move):
    possiblePositions = [(2, 0)]
    isCheckable = False

    @classmethod
    def getNextPositions(cls, chessboard, chessPiece, disregardCheck=False):
        nextPositions = list()
        
        for possiblePosition in cls.possiblePositions:
            position = chessPiece.r + chessPiece.forward * possiblePosition[0], chessPiece.c + possiblePosition[1]
            if chessboard.containsCell(*position) and chessboard.isEmpty(*position) and not chessboard.obstructed(chessPiece.r, chessPiece.c, *position) and \
            chessPiece.neverMoved and chessPiece.r == (1 if -chessboard.orientation * chessPiece.color == 1 else 6) and \
                 (disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, position)):
                nextPositions.append(position)
                
        return nextPositions
        
    @staticmethod
    def makeMove(chessboard, chessPiece, r, c):
        Move.makeMove(chessboard, chessPiece, r, c)


class ForwardDiagonal(Move):
    possiblePositions = [(1, -1), (1, 1)]

    @classmethod
    def getNextPositions(cls, chessboard, chessPiece, disregardCheck=False):
        nextPositions = list()
        
        for possiblePosition in cls.possiblePositions:
            position = chessPiece.r + chessPiece.forward * possiblePosition[0], chessPiece.c + possiblePosition[1]
            if chessboard.containsCell(*position) and chessboard.cellColor(*position) == -chessPiece.color and \
                 (disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, position)):
                nextPositions.append(position)
                
        return nextPositions
        
    @staticmethod
    def makeMove(chessboard, chessPiece, r, c):
        Move.makeMove(chessboard, chessPiece, r, c)


class EnPassant(Move):
    possiblePositions = [(1, -1), (1, 1)]
    isCheckable = False

    @classmethod
    def getNextPositions(cls, chessboard, chessPiece, disregardCheck=False):
        nextPositions = list()

        for possiblePosition in cls.possiblePositions:
            position = chessPiece.r + chessPiece.forward * possiblePosition[0], chessPiece.c + possiblePosition[1]
            if chessboard.containsCell(*position) and chessboard.isOccupied(position[0] - chessPiece.forward, position[1]) and \
            chessboard.get(position[0] - chessPiece.forward, position[1]).lastMoved == chessboard.count - 1 and chessboard.history and chessboard.history[-1]["move"] == DoubleForward and \
                 (disregardCheck or not cls.causeEnemyCheck(chessboard, chessPiece, position)):
                nextPositions.append(position)

        return nextPositions

    @staticmethod
    def makeMove(chessboard, chessPiece, r, c):
        chessboard.set(r - chessPiece.forward, c, None)
        Move.makeMove(chessboard, chessPiece, r, c)


moves = [Adjacent, Castling, RankFile, Diagonal, LJump, Forward, DoubleForward, ForwardDiagonal, EnPassant]
        

def main():
    print("Please run the Chess_by_Eric_Liu.pyde file to run the program.")


if __name__ == "__main__":
    main()
