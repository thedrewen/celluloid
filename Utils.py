import random, math
import pygame as pg
from pygame import gfxdraw

class Color:
    RED = (200,0,0)
    REDOPAQUE = pg.Color(200,0,0, 100)
    WHITEOPAQUE = pg.Color(255,255,255, 100)
    GREEN = (34,139,34)
    WHITE = (255,255,255)
    BLACK = (0, 0, 0)
    BLACKGREY = (35,35,35)
    BLACKGREYUP = (30,30,30)

    def random():
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    def addOneToColor(color):

        r, g, b = color
        addColor = 50
        if r > 250 - addColor:
            r -= addColor
        else:
            r += addColor
        if g >= 250 - addColor:
            g -= addColor
        else:
            g += addColor
        if b >= 250 - addColor:
            b -= addColor
        else:
            b += addColor

        return (r, g, b)
    
def draw_circle(surface, x, y, radius, color):
    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.filled_circle(surface, x, y, radius, color)

def taille_cote_carrer_inscrit(radius):
    diameter = 2 * radius
    side_length = diameter / math.sqrt(2)
    return side_length
