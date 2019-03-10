import shlex
from subprocess import Popen, PIPE
import piece

# A class that launches the Stockfish AI program and communicate with it for a solid AI to be played against.
class StockfishAI:
    # An __init__ member function that gets called as the Stockfish AI instance is created. It creates the representation of the object.
    def __init__(self, master):
        self.master = master
        self.path = sketchPath() + "\\data\\stockfish_9_x64.exe"
        self.process = Popen(self.path, stdin=PIPE, stdout=PIPE)
        self.moves = []
        self.setup()
        
    # A member function that readies the Stockfish AI program.
    def setup(self):
        self.process.stdout.readline()  # the Stockfish AI program prints one line by default when it is launched.
        self.process.stdin.write("isready\r\nucinewgame\r\n")
        self.process.stdin.flush()
        self.process.stdout.readline()  # the Stockfish AI should print readyok here.
        
    # A member function that gets the move from the AI program.
    def getMove(self):
        self.process.stdin.write("go\r\n")
        self.process.stdin.flush()

        out = self.process.stdout.readline()
        while "bestmove" not in out:
            out = self.process.stdout.readline()
            
        out = out.split()
        move = out[1]

        if len(move) > 4:  # Then, promotion needs to be done.
            newPiece = None
            if move[-1] == "r":
                newPiece = piece.PIECE.ROOK
            elif move[-1] == "q":
                newPiece = piece.PIECE.QUEEN
            elif move[-1] == "n":
                newPiece = piece.PIECE.KNIGHT
            elif move[-1] == "b":
                newPiece = piece.PIECE.BISHOP
                
            r, c = self.master.chessboard.posToCell(move[2], move[3])
            self.master.drawingQueue.put(lambda: self.master.chessboard.get(r, c).changeTo(self.master.chessboard.get(r, c).color * newPiece))

        return move[0], move[1], move[2], move[3]
    
    # A member function that sends a move made to the program.
    def setMove(self, a1, n1, a2, n2):
        self.moves.append(a1 + n1 + a2 + n2)
        self.process.stdin.write("\r\nposition startpos moves " + " ".join(self.moves) + "\r\n")
        self.process.stdin.flush()
        
    # A member function that sends information about promotion.
    def promote(self, symbol):
        self.moves[-1] += symbol
        self.process.stdin.write("\r\nposition startpos moves " + " ".join(self.moves) + "\r\n")
        self.process.stdin.flush()
        
    # A member function that quits the process.
    def quit(self):
        self.process.stdin.write("quit\r\n")
        self.process.stdin.flush()
        self.process.wait()
