import copy
import tkinter
from tkinter.constants import FALSE
import webbrowser
import platform
import os
from os import name, path
from enum import Enum
import json
from tkinter import StringVar, Tk
from typing import Text

#from PIL.Image import SAVE
import components
# import PIL.Image
# import PIL.ImageTk

from tkinter import Canvas

from GUI import ConfigPage, Dashboard, DropOutCard, GButton, GLabel, GUI, GameTitle, Leaderboard

from Utils import *

class Shape(Enum):
    Oval = 0
    Rect = 1
    Spirit = 2


class GameObj:
    """
    Game Object class, the base unit of the object in game,
    abstract from tkinter. Independent logic system and coordinate system with tkinter.
    """

    def __init__(self, position: Vec2, size: Vec2, shape: Shape = Shape.Oval, source = None, isDynamic = False, frameCount=1, **kwargs):
        self.position = position
        self.size = size

        self.gravity = 9.8
        self.velocity = Vec2(0, 0)
        self.grounded = 0

        self.name = "GameObject"

        self.tag = "general"

        self.shape = shape
        
        self.isDynamic = isDynamic
        self.LoadImageSource(source, frameCount)

        self.ctrl = None

        self.Components = []

    def Init(self):
        """
        Initialize all components in the GameObject
        """
        for comp in self.Components:
            try:
                comp.Init()
            except NameError:
                continue
            
    def LoadImageSource(self, source, frameCount=1):
        """
        Load image resources from the file,
        allows animation import, but currently do not support GIF file.
        """
        if isinstance(source, str):
            if self.isDynamic:
                fmt = source[-4:]
                if fmt == '.gif':
                    raise NotImplementedError("The gif animation import function can't function properly so this part is deprecated")
                    self.frames = []
                    self.frameCount = frameCount
                    self.currentFrame = 0
                    tag = path.split(source)[-1][:-4]
                    gif = PIL.Image.open(source).resize((int(self.size.X), int(self.size.Y)), PIL.Image.LANCZOS)
                    for i in range(frameCount):
                        Game.Instance.ImageResources[f'{tag}_{i}'] = PIL.ImageTk.PhotoImage(image=gif, format=f"gif -index {i+1}")
                        self.frames.append(f"{tag}_{i}")
                    gif.close()
                    self.source = Game.Instance.ImageResources[f'{tag}_0']
                    self.currentSpirit = self.source
                    self.nextSpirit = self.source
                elif fmt == '.png' or fmt == '.jpg':
                    self.frames = []
                    self.frameCount = frameCount
                    self.currentFrame = 0
                    tag = path.split(source)[-1][:-4]
                    for i in range(frameCount):
                        Game.Instance.ImageResources[f'{tag}_{i}'] = Utils.LoadImage(Utils.InsertString(source, -4, f'_{i}'), self.size.X, self.size.Y)
                        self.frames.append(f"{tag}_{i}")
                    self.source = Game.Instance.ImageResources[f'{tag}_0']
                    self.currentSpirit = self.source
                    self.nextSpirit = self.source
            else:
                # img = PIL.Image.open(source)
                # self.source = PIL.ImageTk.PhotoImage(image=img.resize((int(self.size.X * Game.Instance.PIXEL_SCALE), int(self.size.Y * Game.Instance.PIXEL_SCALE)), resample=PIL.Image.LANCZOS))
                # img.close()
                self.source = Utils.LoadImage(source, self.size.X * Game.Instance.PIXEL_SCALE, self.size.Y * Game.Instance.PIXEL_SCALE)
        else:
            self.source = source

    def FixedUpdate(self, deltatime):
        """
        call all fixed update in components.
        And control animation frame transit.
        """
        if self.isDynamic:
            self.currentSpirit = self.nextSpirit
            self.nextSpirit = Game.Instance.ImageResources[self.frames[self.currentFrame]]
            if self.currentFrame < self.frameCount-1:
                self.currentFrame += 1
            else:
                self.currentFrame = 0
        
        for comp in self.Components:
            try:
                comp.FixedUpdate(deltatime)
            except AttributeError:
                continue
        pass

    def Update(self, deltatime):
        """
        Call all Update in components.
        And update physical behaviour of the GameObject.
        """
        if self.isDynamic:
            self.source = self.currentSpirit
        
        if self.grounded <= 0:
            if (self.gravity > 0):
                self.velocity += (0, -self.gravity*deltatime)
        else:
            self.velocity.Y = max(0, self.velocity.Y)

        self.position += self.velocity * deltatime
        for comp in self.Components:
            try:
                comp.Update(deltatime)
            except AttributeError:
                continue
            
    def OnSpacePressed(self):
        """
        Not only space key actually, also include Up key and W key
        """
        for comp in self.Components:
            try:
                comp.OnSpacePressed()
            except AttributeError:
                continue

    def GetDistance(self, obj):
        """
        Get distance from self to the obj
        """
        return self | obj

    def GetCollider(self):
        """
        Quick method of getting collider component
        """
        for comp in self.Components:
            if Utils.IsType(comp, 'Collider'):
                return comp

    def OnCollision(self, collider):
        """
        Event function: Collision
        call on collision enter
        
        parameter:
            collider: the GameObj of the collider
        """
        if collider.tag == "ground":
            if collider.position.Y < self.position.Y:
                self.position.Y = collider.position.Y + collider.size.Y/2
                self.grounded += 1
        for comp in self.Components:
            if not Utils.IsType(comp, 'Collider'):
                try:
                    comp.OnCollision(collider)
                except AttributeError:
                    continue

    def OnExitCollision(self, collider):
        """
        Event function: Collision
        call on collision exit
        
        parameter:
            collider: the GameObj of the collider
        """
        if collider.tag == "ground":
            self.grounded -= 1
        for comp in self.Components:
            if not Utils.IsType(comp, 'Collider'):
                try:
                    comp.OnExitCollision(collider)
                except AttributeError:
                    continue

    def AddComponent(self, Component):
        """
        Add an component instance to the GameObj
        """
        if isinstance(Component, components.Component):
            Component.GameObject = self
            self.Components.append(Component)

    def GetComponent(self, T: type):
        """
        Get the component instance to the GameObj
        """
        for comp in self.Components:
            if type(comp) == T:
                return comp
        return None
    
    def copy(self):
        """
        Get a copy of this GameObj
        """
        copied = copy.copy(self)
        copied.position = copy.copy(self.position)
        copied.size = copy.copy(self.size)
        copied.velocity = copy.copy(self.velocity)
        comps = []
        for c in self.Components:
            comp = c.copy()
            comp.GameObject = copied
            comps.append(comp)
        copied.Components = comps
        return copied
        
class Configuration:
    """
    Config data class
    """
    
    def __init__(self) -> None:
        self.PlayerName = ""
        self.BossKey = 'B'
        self.LockCameraY = False
        self.AutoSave = True
        
    def LoadFromFile(self, path="./assets/user/config.json"):
        f = open(path, 'r')
        cfgObj = json.loads(f.read())
        f.close()
        
        self.attrNames = []
        for cfg in cfgObj:
            if hasattr(self, cfg):
                self.attrNames.append(cfg)
                setattr(self, cfg, cfgObj[cfg])
            
    def SaveToFile(self, path="./assets/user/config.json"):
        f = open(path, 'w')
        
        cfgObj = dict()
        for cfg in self.attrNames:
            cfgObj[cfg] = getattr(self, cfg)
        
        jsonData = json.dumps(cfgObj)
        f.write(jsonData)
        f.close()
        
class Game:
    """
    The main Game class, reponsible for:
    
    Initialize game process,
    Manage GameObjects,
    Recieve call and invoke GameObjects' events,
    Part of UI Logic,
    Global Functions,
    Global Variable/Constants,
    Apply Game Config
    """

    # At first it is considered that the Rendered Object should have a different scale to the Tk.
    # In another words, I try to make the coordinate system in abstract layer have a different scale to the actual render layer.
    # But that caused some problem at first and I found this might be meaningless (Although it sometimes makes arguments easier to modify)
    # While I was testing camera function, I found that not to set scale make life easier.
    # So I didn't change that back(original 16)
    PIXEL_SCALE = 1

    #When player below this height player will dead.
    Death_Altitude = -500

    #Static global instance make this instance easier to call, it's similar to Java's: public static Game Instance; Game.Instance = this;
    Instance = None
    
    #Save slot path
    SavePath = "./assets/user/save.json"

    def __init__(self) -> None:
        self.GameObjectList = []
        self.GameObjectTable_Name = {}
        self.GameObjectTable_tag = {}
        
        self.ImageResources = {}
        
        self.GAMING = False
        self.PAUSE = False
        self.END_GAME = False
        
        self.EXIT = False
        
        self.CHEAT_MODE = False
        
        self.Config = Configuration()
        self.Config.LoadFromFile()
        
        self.camera = None
        Game.Instance = self

    def OnKeyPressed(self, event):
        if event.char == self.Config.BossKey.lower():
            self.OnBossKeyPressed()
        if self.GAMING:
            if event.keysym == 'Escape':
                self.PauseGame()
            if event.char == ' ' or event.char == 'w' or event.keysym == 'Up':
                for obj in self.GameObjectList:
                    obj.OnSpacePressed()
    
    def OnBossKeyPressed(self):
        """
        Implemented boss key, Pause the Game and open the outlook mail to pretend that you are working.
        """
        if self.GAMING:
            self.PauseGame()
        
        url = 'http://outlook.office.com/'

        chrome_path = ''

        if platform.system() == 'Darwin':
            chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
        elif platform.system() == 'Windows':
            chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
        elif platform.system() == 'Linux':
            chrome_path = '/usr/bin/google-chrome %s'
            
        success = webbrowser.get(chrome_path).open_new_tab(url)
        if not success:
            webbrowser.open_new_tab(url)

    def Initialize(self,height, width, canvas: Canvas, tkRoot: Tk):
        """
        Very beginning step of initialize.
        
        parameters:
        
            height: Window height.          
            width: Window width.
            canvas: Main tk render canvas
            tkRoot: Tk instance
        """
        self.canvas: Canvas = canvas
        self.Height = height
        self.Width = width

        self.LoadPrefabs()
        tkRoot.bind('<Key>', self.OnKeyPressed)
        pass

    def deserilize_prefab(self, obj):
        """
        Instantiate prefab to a GameObject by datas.
        """
        def tryGet(key: str, default):
            if key in obj:
                return obj[key]
            else:
                return default
        
        gameObj = GameObj(Vec2.FromStr(tryGet('position', '0,0')),
                          Vec2.FromStr(tryGet('size', '0,0')), shape=Shape(tryGet('shape', 0)), source=(tryGet('source', None)), isDynamic=tryGet('isDynamic', False), frameCount=tryGet('frameCount', 1))
        gameObj.gravity = tryGet('gravity', 9.8)
        gameObj.name = tryGet('name', "")
        gameObj.tag = tryGet('tag', "general")

        if 'components' in obj:
            for comp in obj['components']:
                t = comp['__type__']
                comp.pop('__type__', None)
                gameObj.AddComponent(getattr(components, t)(**comp))
        
        return gameObj

    def LoadPrefabs(self, path="./assets/data/prefabs.json"):
        """
        Load prefabs from Json file
        """
        self.Prefabs = {}
        with open(path) as file:
            root = json.loads(file.read())
            for prefab in root['prefabs']:
                obj = self.deserilize_prefab(prefab)
                self.Prefabs[obj.name] = obj
            file.close()
            
    def PauseGame(self):
        def Resume():
            self.PAUSE=False
            GUI.Instance.DestroyByTag('game_pause')
            
        if not self.PAUSE:
            self.PAUSE = True
                
            def Restart():
                if path.exists(Game.SavePath):
                    os.remove(Game.SavePath)
                GUI.Instance.DestroyByTag('game_pause')
                self.RestartGame()
                
            def Menu():
                if self.Config.AutoSave:
                    self.SaveGame()   
                GUI.Instance.DestroyByTag('game_pause') 
                GUI.Instance.DestroyByTag('InGame')
                self.Back2MainMenu()
                
            w=self.Width/3
            h=self.Height/6
            
            GUI.Instance.Create(GButton(position=Vec2(self.Width/3, self.Height/4), text="Resume", width=w, height=h, leftClickEvent=Resume, name="resume", tag="game_pause"))
            GUI.Instance.Create(GButton(position=Vec2(self.Width/3, self.Height/4 + h*2), text="Restart Game", width=w, height=h, leftClickEvent=Restart, name="restart", tag="game_pause"))
            GUI.Instance.Create(GButton(position=Vec2(self.Width/3, self.Height/4 + h*3.2), text="Save &\n Main Menu" if self.Config.AutoSave else "Main Menu", width=w, height=h, leftClickEvent=Menu, name="main menu", tag="game_pause"))
        else:
            if not self.END_GAME:
                Resume()
    
    def SaveGame(self):
        saveObj = []
        player = self.GetPlayer()
        playerController = player.GetComponent(components.Player)
        mapGen = player.GetComponent(components.MapGenerator)
        playerData = {"name":"Player",
                      "tag":"player",
                      "position":self.GetPlayer().position.__str__(),
                      "score":playerController.Score,
                      "holding":playerController.HoldingMeme,
                      "lastEndPos":str(mapGen.LastEndPos),
                      "velocity":player.velocity.X
                      }
        saveObj.append(playerData)
        for go in self.GameObjectList[1:]:
            gameObj = {}
            if go.tag == 'ground' or go.tag == 'wall' or go.tag == 'meme':
                gameObj["name"] = go.name
                gameObj["tag"] = go.tag
                gameObj["position"] = go.position.__str__()
                gameObj["size"] = go.size.__str__()
                if go.tag == 'meme':
                    gameObj["meme"] = go.GetComponent(components.Meme).spirit
                saveObj.append(gameObj)
        
        with open(Game.SavePath, 'w') as file:
            jsonData = json.dumps(saveObj)
            file.write(jsonData)
            file.close()
            
    def LoadGame(self):
        file = open(Game.SavePath, 'r')
        jsonObj = json.loads(file.read())
        file.close()
        
        player = self.GetPlayer()
        player.position = Vec2.FromStr(jsonObj[0]['position']) + Vec2(0,60)
        player.velocity.X = jsonObj[0]['velocity']
        playerController = player.GetComponent(components.Player)
        playerController.Score = jsonObj[0]['score']
        playerController.HoldingMeme = jsonObj[0]['holding']
        self.dashboard.SetMeme1Image(playerController.HoldingMeme)
        player.GetComponent(components.MapGenerator).LastEndPos = Vec2.FromStr(jsonObj[0]['lastEndPos'])
        
        for goData in jsonObj[1:]:
            obj = GameObj(Vec2.FromStr(goData['position']), Vec2.FromStr(goData['size']))
            obj.name = goData['name']
            obj.tag = goData['tag']
            if obj.tag == 'ground' or obj.tag == 'wall':
                obj.gravity = 0
                obj.shape = Shape.Rect
                obj.AddComponent(components.Collider(0, rigid=False))
            elif obj.tag == 'meme':
                obj.position += Vec2(0, 60)
                obj.gravity = 180
                obj.shape = Shape.Spirit
                obj.AddComponent(components.Collider(0, rigid=True))
                obj.AddComponent(components.Meme(goData['meme']))
            self.InstantiateGameObject(obj, obj.name, obj.tag)
                
    def HaveSaveToLoad(self):
        """
        Check if there is a save file and if the config state that we need to load it.
        """
        if self.Config.AutoSave:
            if path.exists(Game.SavePath):
                return True
        return False
                
    def MainMenu(self):
        self.GAMING = False
        
        self.lbOpen = False
        self.leaderboard = None
                
        def Start():
            GUI.Instance.DestroyByTag("MainMenu")
            self.StartGame()
            
        def ShowLeaderboard():
            if not self.lbOpen:
                self.leaderboard = GUI.Instance.Create(Leaderboard("Leaderboard", "leaderboard", Vec2(self.Width/10, self.Height/10), self.Width/5*4, self.Height/5*4))
                self.lbOpen = True
            else:
                self.leaderboard.Close()
                self.lbOpen = False
        
        GUI.Instance.Create(GameTitle(Vec2(self.Width/4, self.Height/8), width=int(self.Width/2), height=int(self.Height/6), text="Meme Cat Run"))
        
        GUI.Instance.Create(GButton(Vec2(self.Width/3, self.Height/6*2), width=int(self.Width/3), height=int(self.Height/6), text="Continue Game" if self.HaveSaveToLoad() else "Start Game", name="start", tag="MainMenu", leftClickEvent=Start))
        GUI.Instance.Create(GButton(Vec2(self.Width/3, self.Height/6*3 + 10), width=int(self.Width/3), height=int(self.Height/6), text="Settings", name="setting", tag="MainMenu", leftClickEvent=self.ShowConfigPage))
        GUI.Instance.Create(GButton(Vec2(self.Width/3, self.Height/6*4 + 20), width=int(self.Width/3), height=int(self.Height/6), text="Quit", name="quit", tag="MainMenu", leftClickEvent=self.ExitGame))
        
        lbButton = GUI.Instance.Create(GButton(Vec2(0, 0), width=self.Width/10, height=self.Height/10, text = "LB", name="leaderboard", tag="MainMenu", leftClickEvent=ShowLeaderboard))
        
    def ShowConfigPage(self):
        def CloseSettingPage():
            settingPage.Return()
            GUI.Instance.Destroy(saveBtn)
            GUI.Instance.Destroy(returnBtn)
            
        def SaveConfigs():
            result = settingPage.SaveConfig()
            GUI.Instance.Create(DropOutCard("saveNotify", "config", result[1], result[0], 360, 160, fontSize=12, stayTime=1.0))
        
        settingPage = GUI.Instance.Create(ConfigPage(config=self.Config, name="SettingsPage", tag="config", position=Vec2(self.Width/8, self.Height/8), width=self.Width/8*6, height=self.Height/8*6))
        
        saveBtn = GUI.Instance.Create(GButton(Vec2(self.Width/5, self.Height/6*5), width=int(self.Width/3), height=int(self.Height/8), text="Save", name="saveConfig", tag="config", leftClickEvent=SaveConfigs))
        
        returnBtn = GUI.Instance.Create(GButton(Vec2(self.Width/5*3, self.Height/6*5), width=int(self.Width/3), height=int(self.Height/8), text="Return", name="return", tag="config", leftClickEvent=CloseSettingPage))
            
    def ResetGame(self):
        """
        Reset all GameObjects and clear Tk rendered cache.
        """
        self.GameObjectList = []
        self.GameObjectTable_Name = {}
        self.GameObjectTable_tag = {}
        
        self.canvas.delete('all')

    def StartGame(self):
        self.GAMING = True
        self.dashboard = GUI.Instance.Create(Dashboard("GameBoard", tag="InGame"))
        if self.Config.PlayerName == "Cheater114514":
            self.CHEAT_MODE = True
        else:
            self.CHEAT_MODE = False
        player = self.InstantiateGameObject(self.Prefabs['Player'])
        if self.HaveSaveToLoad():
            self.LoadGame()
        self.camera = Camera(player, self.canvas, self.Width, self.Height) 

    def RestartGame(self):
        self.END_GAME = False
        self.PAUSE = False
        
        self.ResetGame()
        self.StartGame()
        pass
    
    def Back2MainMenu(self):
        self.END_GAME = False
        self.PAUSE = False
        
        self.ResetGame()
        self.MainMenu()
        pass

    def RecordScore(self, path="./assets/user/leaderboard.json"):
        player = self.GetPlayer().GetComponent(components.Player)
        score = player.Score
        distance = player.RunningDistance
        
        name = self.Config.PlayerName
                
        if os.path.exists(path):        
            file = open(path, 'r')
            Json = file.read()
            file.close()
        else:
            file = open(path, 'w+')
            Json = file.read()
            file.close()
            
        if Json != "":
            root: list = json.loads(Json)
        
            i = 0
            for data in root:
                if score > data['score']:
                    root.insert(i, {"name":name, "score": score, "distance": distance})
                    break
                else:
                    i += 1
                    continue
            else:
                root.append({"name":name, "score": score, "distance": distance})
        else:
            i=0
            
            root = []
            root.append({"name":name, "score": score, "distance": distance})

        newRecord = False

        if i == 0:
            newRecord = True
            
        file = open(path, 'w')
        file.write(json.dumps(root))
        file.close()
        
        return score, newRecord

    def GameEnd(self):
        self.END_GAME = True
        self.PAUSE = True
        if path.exists(Game.SavePath):
            os.remove(Game.SavePath)
        
        def Restart():
            GUI.Instance.DestroyByTag("InGame")
            GUI.Instance.DestroyByTag("game_end")
            self.RestartGame()
            
        def MainMenu():
            GUI.Instance.DestroyByTag("InGame")
            GUI.Instance.DestroyByTag("game_end")
            self.Back2MainMenu()
            
        res = self.RecordScore()
        score = res[0]
        newRcd = res[1]
            
        w=self.Width/3
        h=self.Height/6
        
        GUI.Instance.Create(GLabel(name="End Label", tag="game_end", position=Vec2(self.Width/3, self.Height/4), width=w*1.2, height=h, text="Opps...\nBetter luck next time", fontSize=20))
        GUI.Instance.Create(GLabel(name="Score Label", tag="game_end", position=Vec2(self.Width/3, self.Height/4*1.2 + h), width=w*1.2, height=h, text=f"Score: {score}" + (" (New Record!)" if newRcd else ""), fontSize=12))
        GUI.Instance.Create(GButton(position=Vec2(self.Width/3, self.Height/2), text="Restart Game", width=w, height=h, leftClickEvent=Restart, name="restart button", tag="game_end"))
        GUI.Instance.Create(GButton(position=Vec2(self.Width/3, self.Height/2*1.4), text="Main Menu", width=w, height=h, leftClickEvent=MainMenu, name="main menu", tag="game_end"))
        
    def ExitGame(self):
        self.EXIT = True
        
    def Update(self, deltatime):
        if not self.PAUSE:
            for obj in self.GameObjectList:
                obj.Update(deltatime)

    def FixedUpdate(self, deltatime):
       if not self.PAUSE:
            for obj in self.GameObjectList:
                obj.FixedUpdate(deltatime)
        #print(f'collision checked {self.c} times in last fixed update\n')
        #print(f'collision check jumped {self.j} times in last fixed update\n')

    def CreateGameObject(self, position=Vec2(0, 0), size=Vec2(1, 1), shape=0, source=None, name="", tag="general"):
        """
        Create a new blank GameObject from basic parameters.
        """
        if name == "":
            name = "go_" + self.GameObjectList.__len__()

        go = GameObj(position, size, shape=shape)
        if shape == Shape.Spirit:
            go.source = source
        go.name = name
        go.tag = tag

        self.GameObjectList.append(go)
        if name in self.GameObjectTable_Name.keys():
            #print("Error: repeated name, Game Object name must be unique")
            name = go.name + '_' + self.GameObjectList.__len__()
            go.name = name
        self.GameObjectTable_Name[name] = go

        if tag in self.GameObjectTable_tag.keys():
            self.GameObjectTable_tag[tag].append(go)
        else:
            self.GameObjectTable_tag[tag] = [go]

        go.Init()
        pass

    def InstantiateGameObject(self, object: GameObj, name="", tag=""):
        """
        Make a copy of a GameObject and load it into the GameObject array for management in Game.
        """
        obj = object.copy()
        if name == "":
            name = obj.name + "_" + str(len(self.GameObjectList))
            obj.name = name
        else:
            obj.name = name

        if tag == "":
            tag = obj.tag
        else:
            obj.tag = tag

        if name in self.GameObjectTable_Name.keys():
            #print("Error: repeated name, Game Object name must be unique")
            name = obj.name + "_" + str(self.GameObjectList.__len__())
            obj.name = name
        self.GameObjectTable_Name[name] = obj

        if tag in self.GameObjectTable_tag.keys():
            self.GameObjectTable_tag[tag].append(obj)
        else:
            self.GameObjectTable_tag[tag] = [obj]
            
        if obj.tag == 'player':
            print('instantiate player: ', hex(id(obj)))

        obj.Init()
        self.GameObjectList.append(obj)
        return obj
    
    def GetPlayer(self):
        """
        Quick function of getting a player's GameObj instance.
        """
        for o in self.GameObjectList:
            if o.tag == "player":
                return o

    def DestroyGameObject(self, obj):
        """
        Completely destroy the GameObj instance.
        Immediate remove from canvas.
        """
        if obj.ctrl != None:
            self.camera.canvas.delete(obj.ctrl)
            self.camera.ExistElements.remove(obj.ctrl)
        self.GameObjectList.remove(obj)
        self.GameObjectTable_Name.pop(obj.name, None)
        self.GameObjectTable_tag[obj.tag].remove(obj)

    def GetGlobalGameObjWithCollider(self):
        objs = []
        for go in self.GameObjectList:
            if go.GetCollider() != None:
                objs.append(go)
        return objs


class Camera:
    """
    The camera class is responsible for render all the virtual GameObjects to the real Tk Canvas.
    """
    
    # the position of the camera is the center point of the camera screen
    def __init__(self, player: GameObj, canvas: Canvas, width=300, height=400) -> None:
        self.Player = player
        self.canvas = canvas
        
        self.AbsPosition = player.position
        self.Width = width
        self.Height = height
        self.GCBoarderOffset = 100
        self.ExistElements = []
        self.debugText = -1

    def RenderElements(self):
        """
        filter & render the GameObjects from the back-end(abstract) layer to the front-end(Tkinter)
        """
        PIXEL_SCALE = Game.Instance.PIXEL_SCALE
        scaleX = PIXEL_SCALE # self.canvas.winfo_width() / self.Width
        scaleY = PIXEL_SCALE # self.canvas.winfo_height() / self.Height
        elements = self.FilterVisibleObjects(GC=True)
        
        #Debug.SetDebugInfo('Nothing')
        
        # if self.debugText == -1:
        #     self.debugText = self.canvas.create_text(100, 30, text=Debug.debugInfo)
        
        self.canvas.itemconfig(self.debugText, text = Debug.debugInfo)
        
        x = 0
        
        for obj in elements:
            relX = (obj.position.X - self.left)
            relY = self.Height - (obj.position.Y - self.bottom + obj.size.Y)
            
            if Utils.Contains(self.ExistElements, obj.ctrl):
                self.canvas.moveto(obj.ctrl, relX, relY)
                if obj.isDynamic:
                    self.canvas.itemconfig(obj.ctrl, image=obj.source)
            else:
                if obj.shape == Shape.Spirit:
                    obj.ctrl = self.canvas.create_image(relX, relY, image = obj.source)
                elif obj.shape == Shape.Oval:
                    obj.ctrl = self.canvas.create_oval((relX, relY, relX + obj.size.X, relY + obj.size.Y), fill="red")
                elif obj.shape == Shape.Rect:
                    obj.ctrl = self.canvas.create_rectangle((relX, relY, relX + obj.size.X, relY + obj.size.Y), fill="red")
                else:
                    print('unknow render target: ', obj.shape)
                if obj.ctrl != None:
                    self.ExistElements.append(obj.ctrl)
                    self.canvas.moveto(obj.ctrl, relX, relY)
                else:
                    Game.Instance.DestroyGameObject(obj)
            x += 1
        #print('canvas operation: {0} times'.format(x))
        self.canvas.pack()
        pass

    def UpdateBoarderInfo(self):
        """
        Update the camera rander area location
        """
        pos = copy.copy(self.Player.position)
        pos = Vec2(pos.X + self.Width/4, max(int(Game.Death_Altitude / 3), pos.Y) if not Game.Instance.Config.LockCameraY else 0)
        self.top = pos.Y + self.Height/2
        self.bottom = pos.Y - self.Height/2
        self.right = pos.X + self.Width/2
        self.left = pos.X - self.Width/2

    def FilterVisibleObjects(self, GC=True):
        """
        Filter the GameObjects which are visiable by the current camera location.
        
        parameters:
        
        GC: If true, GameObjects behind / below the Camera GC range will be destroyed in order to release memory.
        """
        self.UpdateBoarderInfo()
        gos = []
        for go in Game.Instance.GameObjectList:
            if (go.position.X > self.left - self.GCBoarderOffset and go.position.X < self.right + self.GCBoarderOffset) and (go.position.Y > self.bottom - self.GCBoarderOffset and go.position.Y < self.top + self.GCBoarderOffset):
                gos.append(go)
            else:
                if GC:
                    if go.position.X + go.size.X < self.left - self.GCBoarderOffset or go.position.Y + go.size.Y < self.bottom - self.GCBoarderOffset:
                        Game.Instance.DestroyGameObject(go)
        return gos
