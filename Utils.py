from json import load
import math

from collections import abc
import numbers
import os

USE_PIL = True

#Althoug the program supports tkinter PhotoImage
#But it is still highly recommended to install the PIL library in order to have best experience. (Due to some image resize problem in tkinter)
try:
    USE_PIL = True
    import PIL.Image as Image
    from PIL.ImageTk import PhotoImage
except:
    USE_PIL = False
    from tkinter import PhotoImage
    
class Utils:
    """
    Provide some utility function for global general use.
    """
    
    @staticmethod
    def Contains(ls: list, target):
        for x in ls:
            if target is x:
                return True
        else:
            return False

    @staticmethod
    def IsType(obj, typeName):
        t = obj.__class__.__name__
        if t == typeName:
            return True
        else:
            return False
        
    @staticmethod
    def InsertString(str: str, index: int, insert: str):
        return str[:index] + insert + str[index:]
    
    @staticmethod
    def LoadImages(dir: str, files: list, width: int = -1, height: int = -1) -> dict:
        res = {}
        
        # paths = [os.path.join(dir, f) for f in files if os.path.exists(os.path.join(dir, f))]
        for file in files:
            path = os.path.join(dir, file)
            res[file[:-4]] = Utils.LoadImage(path, width, height)
        return res
        
    @staticmethod
    def LoadImage(path: str, width: int = -1, height: int = -1) -> PhotoImage:
        if USE_PIL:
            if width != -1 and height != -1:
                src = Image.open(path).resize((int(width), int(height)), resample=Image.LANCZOS)
            else:
                src = Image.open(path)
            image = PhotoImage(image=src)
            src.close()
            return image
        else:
            image = PhotoImage(file=path)
            h = image.height()
            w = image.width()
            
            relx = w/width
            rely = h/height
            #image = image.zoom(relx, rely)
            image = image.subsample(math.ceil(relx), math.ceil(rely))
            return image
        
class Debug:
    """
    Use to display some debug text on canvas,
    but you shouldn't see them now.
    """
    debugInfo: str = "None"
    
    @staticmethod
    def SetDebugInfo(info):
        Debug.debugInfo = info

class Vec2:
    """
    Vector 2D class, provide basic function for vector operations
    """

    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.X = x
        self.Y = y
        
    @staticmethod
    def FromStr(str):
        res = Vec2()
        xy = str.split(',')
        res.X = float(xy[0])
        res.Y = float(xy[1])
        return res
        
    def __str__(self) -> str:
        return f"{self.X},{self.Y}"

    def __add__(self, adder):
        sum: Vec2 = Vec2()
        if isinstance(adder, Vec2):
            sum = Vec2(self.X + adder.X, self.Y + adder.Y)
        elif isinstance(adder, abc.Iterable):
            sum = Vec2(self.X + adder[0], self.Y + adder[1])
        else:
            raise NotImplementedError
        return sum

    def __sub__(self, subtractor):
        diff: Vec2 = Vec2()
        if isinstance(subtractor, Vec2):
            diff = Vec2(self.X - subtractor.X, self.Y - subtractor.Y)
        elif isinstance(subtractor, abc.Iterable):
            diff = Vec2(self.X - subtractor[0], self.Y - subtractor[1])
        else:
            raise NotImplementedError
        return diff

    def __mul__(self, multiplier):
        product: Vec2 = Vec2()
        if isinstance(multiplier, numbers.Real):
            product = Vec2(self.X * multiplier, self.Y * multiplier)
        else:
            raise NotImplementedError
        return product

    def __div__(self, divider):
        quotient: Vec2 = Vec2()
        if isinstance(divider, numbers.Real):
            quotient = Vec2(self.X / divider, self.Y / divider)
        else:
            raise NotImplementedError
        return quotient

    def __eq__(self, compare):
        if Utils.IsType(compare, 'Vec2'):
            if self.X == compare.X and self.Y == compare.Y:
                return True
            else:
                return False
        else:
            return False

    def GetDistance(self, target):
        dif = self - target
        distance = math.sqrt(dif.X ** 2 + dif.Y ** 2)
        return distance

    def Abs(self):
        return Vec2(abs(self.X), abs(self.Y))

    def __or__(self, other):
        if type(other) == Vec2:
            return self.GetDistance(other)

    def ToAngle(self, arc=False):
        arcVal = math.atan(self.Y/self.X)
        return arcVal if arc == True else (arcVal/math.pi*180)
