from components import Meme
from threading import Thread
import tkinter as tk
from tkinter import *
import time
import sys

from tkinter import *
from Game import *

root = Tk()

MemeGame = Game()
GameUI = GUI()

lastDeltaTime = 0.04
fixedFrameThread = None

def StartFixedUpdate():
    """
    Fixed update, update 25 times fixedly per second.
    delta time is always 0.04 sec.
    """
    global MemeGame
    global GameUI
    while not MemeGame.EXIT:
        start = time.time()
        MemeGame.FixedUpdate(0.04)
        GameUI.FixedUpdate(0.04)
        end = time.time()
        actualDelta = end - start
        time.sleep(max(0, 0.04 - actualDelta))

def StartMainGame(tk: Tk, canvas: Canvas):
    """
    Start main game process.
    Begin main loop and fixed loop,
    And display the main mune.
    """
    global lastDeltaTime
    global MemeGame
    global GameUI
    global fixedFrameThread
    
    #MemeGame.canvas.delete("all")
    
    MemeGame.MainMenu()
    
    fixedFrameThread = Thread(target=StartFixedUpdate, name="FixedUpdate")
    fixedFrameThread.start()
    while not MemeGame.EXIT:
        try:
            start = time.time()
            MemeGame.Update(lastDeltaTime)
            if MemeGame.camera != None:
                    MemeGame.camera.RenderElements()
            GameUI.Update(lastDeltaTime)
            tk.update()
            time.sleep(0.00000001)
            end = time.time()
            lastDeltaTime = end - start
        except:
            MemeGame.EXIT = True
    fixedFrameThread.join()
    
def InitGameWindow(width=500, height=300):
    """
    Initialize Tk window with width and height parameters,
    And start main game process.
    """
    global MemeGame
    global GameUI
    global root
    # file = PIL.Image.open('./assets/images/background.jpg').resize((int(width*1.2), int(height*1.2)), PIL.Image.LANCZOS)
    # BgImage = PIL.ImageTk.PhotoImage(file)
    # file.close()
    root.size = (width, height)
    root.resizable(width=None, height=None)
    root.title("Meme Cat Run")
    mainCanvas = Canvas(background="gray80", height=height, width=width)
    #mainCanvas.create_image(int(width*0.5), max(0, int(height-350)), image = BgImage)
    mainCanvas.pack()
    
    MemeGame.Initialize(height, width, mainCanvas, root)
    GameUI.Init(mainCanvas, height, width)
    # startButton = Button(mainCanvas, background="red", command=StartMainGame)
    StartMainGame(root, mainCanvas)
    
    
if __name__ == "__main__":
    args = {}
    
    o = True
    opt = ''
    for arg in sys.argv[1:]:
        if o:
            opt = arg
            o = False
        else:
            args[opt] = arg
            o = True
        
    width = 1280
    height = 720
    try:
        if '-w' in args:
            width = int(args['-w'])
        if '-h' in args:
            height = int(args['-h'])
    except:
        raise TypeError('Argument type invalid')
    InitGameWindow(width=width, height=height)
    print('end')
    pass