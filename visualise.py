import argparse
import csv
from PIL import Image, ImageDraw


Width = 600
Height = 600
GASPROPS = {
    "oxygen": {
        "color": "red",
        "radius": 4
    },
    "fuel": {
        "color": "blue",
        "radius": 4
    },
    "carbon_dioxide": {
        "color": "black",
        "radous": 4
    }
}

class FrameDrawer:
  def __init__(self, width, height, propsdict):
    self.img_width = width
    self.img_height = height
    self.shift_x = 0
    self.shift_y = 0
    self.props = propsdict
    
  def drawFrame(self, frameNo, rows):
    img = Image.new("RGB", (self.img_width, self.img_height), "white")
    d = ImageDraw.Draw(img)
    
    for row in rows:
        #print(row)
        type = row[0]
        x = float(row[1]) + self.shift_x
        y = float(row[2]) + self.shift_y
        color = self.props[type]["color"]
        radius = self.props[type]["radius"]
        
        d.ellipse((x - radius, y - radius, x + radius, y + radius), color)
        
    img.save("frame_" + str(frameNo) + ".png", "PNG")
    del img


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-if", type=str, dest="in_file", default="frames.csv")
    opts = parser.parse_args()
    
    in_file = open(opts.in_file, "rt")
    drawer = FrameDrawer(Width, Height, GASPROPS)
    
    secname = ""
    section = []
    
    for line in in_file:
        if line.startswith("!"):
            new_secname = line[1:]
            if secname == "":
                # Write first section.
                secname = new_secname
            elif new_secname != secname:
                # Begin new section.
                reader = csv.reader(section)
                print("Reading section " + secname)
                frame = drawer.drawFrame(int(secname), reader)
                secname = new_secname
                section = []
        else:
            section.append(line)
    
    # Finish off any remaining sections.
    reader = csv.reader(section)
    frame = drawer.drawFrame(int(secname), reader)
    
    in_file.close()

run()