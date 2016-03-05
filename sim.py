import numpy as np
import math

# Configuration variables.
particles = 100
width = 640
height = 480
delta_h = 100
start_angle = 0
end_angle = math.pi

def shapefunc(angle, vec):
    '''
    Defines shape on a pixel-by-pixel basis, i.e. for every coordinate supplied
    as an argument returns true (belongs to the shape) or false.
    '''
    
    if [A