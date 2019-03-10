import chess


def setup():
    global game, mouseDown
    
    size(1200, 900)
    frameRate(1000)
    textAlign(CENTER, CENTER)
    rectMode(CENTER)
    imageMode(CENTER)
    
    game = chess.Chess()

    
def draw():
    game.mousePressed = mousePressed
    
    if game.drawingQueue.qsize():
        function = game.drawingQueue.get()
        function()
        return
    
    game.update()
    game.display()
    

def mousePressed():
    game.mouseAction()
    
    
def mouseReleased():
    game.mouseAction()

    
