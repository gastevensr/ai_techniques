import wx

class GameMap:

    def __init__(self, matrix, entrance, exit_, rows, columns):
        self.map = matrix
        self.entrance = entrance
        self.exit_ = exit_
        self.mapHeight = rows
        self.mapWidth  = columns
        self.findEntranceExitCoords()
        self.resetMemory()

    def findEntranceExitCoords(self):
        for y in range(self.mapHeight):
            for x in range(self.mapWidth):
                if self.map[y][x] == self.entrance:
                    self.startX = x
                    self.startY = y
                elif self.map[y][x] == self.exit_:
                    self.endX = x
                    self.endY = y

    def resetMemory(self):
        """ Resets the memory map to zeros. """
        self.memory =  [[ValueDirection() for i in range(self.mapWidth)] for j in range(self.mapHeight)]

    def TestRoute(self, path, memory):
        """ Takes a string of directions and see's how far Bob can get. Returns a
        fitness score proportional to the distance reached from the exit. """
        posX = self.startX
        posY = self.startY
        for i in range(len(path)):
            direction = path[i]
            if direction == 0:# North
                if posY - 1 >= 0 and self.map[posY - 1][posX] != 1:
                    posY -= 1
            elif direction == 1:# South
                if posY + 1 < self.mapHeight and self.map[posY + 1][posX] != 1:
                    posY += 1
            elif direction == 2:# East
                if posX + 1 < self.mapWidth and self.map[posY][posX + 1] != 1:
                    posX += 1
            elif direction == 3:# West
                if posX - 1 >= 0 and self.map[posY][posX - 1] != 1:
                    posX -= 1
            memory.memory[posY][posX].value = 1
            memory.memory[posY][posX].direction = direction
        diffX = abs(posX - self.endX)
        diffY = abs(posY - self.endY)

        return 1.0 / (diffX + diffY + 1), memory.memory

    def render(self, width, height, canvas):
        """ Given a surface to draw on this function uses the windows GDI to display the map. """
        border = 20
        blockSizeX = (width - 2 * border) / self.mapWidth
        blockSizeY = (height - 2 * border) / self.mapHeight

        black = wx.Colour(0, 0, 0)
        brush = wx.Brush(black)
        pen = wx.Pen(black)
        canvas.SetPen(pen)
        canvas.SetBrush(brush)
        for y in range(0, self.mapHeight):
            for x in range(0, self.mapWidth):
                # Calculate the corners of each cell.
                left = border + (blockSizeX * x)
                top = border + (blockSizeY * y)
                # Draw a black rectangle if this is a wall.
                if self.map[y][x] == 1:
                    canvas.DrawRectangle(left, top, blockSizeX, blockSizeY)

    def memoryRender(self, width, height, canvas):
        """ Draws whatever path may be stored in the memory. """
        border = 20
        blockSizeX = (width - 2 * border) / self.mapWidth
        blockSizeY = (height - 2 * border) / self.mapHeight

        blue = wx.Colour(0, 0, 255)
        blueBrush = wx.Brush(blue)
        bluePen = wx.Pen(blue)
        
        yellow = wx.Colour(255, 255, 0)
        yellowPen = wx.Pen(yellow)
        for y in range(0, self.mapHeight):
            for x in range(0, self.mapWidth):
                # Calculate the corners of each cell.
                left = border + (blockSizeX * x)
                top = border + (blockSizeY * y)
                # Draw a blue path.
                if self.memory[y][x].value == 1:
                    canvas.SetPen(bluePen)
                    canvas.SetBrush(blueBrush)
                    canvas.DrawRectangle(left, top, blockSizeX, blockSizeY)

                    coords = []
                    if self.memory[y][x].direction == 0:# North
                        x1 = left + blockSizeX / 2
                        y1 = top

                        x2 = left + blockSizeX
                        y2 = top + blockSizeY

                        x3 = left
                        y3 = top + blockSizeY
                        coords = [(x1, y1), (x2, y2), (x3, y3)]
                    elif self.memory[y][x].direction == 1:# South
                        x1 = left + blockSizeX / 2
                        y1 = top

                        x2 = left + blockSizeX
                        y2 = top + blockSizeY

                        x3 = left
                        y3 = top + blockSizeY
                        coords = [(x1, y1), (x2, y2), (x3, y3)]
                    elif self.memory[y][x].direction == 2:# East
                        x1 = left + blockSizeX
                        y1 = top + blockSizeY / 2

                        x2 = left
                        y2 = top + blockSizeY

                        x3 = left
                        y3 = top
                        coords = [(x1, y1), (x2, y2), (x3, y3)]
                    elif self.memory[y][x].direction == 3:# West
                        x1 = left
                        y1 = top + blockSizeY / 2

                        x2 = left + blockSizeX
                        y2 = top + blockSizeY

                        x3 = left + blockSizeX
                        y3 = top
                        coords = [(x1, y1), (x2, y2), (x3, y3)]

                    canvas.SetPen(yellowPen)
                    canvas.DrawPolygon(coords)

    def drawGates(self, width, height, canvas):
        border = 20

        blockSizeX = (width - 2 * border) / self.mapWidth
        blockSizeY = (height - 2 * border) / self.mapHeight

        left = border + (blockSizeX * self.startX)
        top = border + (blockSizeY * self.startY)

        # Entrance is green.
        green = wx.Colour(0, 255, 0)
        brush = wx.Brush(green)
        pen = wx.Pen(green)
        canvas.SetPen(pen)
        canvas.SetBrush(brush)
        canvas.DrawRectangle(left, top, blockSizeX, blockSizeY)

        left = border + (blockSizeX * self.endX)
        top = border + (blockSizeY * self.endY)

        # Exit is red.
        red = wx.Colour(255, 0, 0)
        brush = wx.Brush(red)
        pen = wx.Pen(red)
        canvas.SetPen(pen)
        canvas.SetBrush(brush)
        canvas.DrawRectangle(left, top, blockSizeX, blockSizeY)

class ValueDirection:
    """ Simple class for storing value of path and direction taken. """
    def __init__(self, value = -1, direction = -1):
        self.value = value
        self.direction = direction
