import json
import numpy as np
import sys
import threading
import time
import wx

from bob import Bob

myEVT_DRAW = wx.NewEventType()
EVT_DRAW = wx.PyEventBinder(myEVT_DRAW, 1)
class EpochEvent(wx.PyCommandEvent):
    """ Event to signal that a draw value is ready """
    def __init__(self, etype, eid):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)

class DrawingThread(threading.Thread):

    def __init__(self, parent, bob):
        """
        @param parent: The gui object that should recieve the value
        @param value: value to 'calculate' to
        """
        threading.Thread.__init__(self)
        self.parent = parent
        self.bob = bob

    def run(self):
        """Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        """
        self.bob.run()
        while (self.bob.busy):
            self.bob.epoch()
            evt = EpochEvent(myEVT_DRAW, -1)
            wx.PostEvent(self.parent, evt)

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1

class Pathfinder(wx.Frame):

    def __init__(self, parent, title, configFile, width = 900, height = 600): 
        super(Pathfinder, self).__init__(parent, title = title, size = (width, height + 40))

        self.width = width
        self.height = height
        self.getConfigFrom(configFile)
        self.bob = Bob(self.crossoverRate, self.mutationRate, self.populationSize, self.chromosomeLength,
				self.geneLength, self.entrance, self.exit_, self.gameMap, self.rows, self.columns)
        self.InitUI()

    def InitUI(self):
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_CHAR, self.OnKeyDown)
        self.Bind(EVT_DRAW, self.OnDraw)

        self.Centre() 
        self.Show(True)

    def OnDraw(self, evt):
        self.Refresh()

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        self.dc = dc
        brush = wx.Brush('white')
        dc.SetBackground(brush)
        dc.Clear()

        self.bob.render(self.width, self.height, dc)

    def OnKeyDown(self, event):
        keycode = event.GetUnicodeKey()
        if keycode == wx.WXK_ESCAPE:
            sys.exit()
        if keycode == wx.WXK_RETURN:
            worker = DrawingThread(self, self.bob)
            worker.start()

        elif keycode == wx.WXK_SPACE:
            self.bob.busy = False
            self.worker.abort()

    def getConfigFrom(self, jsonFile):
        with open(jsonFile) as file:  
            data = json.load(file)
            self.crossoverRate = data['crossoverRate']
            self.mutationRate = data['mutationRate']
            self.populationSize = data['populationSize']
            self.chromosomeLength = data['chromosomeLength']
            self.geneLength = data['geneLength']
            self.entrance = data['entrance']
            self.exit_ = data['exit']
            self.rows = data['rows']
            self.columns = data['columns']
            #self.gameMap = [[0 for i in range(self.columns)] for j in range(self.rows)]
            self.gameMap = np.zeros([self.rows, self.columns])
            matrix = data['gameMap']
            i = 0
            for row in matrix:
                j = 0
                for val in row:
                    self.gameMap[i][j] = val
                    j += 1
                i += 1

ex = wx.App() 
Pathfinder(None, 'Pathfinder', 'config/config.json', 900, 600)
ex.MainLoop()
