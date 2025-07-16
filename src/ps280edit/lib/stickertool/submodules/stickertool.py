# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
import os,sys, yaml
print(os.getcwd())
print(sys.path)
import segno
from PIL import ImageFont, ImageDraw, Image, ImageOps
import textwrap as tr
from IPython.display import Image as dispImg




class Sticker:
    
    def get_text_size(self, text, image, font, xoffset= 0, yoffset= 0):
        im = Image.new('RGB', (image.width-xoffset, image.height-yoffset))
        draw = ImageDraw.Draw(im)
        _, _, tw, th = draw.textbbox((0, 0), text, font)
        return(tw,th)

    def find_font_size(self, text, font, image, target_width_ratio, xoffset= 0, yoffset= 0):
        tested_font_size = 100
        tested_font = ImageFont.truetype(font, tested_font_size)
        observed_width, observed_height = self.get_text_size(text, image, tested_font, yoffset)
        estimated_font_width = tested_font_size *(image.width- xoffset) * target_width_ratio/ observed_width
        estimated_font_heigth =  tested_font_size / 1.15 *(image.height- yoffset* 1.34) * target_width_ratio/ observed_height 
        return round(min(estimated_font_heigth, estimated_font_width)/1.5+10)


    def wrap(self, text,width):
        wrapper = tr.TextWrapper(width= width)
        word_list = wrapper.wrap(text=text)
        linelength=max([len(l) for l in word_list])
        lines=len(word_list)
        return('\n'.join(word_list).strip(' ').replace('  ',' '))

    def draw_text(self, image,text, ratio= 1, xoffset= 0, yoffset= 0, font_family='Arial.ttf',linelength=35):
        text = self.wrap(text, linelength)
        editable_image = ImageDraw.Draw(image)
        iw, ih = editable_image.im.size
        font_size = self.find_font_size(text, font_family, image, ratio, xoffset, round(yoffset/1.27))
        font = ImageFont.truetype(font_family, font_size)
        _, _, tw, th = editable_image.textbbox((0, 0), text, font= font)

        editable_image.text(((iw-tw)/2+xoffset ,yoffset),text, fill="black", font=font, align= 'center',spacing=10)
        return(True)


    
    def __init__(self, configfile='',
                       mailaddress= '',
                       mailsubject= '',
                       mailbody= '',
                       infotext= '',
                       supporttext= '',
                       serial= '',
                       sensorid= '',
                       size= 38.5,
                       dpi= 300,
                       output_path='sticker',
                       image_template='sticker'):
                 
        self.mailaddress = mailaddress
        self.mailsubject = mailsubject
        self.mailbody = mailbody
        self.infotext = infotext
        self.supporttext = supporttext
        self.serial = serial
        self.sensorid = sensorid
        self.size = size
        self.dpi = dpi
        self.output_path = output_path
        self.configfile = configfile
        self.image_template = image_template
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)
                 
    def read_configuration(self, configfile=''):
        if not configfile:
             configfile = self.configfile
        with open(configfile, 'r') as f:
            configuration = yaml.safe_load(f)
        self.__dict__.update(configuration)
        #for k,v in configuration.items():
        #    eval(f"self.{k}") = v
        return(self.__dict__)
                

    def create_qr_code(self, size= 0, dpi= 0,show= True):

        if not size:
            size = self.size
        else:  
            self.size = size
            
        if not dpi:
            dpi = self.dpi
        else:
            self.dpi = dpi
            
        mailsubject= self.mailsubject.replace('<<sensorid>>',self.sensorid).replace('<<serial>>',self.serial).replace(' ','%20')
        mailbody= self.mailbody.replace('<<sensorid>>',self.sensorid).replace('<<serial>>',self.serial).replace(' ','%20')
        qrcode = segno.make_qr(f"mailto:{self.mailaddress}?subject={mailsubject}&body={mailbody}".encode('utf8'),)
        qrcode.save(os.path.join(self.output_path,'qr_temp.png'), scale=5 , dpi=dpi, border=15) #size/7.7
        width_ratio = 0.9  # Portion of the image the text width should be (between 0 and 1)
        font_family = "Arial.ttf"
        text = f"Serial: {self.serial}"
        image = Image.open(os.path.join(self.output_path,'qr_temp.png'))
        editable_image = ImageDraw.Draw(image)
        iw, ih = editable_image.im.size
        font_size = self.find_font_size(text, font_family, image, width_ratio)
        font = ImageFont.truetype(font_family, round(font_size*0.85))
        _, _, tw, th = editable_image.textbbox((0, 0), text, font= font)
        editable_image.text(((iw-tw)/2 , ih-2.3*th), text, font=font, align= 'center')

        resolution= round(image.info['dpi'][0])
        pixel_per_mm= resolution/25.4
        width, height = image.size
        new_width= pixel_per_mm * size
        factor= new_width/width*dpi/resolution    
        image= image.resize((round(width*factor),round(height*factor)))
        image= ImageOps.expand(image, border=(1, 1, 1, 20), fill='white')
        image= ImageOps.expand(image, border=(1, 1, 1, 1), fill='black')
        image.save(os.path.join(self.output_path, f"{self.serial}_qrcode.png"), dpi=(dpi, dpi))
        if show:
            image.show()
        os.remove(os.path.join(self.output_path,'qr_temp.png'))
        return(os.path.join(self.output_path, f"{self.serial}_qrcode.png"))
    
    @property 
    def qr_code_file(self):
        return(os.path.join(self.output_path, f"{self.serial}_qrcode.png"))
    
    
    def create_sticker(self, size= 0, dpi= 0, show= True):

        if not size:
            size = self.size
        else:  
            self.size = size
            
        if not dpi:
            dpi = self.dpi
        else:
            self.dpi = dpi
            
        image = Image.open(self.image_template)

        infotext= self.infotext.replace('<<mailto>>',self.mailaddress).replace('<<serial>>',self.serial).replace('<<sensorid>>',self.sensorid)
        self.draw_text(image,infotext, 0.8, 0, 100, linelength=35)
        supporttext= self.supporttext.replace('<<mailto>>',self.mailaddress).replace('<<serial>>',self.serial).replace('<<sensorid>>',self.sensorid)
        self.draw_text(image,supporttext, 0.8, 0, 295, linelength=40)
        self.draw_text(image,f"[{self.sensorid}]", 0.8, 0, 420, linelength=45)
        self.draw_text(image,f"Serial: {self.serial}", 0.8, -120, 530, linelength=45)
        resolution= round(image.info['dpi'][0])
        pixel_per_mm= resolution/25.4
        width, height = image.size
        new_width= pixel_per_mm * size
        factor= new_width/width * dpi/resolution    
        image= image.resize((round(width*factor),round(height*factor)))
        image= ImageOps.expand(image, border=(1, 1, 1, 1), fill='black')
        image.save(os.path.join(self.output_path,f"{self.serial}_sticker.png"), dpi= (dpi,dpi))
        if show:
            image.show()
        return(os.path.join(self.output_path,f"{self.serial}_sticker.png"))
    
    
    @property 
    def image_file(self):
        return(os.path.join(self.output_path, f"{self.serial}_sticker.png"))
# -


