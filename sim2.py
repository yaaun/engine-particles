import math
import random
import argparse
import csv

GASPROPS = {
    "oxygen": {
        "radius": 4,    #[px]
        "mass": 32,
        "color": "red"
    },
    
    "fuel": {
        "radius": 4,
        "mass": 100,
        "color": "#07f"
    },
    
    "carbon_dioxide": {
        "radius": 4,
        "mass": 44,
        "color": "black"
    }
}


# About units used in this simulation
#
#
# ** LENGTH **
# Lengths are expressed in pixels [px].
#
# ** VELOCITY **
# Velocity is expressed in pixels per millisecond [px/ms]. The assumption is
# that there are 1000 frames per second.
#
# ** MASS **
# Masses are defined strictly relative to each other, and do not correspond
# to any real-world unit.


# Conventions relating to coordinate systems and their entities
#
# ** COORDINATE AXES **
# The X coordinates run horizontally to the screen, growing from left to right.
# The Y coordinates run vertically to the screen, growing from top to bottom.
#
# ** ANGLES **
# Angles are described using numbers from -PI to PI. A vector with an angle of 0
# is parallel to the X axis, and is directed towards positive X.



# Configuration variables.
Width = 600
Height = 600
WidthDivision = 10
HeightDivision = 10
OxygenParticles = 200
FuelParticles = 100
CarbonDioxideParticles = 0

FastSpeed = 5
SlowSpeed = 0.5
Frames = 300

StartAngle1 = 1/2 * math.pi
StartAngle1Delta = 1/2 * math.pi


def dist(m1, m2):
    return math.sqrt((m2.x - m1.x)**2 +
        (m2.y - m1.y)**2)

def calcSpeed(energy, mass):
    return math.sqrt(2 * energy / mass)

def randPosition(min_x, min_y, max_x, max_y):
    return (random.randint(min_x, max_x), random.randint(min_y, max_y))
    
def randVelocity(max):
    return (random.random() * max, random.random() * max)

def makeVec(angle, magnitude):
    x = math.cos(angle) * magnitude
    y = math.sin(angle) * magnitude
    
    return (x, y)


class Gas:
  def __init__(self, name):
    self.radius = GASPROPS[name]["radius"]
    self.mass = GASPROPS[name]["mass"]
    self.color = GASPROPS[name]["color"]


class Molecule:
  lastID = 0
  
  def __init__(self, type, id=0):
    self.type = type
    self.x = 0
    self.y = 0
    self.vx = 0
    self.vy = 0
    self.id = id
  
  def move(self, time):
    self.x += self.vx * time
    self.y += self.vy * time
  
  def setPosition(self, x, y):
    self.x = x
    self.y = y
  
  def setVelocity(self, vx, vy):
    self.vx = vx
    self.vy = vy
  
  @property
  def mass(self):
    return GASPROPS[self.type]["mass"]
 
  @property
  def radius(self):
    return GASPROPS[self.type]["radius"]
  
  @classmethod
  def nextID(cls):
    rv = cls.lastID
    cls.lastID += 1
    return rv


class Volume:
  """
  An object that describes a space relative to which molecules are
  positioned.
      
  The following duties are delegated to this class:
    * interface for storing and retrieving molecules
    * finding molecules within a given search radius
    * defining bounds and detecting related collisions
  
  This class stores (internally) only one instance of a molecule, to avoid
  excessive waste.
  """
  
  def __init__(self, width, height, w_div, h_div):
    self.width = width
    self.height = height
    self._mols = {}
    self._spatial = {}
    self._cell_width = self.width // w_div
    self._cell_height = self.height // h_div
    
    # Initialize the spatial.
    for i in range(-1, h_div + 1):
      for j in range(-1, w_div + 1):
        self._spatial[(j, i)] = []

  def _sort(self):
    # for k in self._spatial.keys():
    #     self._spatial[k] = []
    # 
    # for mol in self._mols.values():
    #   cell_x = mol.x // self._cell_width
    #   cell_y = mol.y // self._cell_height
    #   
    #   self._spatial[(cell_x, cell_y)].append(mol)
    pass
  
  def __iter__(self):
    return iter(self._list)
    
  def setList(self, lst):
    self._mols = lst
    self._sort()

  def wallCollision(self, mol):
    """ 
    Detects whether the given particle collides with a wall (walls). Returns
    the angle of the normal vector of the surface that the molecule has collided
    with. The vector is directed **from** the solid bulk of the barrier.
    
    E.g. a collision with the top wall of a square would yield (3/2)*PI.
    A collision with the bottom and left walls of the square would yield PI/4.
        
    Note: index is a number that refers to the list index of the molecule
      that is being tested for wall collisions.
    """
    
    #mol = self._mols[id]
    angle = None
    
    if  mol.x - mol.radius < 0 and mol.y - mol.radius < 0:
        # Upper left corner.
        angle = 1/4 * math.pi
    elif mol.x + mol.radius > self.width and mol.y - mol.radius < 0:
        # Upper right corner.
        angle = 3/4 * math.pi
    elif mol.x - mol.radius < 0 and mol.y + mol.radius > self.height:
        # Lower left corner.
        angle = -1/4 * math.pi
    elif mol.x + mol.radius > self.width and mol.y + mol.radius > self.height:
        angle = -3/4 * math.pi
    elif mol.x - mol.radius < 0:
        # Left wall.
        angle = 0
    elif mol.y - mol.radius < 0:
        # Top wall.
        angle = 1/2 * math.pi
    elif mol.x + mol.radius > self.width:
        # Right wall.
        angle = math.pi
    elif mol.y + mol.radius > self.height:
        # Bottom wall.
        angle = -1/2 * math.pi

    return angle
    
  def findInRadius(self, id, radius):
    """
    Attempts to find all molecules that are located near the supplied molecule
    within the search radius.
    
    Note: the index argument is an index, and the return value is a list of
      molecule indexes.
    """
    return [] # for now
    

class Model:
  def __init__(self, o2, fuel, co2):
    self.o2 = o2
    self.fuel = fuel
    self.co2 = co2
    self.frame = 0
    # If self.frame is a multiple of this value, a snapshot will be made.
    self.keyframe_frames = 5
    self.mols = {}
    self.volume = Volume(Width, Height, WidthDivision, HeightDivision)
    self.id_counter = 0
    
    for i in range(self.o2):
        mol = Molecule("oxygen", self.id_counter)
        mol.setPosition(self.volume.width / 2, mol.radius * 2)
        angle = StartAngle1 + StartAngle1Delta * (i / self.o2) * 2
        mol.setVelocity(*makeVec(angle, SlowSpeed))
        
        self.mols[self.id_counter] = mol
        self.id_counter += 1
    
    for i in range(self.fuel):
        mol = Molecule("fuel", self.id_counter)
        # mol.setPosition(5 + random.randint(0, self.volume.width - 10),
        #    5 + random.randint(0, self.volume.height - 10))
        # mol.setVelocity(random.randint(-5, 5), random.randint(-5, 5))
        mol.setPosition(self.volume.width / 2, mol.radius * 2)
        angle = StartAngle1 + StartAngle1Delta * (i / self.fuel) * 2
        mol.setVelocity(*makeVec(angle, FastSpeed))
        
        
        self.mols[self.id_counter] = mol
        self.id_counter += 1
    

  def run(self):
    keyframe = False
    newmols = {}
    
    self.volume.setList(self.mols)
    
    # The integration step.
    for id, mol in self.mols.items():
        # Check if there are no collisions.
        wallAngle = self.volume.wallCollision(mol)
        # collide = self.volume.findInRadius(id, mol.radius * 2)
        #if mol.type == "fuel":
        #    print("wallAngle is " + str(wallAngle))
        
        if wallAngle != None:
            vec_angle = math.atan2(mol.vy, mol.vx)
            magnitude = math.hypot(mol.vx, mol.vy)
            
            rel_angle = vec_angle - wallAngle
            
            #if mol.type == "fuel":
            #    print("vx = {}, vy = {}".format(mol.vx, mol.vy))
            #    print("vec_angle = {}, rel_angle = {}".format(vec_angle, rel_angle))
            
            
            if  rel_angle <= -1/2 * math.pi or rel_angle >= 1/2 * math.pi:
                # Collision took place.
                #print("Collision event at angle " + str(rel_angle))
                new_angle = math.pi - rel_angle
                new_angle += wallAngle
                
                new_vx, new_vy = makeVec(new_angle, magnitude)
            else:
                new_vx = mol.vx
                new_vy = mol.vy

            
        # elif collide != None:
        #    new_v
        else:
            new_vx = mol.vx
            new_vy = mol.vy
        
        new_x = mol.x + new_vx
        new_y = mol.y + new_vy
        
        newmol = Molecule(mol.type, id)
        newmol.setPosition(new_x, new_y)
        newmol.setVelocity(new_vx, new_vy)
        newmols[id] = newmol

    self.mols = newmols

    if self.frame % self.keyframe_frames == 0:
        # Make key frame.
        keyframe = newmols
        
        
    self.frame += 1
    return keyframe


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o2", dest="o2", type=int, default=OxygenParticles)
    parser.add_argument("-fuel", dest="fuel", type=int, default=FuelParticles)
    parser.add_argument("-f", dest="frames", type=int, default=Frames) # number of frames to execute
    opts = parser.parse_args()
    
    file = open("frames.csv", "w", newline="")
    
    
    model = Model(opts.o2, opts.fuel, 0)
    w = csv.writer(file)
    
    for i in range(opts.frames):
        snap = model.run()
        
        if snap:
            file.write("!" + str(i) + "\r\n")
            
            for v in snap.values():
                w.writerow((v.type, v.x, v.y, v.vx, v.vy))


    file.close()

run()

