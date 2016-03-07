import argparse
import csv
from PIL import Image, ImageDraw


Width = 600
Height = 600
Padding = 50

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
  def __init__(self, width, height, propsdict, shift_x=0, shift_y=0, lim_width=0, lim_height=0):
    self.img_width = width
    self.img_height = height
    self.lim_width = lim_width if lim_width > 0 else width
    self.lim_height = lim_height if lim_height > 0 else height
    self.shift_x = shift_x
    self.shift_y = shift_y
    self.props = propsdict

  def drawFrame(self, frameNo, rows):
    img = Image.new("RGB", (self.img_width, self.img_height), "white")
    
    try:
        bg = Image.open("background.png")
    except:
        print("No background.png")
        bg = None
    
    d = ImageDraw.Draw(img)
    
    if bg:
        img.paste(bg)
    
    for row in rows:
        #print(row)
        type = row[0]
        x = float(row[1]) + self.shift_x
        y = float(row[2]) + self.shift_y
        
        color = self.props[type]["color"]
        radius = self.props[type]["radius"]
        
        c_x = float(row[1]) + radius
        c_y = float(row[2]) + radius
        
        if 0 <= c_x <= self.lim_width and 0 <= c_y <= self.lim_height:
            d.ellipse((x - radius, y - radius, x + radius, y + radius), color)
        
    

    
    img.save("frame_" + str(frameNo) + ".png", "PNG")
    del img


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-if", type=str, dest="in_file", default="frames.csv")
    opts = parser.parse_args()
    
    in_file = open(opts.in_file, "rt")
    drawer = FrameDrawer(Width + 2 * Padding, Height + 2 * Padding, GASPROPS,
        Padding, Padding, Width, Height)
    
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