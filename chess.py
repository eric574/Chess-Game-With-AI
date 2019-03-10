from Queue import Queue
import chessboard
import variant
import piece
import widget
import AI


# A GUI enumeration class that holds the GUI state of the program.
class GUI:
    MAIN = 0
    LOAD = 1
    GAME = 2


# A THEME enumeration class that acts as enum that holds the design theme of the program.
class THEME:
    MODERN = "Modern"
    CLASSIC = "Classic"


# A Chess class that controls all the other classes in the program.
class Chess:
    # An __init__ member function that gets called as the Chess instance is created. It creates the representation of the object.
    def __init__(self):
        self.resetVars()
        self.switchTo(GUI.MAIN)
        
    # A member function that resets the variables of the Chess instance.
    def resetVars(self):
        self.calculateGeometry()
        self.drawingQueue = Queue()
        self.mousePressed = False
        self.guiState = None
        self.widgets = list()
        self.chessboard = None
        self.chessPieceImageRaw = None
        self.chessPieceImages = None
        self.hasPopUp = False
        self.popUp = None
        self.AI = None
        self.boardAngle = 0
        self.currentBoardAngle = 0
        self.resetSettings()
        self.waitingTime = 0
        self.guiWidgets = {
                GUI.MAIN: lambda: [widget.Image(width / 2.0, height / 2.0, width, height, loadImage("mainImage.jpg"), False), \
                                   widget.Button(3 * self.xUnit, 4 * self.yUnit, 4 * self.xUnit, self.yUnit, "2 Players", 0.45 * self.yUnit, color(0), color(255), color(0), 5, \
                                                lambda: self.createSettingsPopUp(), True), \
                                   widget.Button(3 * self.xUnit, 5.2 * self.yUnit, 4 * self.xUnit, self.yUnit, "Player vs Computer", 0.45 * self.yUnit, color(0), color(255), color(0), 5, \
                                                lambda: self.settings.__setitem__("AI", True) or self.createSettingsPopUp(), True)],
                GUI.LOAD: lambda: [],
                GUI.GAME: lambda: [widget.Button(0.8 * self.xUnit, 9.45 * self.yUnit, 1.2 * self.xUnit, 0.7 * self.yUnit, "To Menu", 0.3 * self.yUnit, color(0), color(255), color(0), 5, \
                                                lambda: self.switchTo(GUI.MAIN), True),
                                   widget.Button(9.2 * self.xUnit, 9.45 * self.yUnit, 1.2 * self.xUnit, 0.7 * self.yUnit, "Rotate", 0.3 * self.yUnit, color(0), color(255), color(0), 5, \
                                                lambda: self.rotate(PI), True)]
                }
        
    def resetSettings(self):
        self.settings = {
                "theme": THEME.MODERN,
                "variant": variant.Standard,
                "color": piece.COLOR.BLACK,
                "AI": False,
                "playAs": []
                }
        
    # A member function that creates a popup on the program based on the list of widgets supplied through the popUp parameter.
    def createPopUp(self, popUp):
        self.hasPopUp = True
        self.popUp = popUp
        
    # A member function that creates a popup that allows the user to set the game settings.
    def createSettingsPopUp(self):
        self.hasPopUp = True
        self.popUp = [widget.Rect(width / 2.0, height / 2.0, width, height, color(1, 200), color(1, 200), 0, False), 
                      widget.Button(width / 2.0, 8 * self.yUnit, 3 * self.xUnit, self.yUnit, "Play", 0.45 * self.yUnit, color(0), color(255), color(0), 5,
                                    lambda: self.drawingQueue.put(lambda: image(loadImage("loadingImage.jpg"), width / 2.0, height / 2.0, width, height)) or
                                    self.drawingQueue.put(lambda: self.destroyPopUp()) or self.drawingQueue.put(lambda: self.switchTo(GUI.LOAD)), True),
                      widget.Button(9 * self.xUnit, 9.5 * self.yUnit, 1.8 * self.xUnit, 0.8 * self.yUnit, "Back", 0.35 * self.yUnit, color(0), color(255), color(0), 5,
                                    lambda: self.resetSettings() or self.drawingQueue.put(lambda: self.destroyPopUp()), True)]

        self.addThemeChoicesToSettingsPopUp()
        self.addColorChoicesToSettingsPopUp()
        if not self.settings["AI"]:  # Stockfish AI can only play in standard variant
            self.addVariantChoicesToSettingsPopUp()
        
    # A member function that adds theme choices to settings pop up.
    def addThemeChoicesToSettingsPopUp(self):
        self.popUp.extend([
                           widget.TXT(1.3 * self.xUnit, 1.5 * self.yUnit, "Theme: ", 0.45 * self.yUnit, color(255), False),
                           widget.Choice(width / 2.0 - self.xUnit, 1.5 * self.yUnit, 1.9 * self.xUnit, self.yUnit, "Modern", 0.45 * self.yUnit, color(0), color(255), color(0), 5,
                           lambda var: self.settings.__setitem__("theme", var), lambda: self.settings["theme"], THEME.MODERN, True),
                           widget.Choice(width / 2.0 + self.xUnit, 1.5 * self.yUnit, 1.9 * self.xUnit, self.yUnit, "Classic", 0.45 * self.yUnit, color(0), color(255), color(0), 5,
                           lambda var: self.settings.__setitem__("theme", var), lambda: self.settings["theme"], THEME.CLASSIC, True),
                           ])
        
    # A member function that adds color choices to settings pop up.
    def addColorChoicesToSettingsPopUp(self):
        self.popUp.extend([
                           widget.TXT(1.3 * self.xUnit, 3 * self.yUnit, "Play as: " if self.settings["AI"] else "Orientation: ", 0.45 * self.yUnit, color(255), False),
                           widget.Choice(width / 2.0 - self.xUnit, 3 * self.yUnit, 1.9 * self.xUnit, self.yUnit, "Black", 0.45 * self.yUnit, color(0), color(255), color(0), 5,
                           lambda var: self.settings.__setitem__("color", var), lambda: self.settings["color"], piece.COLOR.BLACK, True),
                           widget.Choice(width / 2.0 + self.xUnit, 3 * self.yUnit, 1.9 * self.xUnit, self.yUnit, "White", 0.45 * self.yUnit, color(0), color(255), color(0), 5,
                           lambda var: self.settings.__setitem__("color", var), lambda: self.settings["color"], piece.COLOR.WHITE, True),
                           ])
        
    def addVariantChoicesToSettingsPopUp(self):
        self.popUp.extend([
                           widget.TXT(self.xUnit, 4.5 * self.yUnit, "Variant: ", 0.45 * self.yUnit, color(255), False),
                           widget.Choice(width / 2.0 - 2 * self.xUnit, 4.5 * self.yUnit, 1.9 * self.xUnit, self.yUnit, "Standard", 0.45 * self.yUnit, color(0), color(255), color(0), 5,
                           lambda var: self.settings.__setitem__("variant", var), lambda: self.settings["variant"], variant.Standard, True),
                           widget.Choice(width / 2.0, 4.5 * self.yUnit, 1.9 * self.xUnit, self.yUnit, "Horde", 0.45 * self.yUnit, color(0), color(255), color(0), 5,
                           lambda var: self.settings.__setitem__("variant", var), lambda: self.settings["variant"], variant.Horde, True),
                           widget.Choice(width / 2.0 + 2 * self.xUnit, 4.5 * self.yUnit, 1.9 * self.xUnit, self.yUnit, "Chess960", 0.45 * self.yUnit, color(0), color(255), color(0), 5,
                           lambda var: self.settings.__setitem__("variant", var), lambda: self.settings["variant"], variant.Chess960, True),
                           ])
        
    # A member function that makes the popup disappear.
    def destroyPopUp(self):
        self.hasPopUp = False
        self.popUp = None
        
    # A member function that imports a sprite of the chess pieces and crops them accordingly.
    def importImages(self):
        self.chessPieceImageRaw = loadImage("chessPieces" + self.settings["theme"] + ".png")
        self.chessPieceImages = dict()
        
        imageWidth = self.chessPieceImageRaw.width
        imageHeight = self.chessPieceImageRaw.height
        
        for i in xrange(1, 7):
            self.chessPieceImages[i] = createImage(imageWidth / 6, imageHeight / 2, ARGB)
            self.chessPieceImages[-i] = createImage(imageWidth / 6, imageHeight / 2, ARGB)
        
        self.getWhiteChessPieceImages()
        self.getBlackChessPieceImages()
        
    # A member function that crops the images of the white pieces from the sprite imported from the importImages member function.
    def getWhiteChessPieceImages(self):
        imageWidth = int(self.chessPieceImageRaw.width)
        imageHeight = int(self.chessPieceImageRaw.height)

        chessPieceImageWidth = self.chessPieceImageRaw.width / 6
        chessPieceImageHeight = self.chessPieceImageRaw.height / 2
        
        for piece in xrange(6):
            self.chessPieceImages[piece + 1].loadPixels()
            for i in xrange(chessPieceImageWidth * chessPieceImageHeight):
                row = i / chessPieceImageWidth
                self.chessPieceImages[piece + 1].pixels[i] = self.chessPieceImageRaw.pixels[row * imageWidth + piece * chessPieceImageWidth + i % chessPieceImageWidth]
            self.chessPieceImages[piece + 1].updatePixels()
        
    # A member function that crops the images of the black pieces from the sprite imported from the importImages member function.
    def getBlackChessPieceImages(self):
        imageWidth = self.chessPieceImageRaw.width
        imageHeight = self.chessPieceImageRaw.height

        chessPieceImageWidth = self.chessPieceImageRaw.width / 6
        chessPieceImageHeight = self.chessPieceImageRaw.height / 2
        
        for piece in xrange(6):
            self.chessPieceImages[-(piece + 1)].loadPixels()
            for i in xrange(chessPieceImageWidth * chessPieceImageHeight):
                row = i / chessPieceImageWidth
                self.chessPieceImages[-(piece + 1)].pixels[i] = self.chessPieceImageRaw.pixels[row * imageWidth + piece * chessPieceImageWidth + i % chessPieceImageWidth + imageWidth * chessPieceImageHeight]
            self.chessPieceImages[-(piece + 1)].updatePixels()
        
    # A member function that calculates the units of the program based on program width and height. This is calculated to improve scaling of the
    # program in various resolutions.
    def calculateGeometry(self):
        self.xUnit = width / 10.0
        self.yUnit = height / 10.0
        
    # A member function that creates the chessboard that will be displayed during the game.
    def createChessboard(self):
        dimension = min(self.xUnit * 8, self.yUnit * 8)
        self.chessboard = chessboard.Chessboard(master=self, x=width / 2.0, y=height / 2.0, w=dimension, h=dimension, variant=self.settings["variant"], orientation=self.settings["color"])
    
    # A member function that gets the mouse location and adjusts accordingly depending on whether or not the board is rotated.
    def getBoardMouseLocation(self):
        if self.boardAngle != 0:
            return PVector(width / 2.0 + (width / 2.0 - mouseX), height / 2.0 + (height / 2.0 - mouseY))
        return PVector(mouseX, mouseY)
    
    # A member function that gets called when the user clicks the mouse.
    def mouseAction(self):
        if self.hasPopUp:
            for widget in self.popUp:
                if widget.contains(mouseX, mouseY):
                    if self.mousePressed:
                        widget.isActive = True
                    elif widget.isActive:
                        widget.action()
        else:
            for widget in self.widgets:
                if widget.contains(mouseX, mouseY):
                    if self.mousePressed:
                        widget.isActive = True
                    elif widget.isActive:
                        widget.action()
            
            if self.guiState == GUI.MAIN:
                pass
            elif self.guiState == GUI.LOAD:
                pass
            elif self.guiState == GUI.GAME:
                mouseLocation = self.getBoardMouseLocation()

                if self.chessboard.containsCoord(mouseLocation.x, mouseLocation.y) and self.chessboard.turn in self.settings["playAs"]:
                    self.chessboard.actionAtCoord(mouseLocation.x, mouseLocation.y, self.mousePressed)
    
    # A member function that gets called every frame.
    def update(self):
        self.currentBoardAngle += (self.boardAngle - self.currentBoardAngle) * min(1, 5 / frameRate)
        
        if self.hasPopUp:
            for widget in self.popUp:
                if not widget.contains(mouseX, mouseY) and not self.mousePressed:
                    widget.isActive = False
        else:
            for widget in self.widgets:
                if not widget.contains(mouseX, mouseY) and not self.mousePressed:
                    widget.isActive = False
            
            if self.guiState == GUI.MAIN:
                pass
            elif self.guiState == GUI.LOAD:
                pass
            elif self.guiState == GUI.GAME:
                mouseLocation = self.getBoardMouseLocation()
                
                if self.chessboard.turn not in self.settings["playAs"] and self.chessboard.result == chessboard.RESULT.UNDETERMINED:
                    if self.waitingTime == 0:  # This only true when the player is playing against AI.
                        move = self.AI.getMove()
                        initialCell = self.chessboard.posToCell(move[0], move[1])
                        finalCell = self.chessboard.posToCell(move[2], move[3])
                        self.chessboard.instantlyMakeMove(initialCell[0], initialCell[1], finalCell[0], finalCell[1])
                    else:
                        self.waitingTime = max(self.waitingTime - 1 / frameRate, 0)
                
                if self.chessboard.containsCoord(mouseLocation.x, mouseLocation.y):
                    self.chessboard.highlight(*self.chessboard.coordToCell(mouseLocation.x, mouseLocation.y))
                    if self.mousePressed:
                        self.chessboard.createEffect(*self.chessboard.coordToCell(mouseLocation.x, mouseLocation.y))
                else:
                    self.chessboard.dehighlight()
    
    # A member function that displays the game.
    def display(self):
        if self.guiState == GUI.MAIN:
            pass
        elif self.guiState == GUI.LOAD:
            pass
        elif self.guiState == GUI.GAME:
            pushMatrix()
            translate(width / 2.0, height / 2.0)
            rotate(self.currentBoardAngle)
            translate(-width / 2.0, -height / 2.0)
            background(255)
            self.chessboard.display()
            popMatrix()
            
        for widget in self.widgets:
            widget.display()
        
        if self.hasPopUp:
            for widget in self.popUp:
                widget.display()
        
    # A member function that switches the GUI state of the program.
    def switchTo(self, guiState):
        if guiState == self.guiState: return

        self.switchFrom()
        
        self.widgets = self.guiWidgets[guiState]()
        
        if guiState == GUI.MAIN:
            pass
        elif guiState == GUI.LOAD:
            self.importImages()
            self.createChessboard()
            
            if self.settings["AI"]:
                self.settings["playAs"] = {self.settings["color"]}
                self.AI = AI.StockfishAI(self)
            else:
                self.settings["playAs"] = {piece.COLOR.BLACK, piece.COLOR.WHITE}
                
            self.drawingQueue.put(lambda: self.switchTo(GUI.GAME))
        elif guiState == GUI.GAME:
            pass
            
        self.guiState = guiState
        
    # A member function that does whatever necessary to switch from a previous gui state.
    def switchFrom(self):
        if self.guiState == GUI.MAIN:
            pass
        elif self.guiState == GUI.LOAD:
            pass
        elif self.guiState == GUI.GAME:
            if self.settings["AI"]:
                self.AI.quit()
            self.resetVars()
            
    # A member function that rotates the board.
    def rotate(self, delta):
        self.boardAngle = (self.boardAngle + delta) % TWO_PI
        
    # A member function that gets called after each move.
    def takeCareOfMove(self, record):
        if self.settings["AI"]:  # If the player is playing against the AI, each move must be sent to the program.
            a1, n1 = self.chessboard.cellToPos(*record["from"])
            a2, n2 = self.chessboard.cellToPos(*record["to"])
            self.AI.setMove(a1, n1, a2, n2)
            self.waitingTime = random(0.1, 0.2)
            
    # A member function that takes care of promotion when playing against the AI.
    def sendPromotionToAI(self, symbol):
        if self.settings["AI"]:
            self.AI.promote(symbol)

def main():
    print("Please run the Chess_by_Eric_Liu.pyde file to run the program.")


if __name__ == "__main__":
    main()
