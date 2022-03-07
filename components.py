import json
from GUI import DropOutCard
from random import Random

from Game import *
from Utils import *

jumped = 0

class Component:
    """
    Component base class
    """
    
    def __init__(self, **kwargs):
        self.GameObject = None
        
    def Init(self):
        """
        event function: Initialize the component, run when Component is instantiated.
        """
        pass
    
    def Update(self, deltatime):
        """
        event function: General Update function, invoke from main Update function
        """
        pass

    def FixedUpdate(self, deltatime):
        """
        event function: Fixed Update func, invoke from main Fixed Update function
        """
        pass

    def OnCollision(self, collider):
        """
        event function: Fixed Update func, call by GameObject when Collision Enter
        """
        pass
    
    def OnExitCollision(self,collider):
        """
        event function: Fixed Update func, call by GameObject when Collision Exit
        """
        pass
    
    def OnSpacePressed(self):
        """
        event function: Fixed Update func, call by GameObject when Collision Exit
        """
        pass
    
    def copy(self):
        """
        Get a copy of this component
        """
        return copy.copy(self)
        

class Collider(Component):
    """
    Collider Component.
    """
    
    def __init__(self, ColliderType = 0, rigid = False, width = 0, height = 0, radius = 0, bouncy = 0.0, **kwargs) -> None:
        """
            Collider Type:
                0: SquareCollider
                1: SphereCollider
        """
        super(Collider, self).__init__()
        self.Shape = ColliderType
        self.Bouncy = bouncy
        if ColliderType == 0:
            self.Width = width
            self.Height = height
        elif ColliderType == 1:
            self.Radius = radius
            self.Width = radius*2
            self.Height = radius*2
        
        self.rigid = rigid
        self.rect = Vec2(self.Width, self.Height)
        self.checked = []
        self.LastInCollision = []
        self.InCollision = []
        
    def Init(self):
        if self.Shape == 0:
            if self.Width == 0:
                self.Width = self.GameObject.size.X
                    
            if self.Height == 0:
                self.Height = self.GameObject.size.Y
            
        if self.Shape == 1:
            if self.Radius == 0:
                self.Radius = self.GameObject.size.X/2
                self.Width = self.GameObject.size.X
                self.Height = self.GameObject.size.X
        
        self.rect = Vec2(self.Width, self.Height)
        pass      

    def UpdateSquareCollisionInfo(self):
        pos = self.GameObject.position
        self.top = pos.Y + self.Height
        self.bottom = pos.Y
        self.right = pos.X + self.Width
        self.left = pos.X

    def SquaresCollide(self, obj):
        self.UpdateSquareCollisionInfo()
        collider = obj.GetCollider()
        collider.UpdateSquareCollisionInfo()
        if (collider.bottom < self.top < collider.top or collider.bottom < self.bottom < collider.top) and (collider.left < self.left < collider.right or collider.left < self.right < collider.right):
            return True
        else:
            return False
        
    def SpheresCollide(self, obj):
        collider = obj.GetCollider()
        apos = self.GameObject.position + self.rect/2
        bpos = obj.position + self.rect/2
        dist = apos - bpos
        if dist <= self.Radius + collider.Radius:
            return True
        else:
            return False    
    
    def SphereSquareCollide(self, obj):
        self.UpdateSquareCollisionInfo()
        obj.collider.UpdateSquareCollisionInfo()
        collider = obj.GetCollider()
        pos = self.GameObject.position + self.rect/2
        if (self.top > collider.bottom or self.bottom < collider.top) and (self.left < collider.right or self.right > collider.left):
            if (pos.Y > collider.bottom and pos.Y < collider.top) or (pos.X > collider.left and pos.X < collider.right):
                    return True
            vertex = Vec2()
            if (self.top > collider.bottom and self.left < collider.right):
                vertex = Vec2(collider.bottom, collider.right)
            elif (self.top > collider.bottom and self.right > collider.left):
                vertex = Vec2(collider.bottom, collider.left)
            elif (self.bottom < collider.top and self.left < collider.right):
                vertex = Vec2(collider.top, collider.right)
            elif (self.bottom < collider.top and self.right > collider.left):
                vertex = Vec2(collider.top, collider.left)
            dist = self.GameObject.position | vertex
            if dist <= self.Radius:
                return True
        return False

    def OnCollision(self, collider):
        if not Utils.Contains(self.LastInCollision, collider):           
            #self.GameObject.velocity -= (collider.velocity + self.GameObject.velocity)*self.Bouncy
            self.GameObject.OnCollision(collider)
        self.InCollision.append(collider)
        pass
    
    def OnExitCollision(self, collider):
        self.GameObject.OnExitCollision(collider)

    def Update(self, deltatime):
        if self.rigid:
            colliders = Game.Instance.GetGlobalGameObjWithCollider()

            self.jumped = 0
            for cldObj in colliders:
                cld = cldObj.GetCollider()
                if self is cld:
                    continue
                if id(cld) in self.checked:
                    self.jumped += 1
                    continue
                if self.Shape == 0:
                    if cld.Shape == 0:
                        if not self.SquaresCollide(cldObj):
                            continue
                    else:
                        continue
                elif self.Shape == 1:
                    if cld.Shape == 0:
                        if not self.SphereSquareCollide(cldObj):
                            continue
                    elif cld.Shape == 1:
                        if not self.SpheresCollide(cldObj):
                            continue
                self.OnCollision(cldObj)
                cld.OnCollision(self.GameObject)
                cld.checked.append(id(self))
            for c in self.LastInCollision:
                if not c in self.InCollision:
                    self.OnExitCollision(c)
                    c.GetCollider().OnExitCollision(self.GameObject)
            # Debug.debugInfo = ""
            # for col in self.InCollision:
            #     Debug.debugInfo += col.name + ',\n'
            self.LastInCollision = self.InCollision
            self.InCollision = []
            self.checked = []
            
    def copy(self):
        cp = super().copy()
        cp.rect = copy.copy(self.rect)
        cp.checked = []
        cp.LastInCollision = []
        cp.InCollision = []
        return cp
        
class MapGenerator(Component):
    
    def __init__(self, possibilities: dict, seed = -1, **kwargs) -> None:
        super(MapGenerator, self).__init__()
        normalScale = 1 / sum(possibilities.values())
        normalizedPosbs = {}
        for m in possibilities:
            normalizedPosbs[m] = possibilities[m] * normalScale
        self.Possibilities = normalizedPosbs
        if seed == -1:
            self.rnd = Random()
        else:
            self.rnd = Random(seed)
        
        self.Prefabs = {}    
        self.LastEndPos = Vec2(0, 0)
        
    def AddPrefab(self, tag, prefab):
        if tag not in self.Prefabs:
            self.Prefabs[tag] = prefab
        else:
            raise NameError("Repeated tags in map generator prefab")
        pass
    
    def __Generate(self, prefab: GameObj, endPointOffset: Vec2 = Vec2(0, 0), specieficPos = None, isGround = True):
        pos = self.LastEndPos if specieficPos == None else specieficPos
        prefab.position = pos
        Game.Instance.InstantiateGameObject(prefab, tag = "ground" if isGround else prefab.tag)
        self.LastEndPos += endPointOffset
        
    def __GenerateFlatGround(self, maxLength = 5):
        gnd: GameObj = Game.Instance.Prefabs['horizontal_l']
        r = self.rnd.randint(3, maxLength)
        for i in range(r):
            self.__Generate(prefab=gnd, endPointOffset=Vec2(gnd.size.X, 0))
    
    def __GenerateGap(self):
        gnd: GameObj = Game.Instance.Prefabs['horizontal_m']
        for i in range(self.rnd.randint(2, 5)):
            self.__Generate(prefab = gnd, endPointOffset=Vec2(gnd.size.X, 0))
        self.LastEndPos += Vec2(200, 0)
        for i in range(self.rnd.randint(2, 5)):
            self.__Generate(prefab = gnd, endPointOffset=Vec2(gnd.size.X, 0))
        pass
    
    def __GenerateHill(self):
        gnd: GameObj = Game.Instance.Prefabs['horizontal_l']
        wall: GameObj = Game.Instance.Prefabs['verticle_h']
        for i in range(self.rnd.randint(3, 5)):
            self.__Generate(prefab = gnd, endPointOffset=Vec2(gnd.size.X, 0))
        self.__Generate(prefab=wall, endPointOffset=Vec2(wall.size.X, wall.size.Y), isGround=False)
        for i in range(self.rnd.randint(3, 10)):
            self.__Generate(prefab = gnd, endPointOffset=Vec2(gnd.size.X, 0))
        self.LastEndPos.Y -= wall.size.Y
        self.__Generate(prefab=wall, endPointOffset=Vec2(wall.size.X, 0), isGround=True)
        for i in range(self.rnd.randint(3, 5)):
            self.__Generate(prefab = gnd, endPointOffset=Vec2(gnd.size.X, 0))
        pass
        
    def __GenerateTrap(self):
        gnd: GameObj = Game.Instance.Prefabs['horizontal_l']
        trap: GameObj = Game.Instance.Prefabs['trap_1']
        for i in range(self.rnd.randint(2, 3)):
            self.__Generate(prefab = gnd, endPointOffset=Vec2(gnd.size.X, 0))
        self.__Generate(prefab=trap, endPointOffset=(0, 0), isGround=False)
        for i in range(self.rnd.randint(2, 3)):
            self.__Generate(prefab = gnd, endPointOffset=Vec2(gnd.size.X, 0))
        pass    
        
    def __gen_test(self):
        gnd_s: GameObj = Game.Instance.Prefabs['horizontal_s']
        gnd_m: GameObj = Game.Instance.Prefabs['horizontal_m']
        gnd_l: GameObj = Game.Instance.Prefabs['horizontal_l']
        self.__Generate(prefab=gnd_l, endPointOffset=Vec2(gnd_l.size.X, 0))
        self.__Generate(prefab=gnd_l, endPointOffset=Vec2(gnd_l.size.X, 0))
        self.__Generate(prefab=gnd_l, endPointOffset=Vec2(gnd_l.size.X, 0))
        self.__Generate(prefab=gnd_l, endPointOffset=Vec2(gnd_l.size.X, 0))
        
    def GenerateNext(self, length = 3, specificPossibs = {}):
        posbs = {**self.Possibilities, **specificPossibs}
        lastBlockEnding = Vec2()
        
        lastBlockEnding = self.LastEndPos
        for i in range(length):
            r = self.rnd.randint(0, 2)
            if r == 0:
                self.__GenerateFlatGround()
            elif r == 1:
                self.__GenerateHill()
            elif r == 2:
                self.__GenerateGap()
            elif r == 3:
                self.__GenerateTrap()
        blockEnding = self.LastEndPos
        
        distance = blockEnding - lastBlockEnding
        
        self.LastEndPos = Vec2(lastBlockEnding.X, 30)
        
        memes = list(posbs.keys())
        ps = list(posbs.values())
        memeNumPerBlock = length
        memeGenDistance = int(distance.X/memeNumPerBlock)
        for i in range(memeNumPerBlock):         
            if not Game.Instance.CHEAT_MODE:
                r = self.rnd.randint(0, len(memes) - 1)
                meme = memes[r]
                p = posbs[meme]
                
                r1 = self.rnd.random()
                idx = 0
                sum = 0
                for v in ps:
                    if r1 < sum + v:
                        break
                    else:
                        sum += v
                        idx += 1
                
                prefab: GameObj = Game.Instance.Prefabs['meme'].copy()
                prefab.AddComponent(Meme(meme))
                self.__Generate(prefab, endPointOffset=Vec2(self.rnd.randint(int(memeGenDistance/2), memeGenDistance), 120), isGround=False)
            else:
                r = self.rnd.randint(0, len(memes) - 1)
                meme = memes[r][:-1]
                    
                for i in range(2):
                    prefab: GameObj = Game.Instance.Prefabs['meme'].copy()
                    prefab.AddComponent(Meme(meme + str(i)))
                    self.__Generate(prefab, endPointOffset=Vec2(self.rnd.randint(int(memeGenDistance/2), memeGenDistance), 120), isGround=False)
        
        self.LastEndPos = blockEnding

    def Init(self):
        #self.__gen_test()
        if Game.Instance.HaveSaveToLoad():
            for i in range(len(Game.Instance.GameObjectList)-1, 0, -1):
                go = Game.Instance.GameObjectList[i]
                if go.tag == 'ground':
                    self.LastEndPos.X = go.position.X + go.size.X
                    break
        else:
            self.__GenerateFlatGround(10)
        # for meme in ['saladCat_0', 'saladCat_1']:
        #     prefab: GameObj = Game.Instance.Prefabs['meme'].copy()
        #     prefab.AddComponent(Meme(meme))
        #     self.__Generate(prefab, specieficPos=Vec2(self.rnd.randint(50, 150), 60), isGround=False)

    def Update(self, deltatime):
        if (self.GameObject.position | self.LastEndPos) < 1200:
            self.GenerateNext()
        pass
    
    def copy(self):
        cp = super().copy()
        cp.LastEndPos = copy.copy(self.LastEndPos)
        return cp

class Meme(Component):
    
    def __init__(self, spirit, **kwargs):
        """
        docstring
        """
        super(Meme, self).__init__()
        self.spirit = spirit
        pass
    
    
    def Init(self):
        super().Init()
        size: Vec2 = self.GameObject.size * Game.PIXEL_SCALE
        self.GameObject.LoadImageSource("./assets/images/{0}.png".format(self.spirit))
        #self.GameObject.source = Game.Instance.ImageResources[self.spirit]
        
    def OnCollision(self, collider):
        super().OnCollision(collider)        
        if collider.tag == "ground" or collider.tag == "wall":
            self.gravity = 0
            self.GameObject.GetCollider().rigid = False

class Player(Component):
    
    def __init__(self, **kwargs) -> None:
        super(Player, self).__init__()
        self.LoadMemes()
        
        def tryGet(key, default):
            if key in kwargs:
                return kwargs[key]
            else:
                return default
        
        self.InitialSpeed = tryGet('InitialSpeed', 180)
        self.MaxHealth = tryGet('InitialHealth', 6)
        self.JumpVelocity = tryGet('JumpVelocity', 240)
        
        self.Health = self.MaxHealth
        self.HoldingMeme = ""
        self.Score = 0
        self.RunningDistance = 0
    
    def LoadMemes(self):
        self.MemeTable = {}
        jsonFile = open('assets/data/Memes.json', 'r')
        
        jsonRoot = json.loads(jsonFile.read())
        jsonFile.close()
        
        memes = jsonRoot['memes']
        self.MemeList = []
        
        memeImgFiles = [f+'.png' for f in memes]
        GUI.Instance.ImageResources = {**GUI.Instance.ImageResources, **Utils.LoadImages("./assets/images/", memeImgFiles, 160, 80)}
        for sp in memes:
            for i in [0,1]:
                label = f"{sp}_{i}"
                self.MemeList.append(label)
                GUI.Instance.ImageResources[label] = Utils.LoadImage(f"./assets/images/{label}.png", 100, 100)
                Game.Instance.ImageResources[label] = Utils.LoadImage(f"./assets/images/{label}.png", 48, 48)
                
        quotes = jsonRoot["quotes"]
        self.MemeQuotes = quotes
            
        # matchings = jsonRoot['matching']
        # for mat in matchings:
        #     first = mat
        #     second = matchings[mat]
        #     if second != None:
        #         if type(second) != int:
        #             self.MemeTable[first] = second
        #             self.MemeTable[second] = first
        #         else:
        #             for i in range(0, second):
        #                 self.MemeTable[f"{first}_{i}"] = i
                    
    def Match(self, meme):
        if meme in self.MemeList:
            if self.HoldingMeme == meme:
                return 1
            else:
                if self.HoldingMeme[:-2] == meme[:-2]:
                    self.HoldingMeme = ""
                    return 3
                else:
                    self.HoldingMeme = meme
                    return 0
        else:
            raise KeyError()
        # if self.HoldingMemes.__len__() == 0:
        #     if (meme in self.MemeTable.keys()):
        #         self.HoldingMemes.append(meme)
        #     else:
        #         raise KeyError("Unknow meme tag")
        #     return True
        # else:
        #     if meme in self.HoldingMemes:
        #         return None
        #     holding = self.HoldingMemes[0]
        #     if(holding in self.MemeTable.keys()):
        #         match = self.MemeTable[holding]
        #         if type(match) == int:
        #             if meme[:-2] == holding[:-2]:
        #                 self.HoldingMemes.append(meme)
        #                 return True
        #             else:
        #                 return False
        #         elif type(match) == str:
        #             if match == meme:
        #                 return True
        #             else:
        #                 return False
        #         else:
        #             raise TypeError("Unexpected matching type")
                
    def OnCollision(self, collider):
        if collider.tag == 'meme':
            meme = collider.GetComponent(Meme)
            if not meme == None:
                gainScore = self.Match(meme.spirit)
                if gainScore > 0:
                    self.Score += gainScore*10
                if gainScore == 3:
                    Game.Instance.dashboard.SetMeme2Image(meme.spirit)
                    memeGroup = meme.spirit[:-2]
                    quote = self.MemeQuotes[memeGroup]
                    GUI.Instance.Create(DropOutCard("memePaired", 'InGame', meme.spirit[:-2], quote, 160*2, 80*2, OnClose=self.ResetDashboardMeme, fontSize=8))
                else:
                    Game.Instance.dashboard.SetMeme1Image(meme.spirit)
                    Game.Instance.dashboard.SetMeme2Image(None)
                # else:
                #     if res == False:
                #         self.Health -= 1
            Game.Instance.DestroyGameObject(collider)
        elif collider.tag == 'trap':
            self.Health -= 1
        elif collider.tag == 'wall':
            Game.Instance.GameEnd()
            
        Game.Instance.dashboard.SetScore(self.Score)
        Game.Instance.dashboard.SetHealth(self.Health)
        
    def ResetDashboardMeme(self):
        if self.HoldingMeme == "":
            Game.Instance.dashboard.SetMeme1Image(None)
            Game.Instance.dashboard.SetMeme2Image(None)
        else:
            Game.Instance.dashboard.SetMeme2Image(None)
        
    def Init(self):
        
        self.LoadMemes()
        self.GameObject.velocity = Vec2(self.InitialSpeed, 0)
        
        Game.Instance.dashboard.SetScore(self.Score)
        Game.Instance.dashboard.SetDistance(self.RunningDistance)
            
    def Update(self, deltatime):
        #Debug.debugInfo = f" score: {self.Score}\n Health: {self.Health}"
        self.GameObject.velocity += Vec2(0.001, 0)
        Game.Instance.dashboard.SetDistance(self.RunningDistance)
        
        if self.Health == 0:
            Game.Instance.GameEnd()
        
        if self.GameObject.position.Y < Game.Death_Altitude:
            Game.Instance.GameEnd()
            
        if self.GameObject.grounded:
            self.GameObject.isDynamic = True
        else:
            self.GameObject.isDynamic = False
            
    def OnSpacePressed(self):
        if self.GameObject.grounded > 0:
            self.GameObject.velocity += (0, self.JumpVelocity)
            
            
    def FixedUpdate(self, deltatime):
        super().FixedUpdate(deltatime)
        self.RunningDistance = int(self.GameObject.position.X)