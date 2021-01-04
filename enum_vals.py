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