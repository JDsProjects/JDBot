from PIL import Image, ImageDraw
from io import BytesIO
import math, discord

def scale_img(img, w, h,totw="NULL",toth="NULL",offset=0):
    image1 =  Image.new("RGBA", (w, h), (0,0,0,0))
    drawer1 = ImageDraw.Draw(image1)
    img = img.convert("RGBA")
    _w = img.width
    _h = img.height

    for x in range(int(w)):
        UVX = x/w
        newx = math.floor(UVX*_w)
        for y in range(int(h)):
            UVY = y/h
            newy = math.floor(UVY*_h)
            drawer1.point((x,y),img.getpixel((newx, newy)))
    return image1

class aniRen:
    frames = []
    curframe =0
    timer = 0
    speed = 0
    max_t = 0
    def __init__(self,frame_list,spd,max_t):
        for obj in frame_list:
            self.frames.append(Image.open(obj))
        self.speed = spd
        self.max_t
    def advance(self):
        self.timer = self.timer + self.speed
        if self.timer>self.max_t:
            self.timer = self.timer-self.max_t
            self.curframe = self.curframe + 1
            if(self.curframe > len(self.frames)-1):
                self.curframe = 0
        return self.frames[self.curframe]

def overlay_image(img, img1):
    image = Image.new("RGBA", (img.width, img.height), (0,0,0,0))
    drawer = ImageDraw.Draw(image)
    offy=0
    if(img1.height != img.height):
        offy = 112-img1.height
    offx = int((112-img1.width)/2)
    for x in range(img.width):
        for y in range(img.height):
            drawer.point((x,y+(0.4*112)),img.getpixel((x,y)))
            try:
                if img.getpixel((x,y))[3] ==0:
                    if(y-offy>=0):
                       if(x-offx>=0):
                          drawer.point((x,y),img1.getpixel((x-offx,y-offy)))
            except:
              banana=1
            
    return image

def alpha_composite(img1, img2,offset):
    drawer = ImageDraw.Draw(img1)
    for x in range(img2.width):
        newx = x + offset[0]
        if(newx>=0) and (newx <img1.width):
            for y in range(img2.height):
                newy = y+offset[1]
                if(newy >=0 ) and (img1.height>newy):
                    color = img2.getpixel((x,y))
                    if color[3]!=0:
                        drawer.point((newx,newy),color)          

def new_paste(img,img1,):
  image =Image.new('RGBA', (img.width,img.height), (0,0,0,0))
  yoff=img.height - img1.height
  xoff =(img.width-img1.width)/2
  yoff = int(yoff)
  xoff =int(xoff)
  alpha_composite(image,img1, (xoff,yoff))
  yoff=yoff-img.height +  (img.height/1.5)
  alpha_composite(image,img,(0,yoff))
  return image

frames = []

framePath = ["utils/petpet_images/1.png","utils/petpet_images/2.png","utils/petpet_images/3.png","utils/petpet_images/4.png","utils/petpet_images/5.png"]
hand = aniRen(framePath,0.5,0.4)

def get_pet(image_bytes):
  tex = Image.open( BytesIO(image_bytes))
  #settings
  max_squ = 0.6
  min_squ = 0.4
  squ = min_squ
  squ_s = 0.09

  tot = int((max_squ-min_squ)/squ_s)*20
  for r1 in range(tot):
      squ = squ + squ_s
      if squ > max_squ:
          squ = max_squ
          squ_s = squ_s*-1
      if squ < min_squ:
          squ=min_squ
          squ_s=squ_s*-1
      squx =((max_squ-squ +min_squ)*0.5)+0.6
      under =scale_img(tex,int(squx*112),int(squ*112))
      frame = new_paste(hand.advance(), under)
      frames.append(frame)
  with BytesIO() as image_binary:
    frames[0].save(image_binary, 'GIF',disposal=2, transparency = -1,save_all=True, append_images=frames[1:(tot-1)], optimize=False, duration=16,loop=0)
    image_binary.seek(0)

    return discord.File(filename="out.gif",fp=image_binary)