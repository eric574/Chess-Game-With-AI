# A Widget base class that provides a representation and interface of each classes that will be inherited from this class.
class Widget:
    # An __init__ member function that gets called as the Widget instance is created. It creates the representation of the object.
    def __init__(self, x, y, w, h, fC, sC, sW, action, highlight):
        self.x = x
        self.xL = x - w / 2.0
        self.xR = x + w / 2.0
        self.y = y
        self.yU = y - h / 2.0
        self.yD = y + h / 2.0
        self.w = w
        self.h = h
        self.fC = fC
        self.sC = sC
        self.sW = sW
        self.action = action
        self.isActive = False
        self.highlight = highlight
        
    # A member function that displays a widget.
    def display(self):
        if self.contains(mouseX, mouseY) and self.highlight:
            self.displayHighlight()
        
    # A member function that determines if a coordinate is on the widget.
    def contains(self, x, y):
        return self.xL <= x < self.xR and self.yU <= y < self.yD
    
    # A member function that highlights the widget.
    def displayHighlight(self):
        pushStyle()
        fill(1, 50)
        stroke(1, 50)
        strokeWeight(self.sW)
        rect(self.x, self.y, self.w, self.h)
        popStyle()


# Implementation of individual widget type classes follow. Each overrides member function from base Widget class if necessary.


class TXT(Widget):
    def __init__(self, x, y, text, textSize, fC, highlight):
        Widget.__init__(self, x, y, 0, 0, fC, None, None, lambda: None, highlight)
        self.text = text
        self.textSize = textSize
        
    def display(self):
        pushStyle()
        fill(self.fC)
        textSize(self.textSize)
        text(self.text, self.x, self.y)
        popStyle()
        
        Widget.display(self)
        


class Rect(Widget):
    def __init__(self, x, y, w, h, fC, sC, sW, highlight):
        Widget.__init__(self, x, y, w, h, fC, sC, sW, lambda: None, highlight)
        
    def display(self):
        pushStyle()
        fill(self.fC)
        stroke(self.sC)
        strokeWeight(self.sW)
        rect(self.x, self.y, self.w, self.h)
        popStyle()
        
        Widget.display(self)


class Ellipse(Widget):
    def __init__(self, x, y, w, h, fC, sC, sW, highlight):
        Widget.__init__(self, x, y, w, h, fC, sC, sW, lambda: None, highlight)
        
    def display(self):
        pushStyle()
        fill(self.fC)
        stroke(self.sC)
        strokeWeight(self.sW)
        ellipse(self.x, self.y, self.w, self.h)
        popStyle()
        
        Widget.display(self)
        
    def displayHighlight(self):
        pushStyle()
        fill(1, 50)
        stroke(1, 50)
        strokeWeight(self.sW)
        ellipse(self.x, self.y, self.w, self.h)
        popStyle()


class Image(Widget):
    def __init__(self, x, y, w, h, img, highlight):
        Widget.__init__(self, x, y, w, h, None, None, None, lambda: None, highlight)
        self.img = img
        
    def display(self):
        image(self.img, self.x, self.y, self.w, self.h)
        
        Widget.display(self)

class ImageButton(Widget):
    def __init__(self, x, y, w, h, img, action, highlight):
        Widget.__init__(self, x, y, w, h, None, None, None, action, highlight)
        self.img = img
        
    def display(self):
        image(self.img, self.x, self.y, self.w, self.h)
        
        Widget.display(self)
    
    
class Button(Widget):
    def __init__(self, x, y, w, h, text, textSize, textFC, fC, sC, sW, action, highlight):
        Widget.__init__(self, x, y, w, h, fC, sC, sW, action, highlight)
        self.text = text
        self.textFC = textFC
        self.textSize = textSize
        
    def display(self):
        pushStyle()
        
        fill(self.fC)
        stroke(self.sC)
        strokeWeight(self.sW)
        
        rect(self.x, self.y, self.w, self.h)
        
        fill(self.textFC)
        textSize(self.textSize)
        
        text(self.text, self.x, self.y)
        
        popStyle()
        
        Widget.display(self)
        
class Choice(Widget):
    def __init__(self, x, y, w, h, text, textSize, textFC, fC, sC, sW, setVal, getVal, value, highlight):
        Widget.__init__(self, x, y, w, h, fC, sC, sW, lambda: self.setVal(self.value), highlight)
        self.text = text
        self.textFC = textFC
        self.textSize = textSize
        self.setVal = setVal
        self.getVal = getVal
        self.value = value
        
    def display(self):
        pushStyle()
        
        fill(self.fC)
        stroke(self.sC)
        strokeWeight(self.sW)
        
        rect(self.x, self.y, self.w, self.h)
            
        if self.getVal() == self.value:
            fill(1, 150)
            rect(self.x, self.y, self.w, self.h)
            
        fill(self.textFC)
        textSize(self.textSize)
        
        text(self.text, self.x, self.y)
        
        popStyle()
        
        Widget.display(self)


def main():
    print("Please run the Chess_by_Eric_Liu.pyde file to run the program.")


if __name__ == "__main__":
    main()
