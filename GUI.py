
import os
import tkinter
import json

from tkinter import Checkbutton, Entry, Image, Label, LabelFrame, Text, font
from tkinter.font import Font, families
from tkinter import Canvas, Button, Frame, PhotoImage, StringVar, Tk, TkVersion, IntVar

from Utils import Utils, Vec2

class GUIControl:
    """
    Base GUI Control class.
    """
    
    def __init__(self, name="", tag="menu",position = Vec2(), width = 100, height = 100):
        self.name = name
        self.tag = tag
        self.GUI = GUI.Instance
        self.canvas = GUI.Instance.canvas
        self.tks = []
        
        self.Width = int(width)
        self.Height = int(height)
        self.__position = position
        pass
    
    @property
    def Position(self):
        return self.__position
    
    @Position.setter
    def Position(self, value):
        if isinstance(value, Vec2):
            if len(self.tks) > 0:
                diff = value - self.__position
                tk = self.tks[0]
                try:
                    tk.update()
                    x=tk.winfo_x()
                    y=tk.winfo_y()
                    w=tk.winfo_width()
                    h=tk.winfo_height()
                    tk.place(x = x+diff.X, y = y+diff.Y, width = w, height=h)
                except:
                    print('got tk error while updating tk control')
            self.__position = value
    
    def InRect(self, pos: Vec2):
        diff = pos - self.__position
        if diff.X > 0 and diff.Y > 0:
            if diff.X < self.Width and diff.Y < self.Height:
                return True
        return False
    
    def Init(self):
        # for tk in self.tks:
        #     tk.pack()
        pass
    
    def Destroy(self):
        for tk in self.tks:
            tk.destroy()
        self.tks = []
        pass
    
    def Update(self, deltatime):
        pass

    def FixedUpdate(self, deltatime):
        pass

class GUI:
    """
    Main GUI Controller.
    """
    
    Instance = None
    
    default_font = 'Comic Sans MS'
    
    def __init__(self) -> None:
        self.Controls = []
        self.ControlsByName = {}
        self.ControlsByTag = {}
        
        self.ImageResources = {}
        GUI.Instance = self
        
    def ReadResources(self, path = "./assets/images/UI/"):
        files = os.listdir(path)
        #files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f[-4:] == '.jpg']
        self.ImageResources = {**self.ImageResources, **Utils.LoadImages(path, files, 64, 64)}
        
    def Create(self, control: GUIControl):
        self.Controls.append(control)
        if control.name in self.ControlsByName:
            control.name += "_" + str(len(self.Controls))
        self.ControlsByName[control.name] = control
        
        if control.tag in self.ControlsByTag:
            self.ControlsByTag[control.tag].append(control)
        else:
            self.ControlsByTag[control.tag] = [control]
            
        control.Init()
        return control
    
    def Destroy(self, control: GUIControl):
        if control in self.Controls:
            self.Controls.remove(control)
            
        self.ControlsByName.pop(control.name, None)
        
        self.ControlsByTag[control.tag].remove(control)
        if self.ControlsByTag[control.tag].__len__() == 0:
            self.ControlsByTag.pop(control.tag, None)
        control.Destroy()
        pass
    
    def DestroyByName(self, name):
        control = self.ControlsByName[name]
        if control in self.Controls:
            self.Controls.remove(control)
            
        self.ControlsByName.pop(name, None)
        
        self.ControlsByTag[control.tag].remove(control)
        if self.ControlsByTag[control.tag].__len__() == 0:
            self.ControlsByTag.pop(control.tag, None)
        control.Destroy()
        pass
    
    def DestroyByTag(self, tag):
        if tag in self.ControlsByTag:
            ctrls = self.ControlsByTag[tag]
            length = len(ctrls)
            if length > 0:
                for i in range(length):
                    self.Destroy(ctrls[0])
            else:
                self.ControlsByTag.pop(tag, None)
        pass
    
    def GetControlByName(self, name):
        if name in self.ControlsByName:
            return self.ControlsByName[name]
        else:
            return None
        
    def GetControlByTag(self, tag):
        if tag in self.ControlsByTag:
            return self.ControlsByTag[tag][0]
        else:
            return None
        
    def GetControlsByTag(self, tag):
        if tag in self.ControlsByTag:
            return self.ControlsByTag[tag]
        else:
            return None

    def Init(self, canvas: tkinter.Canvas, height, width):
        self.canvas: Canvas = canvas
        
        self.Height = height
        self.Width = width
        
        self.ReadResources()
        
    def Update(self, deltatime):
        for ctrl in self.Controls:
            ctrl.Update(deltatime)
        #self.canvas.pack()
        pass
        
    def FixedUpdate(self, deltatime):
        for ctrl in self.Controls:
            ctrl.FixedUpdate(deltatime)
        pass
        
    
class GButton(GUIControl):
    
    def __init__(self, position: Vec2 = Vec2(), width = 100, height = 50, text = "button text", name = "Button", tag = "button", leftClickEvent = None):
        super().__init__(name, tag, position, width, height)
        
        self.text = text
        
        if leftClickEvent != None:
            self.__LeftClickEvent = leftClickEvent

        self.wait = False
    
    def __LeftClickEvent(self):
        pass
    
    def OnLeftHold(self, event):
        self.tks[0].configure(background="gray70")
        pass
    
    def OnLeftRelease(self, event):
        self.tks[0].configure(background="gray80")
        self.__LeftClickEvent()
        pass
        
    def Init(self):
        button = Label(master=self.canvas, text=self.text, background="gray80", width=self.Width, height=self.Height, font=Font(family=GUI.default_font, size=24, weight='bold'))
        button.bind("<Enter>", self.OnMouseEnter)
        button.bind("<Leave>", self.OnMouseExit)
        button.bind("<Button-1>", self.OnLeftHold)
        button.bind("<B1-ButtonRelease>", self.OnLeftRelease)
        button.place(x = self.Position.X, y = self.Position.Y, width=self.Width, height=self.Height)
        self.tks.append(button)
        
        super().Init()
        
    def OnMouseEnter(self, event):
        self.tks[0].configure(background="gray90")
        pass
    
    def OnMouseExit(self, event):
        self.tks[0].configure(background="gray80")
        pass
        
class GLabel(GUIControl):
    
    def __init__(self, name, tag, position, width, height, text, fontSize=16, image = ''):
        super().__init__(name=name, tag=tag, position=position, width=width, height=height)
        self.text = text
        self.fontSize = fontSize
        if image != '':
            self.image = GUI.Instance.ImageResources[image]
        else:
            self.image = image
        
    def Init(self):
        label = Label(master=self.canvas, background="gray80", image=self.image, text=self.text, font=Font(family=GUI.default_font, size=self.fontSize, weight='bold'))
        label.place(x=self.Position.X, y=self.Position.Y, width=self.Width, height=self.Height)
        
        self.tks = [label]
        super().Init()
        
class Dashboard(GUIControl):
    def __init__(self, name, tag="InGame", position=Vec2(0, 0), width = 240, height = 160):
        super().__init__(name=name, tag=tag, position=position, width=width, height=height)
        
        self.score = ""
        self.health = ""
        
    def Init(self):
        imageLength = int((self.Width-40)/2)
        boardFrame = tkinter.Frame(master=self.GUI.canvas, width=self.Width, height=self.Height)
        boardFrame.place(x=0, y=0, width=self.Width, height=self.Height)
        meme1 = tkinter.Label(master=boardFrame, height=imageLength, width=imageLength, background="gray80", text="meme1", font=Font(family=GUI.default_font, size=12, weight='bold'))
        meme1.place(x=15, y=5, width=imageLength, height=imageLength)
        meme2 = tkinter.Label(master=boardFrame, height=imageLength, width=imageLength, background="gray80", text="meme2", font=Font(family=GUI.default_font, size=12, weight='bold'))
        meme2.place(x=25 + imageLength, y=5, width=imageLength, height=imageLength)
        
        scoreLabel = tkinter.Label(width=50, height=20, text=self.score, font=Font(family=GUI.default_font, size=10, weight='bold'))
        scoreLabel.place(x=15, y=self.Height - 50, width=120, height=20)
        distanceLabel = tkinter.Label(width=50, height=20, text=self.health, font=Font(family=GUI.default_font, size=10, weight='bold'))
        distanceLabel.place(x=15, y=self.Height - 25, width=160, height=20)
        
        self.tks = [boardFrame, meme1, meme2, scoreLabel, distanceLabel]
        super().Init()
        
    def SetScore(self, score: int):
        self.tks[3].configure(text = "Score: " + str(score))
     
    def SetDistance(self, distance: int):
        self.tks[4].configure(text = "Run Distance: " + str(distance))
                
    def SetMeme1Image(self, img):
        if img != None and img != '':
            image = GUI.Instance.ImageResources[img]
            self.tks[1].configure(image = image)
        else:
            self.tks[1].configure(image = '')

    def SetMeme2Image(self, img):
        if img != None:
            image = GUI.Instance.ImageResources[img]
            self.tks[2].configure(image = image)
        else:
            self.tks[2].configure(image = '')

        
class DropOutCard(GUIControl):
    
    def __init__(self, name, tag, image, text, width, height, OnClose = None, fontSize = 14, stayTime = 3.0):
        super().__init__(name=name, tag=tag, position=Vec2(GUI.Instance.Width - width, -height), width=width, height=height)
        self.image = GUI.Instance.ImageResources[image]
        self.text = text
        self.fontSize = fontSize
        self.stayTime = stayTime
        
        self.status = 0
        self.waitTime = 0
        
        self.OnCloseEvent = OnClose
        
    def Init(self):
        frame = Frame(master=self.canvas)
        frame.place(x=self.Position.X, y=self.Position.Y, width=self.Width, height=self.Height)
        
        imageW = self.image.width()
        imageH = self.image.height()
        
        memeImg = Label(master=frame, image=self.image, background="gray")
        memeImg.place(x=5, y=self.Height/3, width=imageW, height=imageH)#width=self.Width/2, height=self.Width/4)
        
        text = Label(master=frame, text=self.text, font=Font(family=GUI.default_font, size=self.fontSize, weight='bold'))
        text.place(x=imageW + 20, y=5, width=self.Width - imageW - 20, height=self.Height-10)
        
        self.tks = [frame, memeImg, text]
        
        return super().Init()
    
    def Update(self, deltatime):
        super().Update(deltatime)
        if self.status == 0:
            self.Position += Vec2(0, 240*deltatime)
            if self.Position.Y > 0:
                self.status = 1
        elif self.status == 1:
            if self.waitTime < self.stayTime:
                self.waitTime += deltatime
            else:
                self.status = 2
        elif self.status == 2:
            self.Position -= Vec2(0, 240*deltatime)
            if self.Position.Y < -self.Height:
                if self.OnCloseEvent != None:
                    self.OnCloseEvent()
                GUI.Instance.Destroy(self)
        
class GameTitle(GUIControl):
    
    def __init__(self, position, width, height, text="Meme Cat Run"):
        super().__init__(name="Title", tag="MainMenu", position=position, width=width, height=height)
        self.text = text
        
    def Init(self):
        title = Label(master=self.canvas, background="white", text=self.text, font=Font(family=GUI.default_font, size=32, weight='bold'))
        title.place(x=self.Position.X, y=self.Position.Y, width=self.Width, height=self.Height)
        
        self.tks = [title]
        super().Init()
        
class ConfigPage(GUIControl):
    
    def __init__(self, config, name, tag, position, width, height):
        super().__init__(name=name, tag=tag, position=Vec2(-width, position.Y), width=width, height=height)
        
        self.finalPosition = position
        
        config.LoadFromFile()
        self.config = config
        
        self.nameVar = StringVar()
        self.bosskeyVar = StringVar()
        self.lockCam = IntVar()
        self.save = IntVar()
        
        self.status = 0
        self.Back = False
        
    def Init(self):
        frame = Frame(master=self.canvas)
        frame.place(x=self.Position.X, y=self.Position.Y, width=self.Width, height=self.Height)
        
        w = int(self.Width/4)
        h = int(self.Height/10)
        
        name = self.config.PlayerName
        bossKey = self.config.BossKey
        lockCameraY = self.config.LockCameraY
        autoSave = self.config.AutoSave
        
        settingTitle = Label(master=frame, text="Settings", width=w*2, height=h*2, font=Font(family=GUI.default_font, size=16, weight='bold'))
        settingTitle.place(relx=0.3, rely=0, width=w, height=h, anchor=tkinter.NW)
        
        nameLabel = Label(master=frame, text="Your Name", width=w, height=h, font=Font(family=GUI.default_font, size=12, weight='bold'))
        #nameLabel.grid(row=0, column=5, sticky=tkinter.NW)
        nameLabel.place(relx=0.1, rely=0.2, width=w, height=h, anchor=tkinter.NW)
        

        self.nameVar.set(name)
        nameTextbox = Entry(master=frame, textvariable=self.nameVar, font=Font(family=GUI.default_font, size=12, weight='bold'))
        #nameTextbox.grid(row=0, column=5, sticky=tkinter.NW)
        nameTextbox.place(relx = 0.5, rely = 0.2, width=w, height=h, anchor=tkinter.NW)
        
        bosskeyLabel = Label(master=frame, text="Boss key", width=w, height=h, font=Font(family=GUI.default_font, size=12, weight='bold'))
        #bosskeyLabel.grid(row=2, column=5, sticky=tkinter.NW)
        bosskeyLabel.place(relx = 0.1, rely = 0.4, width=w, height=h, anchor=tkinter.NW)
        
        self.bosskeyVar.set(bossKey)
        bosskeyTextbox = Entry(master=frame, textvariable=self.bosskeyVar, font=Font(family=GUI.default_font, size=12, weight='bold'))
        #bosskeyTextbox.grid(row=2, column=5, sticky=tkinter.NW)
        bosskeyTextbox.place(relx = 0.5, rely = 0.4, width=w, height=h, anchor=tkinter.NW)
        
        self.lockCam.set(int(lockCameraY))
        lockCamCheckbox = Checkbutton(master=frame, text="Lock Camera Y-axis", width=int(w*1.5), height=h, variable=self.lockCam, onvalue=1, offvalue=0, font=Font(family=GUI.default_font, size=10, weight='bold'))
        #lockCamCheckbox.grid(row=4, sticky=tkinter.W)
        lockCamCheckbox.place(relx=0.3, rely=0.6, width=int(w*2), height=h, anchor=tkinter.NW)
        
        self.save.set(int(autoSave))
        autoSaveCheckbox = Checkbutton(master=frame, text="Auto Save&Load Game process", width=int(w*1.5), height=h, variable=self.save, onvalue=1, offvalue=0, font=Font(family=GUI.default_font, size=10, weight='bold'))
        #lockCamCheckbox.grid(row=4, sticky=tkinter.W)
        autoSaveCheckbox.place(relx=0.3, rely=0.8, width=int(w*2), height=h, anchor=tkinter.NW)
        
        self.tks = [frame, settingTitle, nameLabel, nameTextbox, bosskeyLabel, bosskeyTextbox, lockCamCheckbox, autoSaveCheckbox]
        super().Init()
        
    def SaveConfig(self):
        
        outputInfo = None
        outputIcon = ''
        
        playerName = self.nameVar.get()
        for c in playerName:
            if ('a' <= c.lower() <= 'z') or ('0' <= c <= '9'):
                continue
            else:
                outputInfo = "(Unsaved)\nPlayer Name can only be \ncombines of alphabets or numbers"
        
        bosskey = self.bosskeyVar.get()
        if len(bosskey) != 1:
            outputInfo = "(Unsaved)\nBoss key can only be \na single English Charater"
        else:
            if not ('a' <= bosskey.lower() <= 'z'):
                outputInfo = "(Unsaved)\nBoss key can only be \na single English Charater"
                
        if outputInfo == None:        
            outputInfo = "Config Saved"
            outputIcon = 'save'

            self.config.PlayerName = playerName
            self.config.BossKey = bosskey
            self.config.LockCameraY = bool(self.lockCam.get())
            self.config.AutoSave = bool(self.save.get())
            
            self.config.SaveToFile()
            if playerName == "Cheater114514":
                return ("良いよ、来いよ！", "senpai")
        else:
            outputIcon = 'fail'
            
        return (outputInfo, outputIcon)
        
    def Return(self):
        self.Back = True
        
    def Update(self, deltatime):
        super().Update(deltatime)
        if self.status == 0:
            self.Position += Vec2(1000*deltatime, 0)
            if self.Position.X > self.finalPosition.X:
                self.status = 1
        elif self.status == 1:
            if self.Back:
                self.status = 2
        elif self.status == 2:
            self.Position -= Vec2(1000*deltatime, 0)
            if self.Position.X < -self.Width:
                GUI.Instance.Destroy(self)
        
        
class Leaderboard(GUIControl):
    
    def __init__(self, name, tag, position, width, height):
        super().__init__(name=name, tag=tag, position=position, width=width, height=height)
        self.finalPosition = position
        
    def Init(self):
        
        self.ReadScoreboard()
        
        frame = Frame(master=self.canvas, width = self.Width, height=self.Height)
        frame.place(x=self.Position.X, y=self.Position.Y, width=self.Width, height=self.Height)
        
        self.tks = [frame]
        
        bgLabel = Label(master=frame, background="gray96", font=Font(family=GUI.default_font, size=12, weight='bold'))
        bgLabel.place(relx=0, rely = 0, relwidth=1, relheight=0.1)
        nameLabel = Label(master=bgLabel, text="Name", font=Font(family=GUI.default_font, size=12, weight='bold'))
        nameLabel.place(relx=0, rely = 0.1, relwidth=0.3, relheight=0.8)
        scoreLabel = Label(master=bgLabel, text="Score", font=Font(family=GUI.default_font, size=12, weight='bold'))
        scoreLabel.place(relx=0.55, rely = 0.1, relwidth=0.2, relheight=0.8)
        distanceLabel = Label(master=bgLabel, text="Distance", font=Font(family=GUI.default_font, size=12))
        distanceLabel.place(relx=0.8, rely = 0.1, relwidth=0.2, relheight=0.8)
        
        self.tks.append(bgLabel)
        self.tks.append(nameLabel)
        self.tks.append(scoreLabel)
        self.tks.append(distanceLabel)
        
        i = 1
        dark = True
        for r in self.ranking:
            
            if dark:
                bgcolor = 'gray70'
                dark = False
            else:
                bgcolor = 'gray90'
                dark = True
            
            bgLabel = Label(master=frame, background=bgcolor, font=Font(family=GUI.default_font, size=12, weight='bold'))
            bgLabel.place(relx=0, rely = 0.1*i, relwidth=1, relheight=0.1)
            nameLabel = Label(master=bgLabel, text=f"{i}. {r[0]}", font=Font(family=GUI.default_font, size=12, weight='bold'))
            nameLabel.place(relx=0, rely = 0.1, relwidth=0.3, relheight=0.8)
            scoreLabel = Label(master=bgLabel, text=r[1], font=Font(family=GUI.default_font, size=12, weight='bold'))
            scoreLabel.place(relx=0.55, rely = 0.1, relwidth=0.2, relheight=0.8)
            distanceLabel = Label(master=bgLabel, text=r[2], font=Font(family=GUI.default_font, size=12))
            distanceLabel.place(relx=0.8, rely = 0.1, relwidth=0.2, relheight=0.8)
            
            self.tks.append(bgLabel)
            self.tks.append(nameLabel)
            self.tks.append(scoreLabel)
            self.tks.append(distanceLabel)
            
            i += 1
            
            if i > 10:
                break
        
        super().Init()

    def ReadScoreboard(self, path="./assets/user/leaderboard.json"):
        if not os.path.exists(path):
            self.ranking = []
            return
        file = open(path, 'r')
        content = file.read()
        file.close()
        self.ranking = []
        if content != '':
            root = json.loads(content)
        else:
            return
        
        self.ranking = []
        
        for data in root:
            self.ranking.append((data['name'], data['score'], data['distance']))
        
    def Close(self):
        GUI.Instance.Destroy(self)

        
        
#Deprecated
# class GAnimation(GUIControl):
    
#     def __init__(self, filePath, frameNum, position: Vec2 = Vec2(), width = 100, height = 50, leftClickEvent = None, rightClickEvent = None):
#         name = "Animation"
#         tag = "anim"
#         super().__init__(name, tag, position, width, height)
        
#         self.frames = self.ReadAnimFile(filePath)
#         self.totalFrame = frameNum
#         self.frameCount = 0
#         self.currentFrame = self.frames[self.frameCount]
        
#     def ReadAnimFile(self, path):
#         pass
    
#     def Init(self):
#         renderArea = tkinter.Image()
    
#     def FixedUpdate(self, deltatime):
#         super().FixedUpdate()
#         if self.frameCount < self.totalFrame:
#             self.frameCount += 1
#         else:
#             self.frameCount = 0
#         self.currentFrame = self.frames[self.frameCount]
        
#     def Update(self, deltatime):
#         super().Update()
#         self.tks['Animation'].configure(image=self.currentFrame)