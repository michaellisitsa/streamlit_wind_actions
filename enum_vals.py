"""
Enums are names bound to unique, constant values.
Unlike a list, enums are immutable, so the programmer gets warned 
that they can't do illegal actions such as editing the value, or incorrect capitalisation
"""

import enum

class Regions(enum.Enum):
    A1 = enum.auto()
    A2 = enum.auto()
    A3 = enum.auto()
    A4 = enum.auto()
    A5 = enum.auto()
    A6 = enum.auto()
    A7 = enum.auto()
    B = enum.auto()
    C = enum.auto()
    D = enum.auto()
    W = enum.auto()

class Cases(enum.Enum):
    ULS = enum.auto()
    SLS = enum.auto()
    FAT = enum.auto()

class Directions(enum.Enum):
    ANY = enum.auto()
    N = enum.auto()
    NE = enum.auto()
    E = enum.auto()
    SE = enum.auto()
    S = enum.auto()
    SW = enum.auto()
    W = enum.auto()
    NW = enum.auto()

class Significance(enum.Enum):
    MAJOR = enum.auto()
    MINOR = enum.auto()

class Wind_angle(enum.Enum):
    NORMAL = enum.auto()
    ANGLE_45 = enum.auto()
    PARALLEL = enum.auto