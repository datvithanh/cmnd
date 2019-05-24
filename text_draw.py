from PIL import Image, ImageDraw, ImageFont, ImageOps
import random 
import os
from argparse import ArgumentParser
import cv2
import numpy as np

class TextDraw:
    def __init__(self, font_path, out_dir = 'data/train'):
        self.font_path = font_path
        self.out_dir = out_dir

    def text_font(self, image_height, text, scale):
        reduced_image_height = image_height // (scale+2)

        left, right = 1, 300
        mid = (left + right) // 2

        while right > left:
            mid = (left + right) // 2

            if ImageFont.truetype(self.font_path, mid).getsize(text)[1] > reduced_image_height:
                right -= 1
            else:
                if ImageFont.truetype(self.font_path, mid).getsize(text)[1] < reduced_image_height:
                    left += 1
                    if ImageFont.truetype(self.font_path, mid + 1).getsize(text)[1] > reduced_image_height:
                        return mid
                else:
                    return mid - 1

        return None

    def draw_text(self, image_path, text, output_file):
        #load bg ismg
        back_ground_img = Image.open(image_path)
        back_ground_size = back_ground_img.size

        #get font-size
        scale_coeff = random.randint(2,8)

        # print(text, scale_coeff)
        font_size = self.text_font(back_ground_size[1], text, scale_coeff)
        if font_size == None:
            return False
        font = ImageFont.truetype(self.font_path, font_size)
        text_size = font.getsize(text)

        #mean bg color
        img_arr = np.array(back_ground_img)
        average_color = [int(x) for x in np.mean(img_arr, axis=(0, 1))[:3]]
        min_channel = min(average_color) - 20
        average_color = [x - min_channel for x in average_color]

        #draw text
        text_img = Image.new('RGBA', (text_size[0], text_size[1] + 20), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_img)
        draw.text((0,13 + random.randint(-1,1)), text, font=font, fill=tuple(average_color))
        text_img = text_img.resize((int(text_img.size[0]*back_ground_size[1]/(text_img.size[1])), back_ground_size[1]))
        if random.randint(0,1) <= 0.2:
            text_img = text_img.rotate(random.uniform(-2,2))
            
        #cut bg image
        start = random.randint(0, max(1, back_ground_img.size[0] - text_img.size[0]))
        border = (start, 0, back_ground_img.size[0] - start - text_img.size[0], 0 ) # left, up, right, bottom
        back_ground_img = ImageOps.crop(back_ground_img, border)

        #draw text with bg
        result_img = Image.new('RGBA', back_ground_img.size, (0, 0, 0, 0))
        result_img.paste(back_ground_img, (0,0))
        result_img.paste(text_img, (0,0), mask=text_img)
        result_img.save(os.path.join(self.out_dir, output_file), format="png")
        return True

class DataGenerator:
    def __init__(self, samples = 5000, valid = False):
        self.samples = samples

        outdir = "data/train" if valid == False else "data/valid"

        self.cmnd_drawer = TextDraw("data/font/cmnd_text.ttf", out_dir = outdir)
        self.cmnd_id_drawer = TextDraw("data/font/cmnd_id.ttf", out_dir = outdir)
        self.cccd_drawer = TextDraw("data/font/cccd_text.ttf", out_dir = outdir)
        self.cmnd_old_drawer = TextDraw("data/font/cmnd_old_text.ttf", out_dir = outdir)

        self.cmnd_bg_path = 'data/crop/cmnd'
        self.cmnd_bg = [x for x in os.listdir(self.cmnd_bg_path) if x.endswith('.png')]

        self.cccd_bg_path = 'data/crop/cccd'
        self.cccd_bg = [x for x in os.listdir(self.cccd_bg_path) if x.endswith('.png')]

        self.cmnd_bg_valid_path = 'data/crop/valid_cmnd'
        self.cmnd_bg_valid = [x for x in os.listdir(self.cmnd_bg_valid_path) if x.endswith('.png')]

        self.cccd_bg_valid_path = 'data/crop/valid_cccd'
        self.cccd_bg_valid = [x for x in os.listdir(self.cccd_bg_valid_path) if x.endswith('.png')]

        self.valid = valid

        f = open('vnpernames.txt', 'r')
        self.names = [x.replace('\n', '') for x in f.readlines()]
        f = open('dates.txt', 'r')
        self.dates = [x for x in f.readlines()[0].replace('\n', '').split(',')]
        f = open('addresses.txt', 'r')
        self.addresses = [x for x in f.readlines()[0].replace('\n', '').split('|')]

        self.labelf = open(os.path.join(outdir, 'label.txt'), 'w+')

    def person_info(self):
        if self.valid == False:
            name = random.choice(self.names[:-len(self.names)//10])
            bday = random.choice(self.dates[:-len(self.dates)//10])
            addr1 = random.choice(self.addresses[:-len(self.addresses)//10])
            addr2 = random.choice(self.addresses[:-len(self.addresses)//10])
        else:
            name = random.choice(self.names[-len(self.names)//10:])
            bday = random.choice(self.dates[-len(self.dates)//10:])
            addr1 = random.choice(self.addresses[-len(self.addresses)//10:])
            addr2 = random.choice(self.addresses[-len(self.addresses)//10:])
        return name, bday, addr1, addr2

    def write_label(self, image_path, label):
        self.labelf.write(f"{image_path}\t{label}\n")

    def valid_word(self, word):
        # word = trim(word)
        pass

    def draw(self, drawer, sample_idx, te, ns, nq, hk):
        name, bday, addr1, addr2 = self.person_info()

        #draw te
        for idx, word in enumerate(name.split(' ')):
            if drawer.draw_text(te, word.upper(), f'{sample_idx}_te_{idx}.png'):
                self.write_label(f'{sample_idx}_te_{idx}.png', word.upper())

        #draw ns
        if drawer.draw_text(ns, bday, f'{sample_idx}_ns.png'):
            self.write_label(f'{sample_idx}_ns.png', bday)

        #draw nq
        for idx, word in enumerate(addr1.split(' ')):
            if drawer.draw_text(nq, word, f'{sample_idx}_nq_{idx}.png'):
                self.write_label(f'{sample_idx}_nq_{idx}.png', word)
        
        #draw hk
        for idx, word in enumerate(addr2.split(' ')):
            if drawer.draw_text(hk, word, f'{sample_idx}_hk_{idx}.png'):
                self.write_label(f'{sample_idx}_hk_{idx}.png', word)

    
    def cmnd_bg_info(self, bg_arr, bg_path):
        te, ns, nq, hk = random.choice([x for x in bg_arr if 'te' in x]), random.choice([x for x in bg_arr if 'ns' in x]), random.choice([x for x in bg_arr if 'nq' in x]), random.choice([x for x in bg_arr if 'hk' in x])
        te, ns, nq, hk = os.path.join(bg_path, te), os.path.join(bg_path, ns), os.path.join(bg_path, nq), os.path.join(bg_path, hk)

        return te, ns, nq, hk
    
    def cccd_bg_info(self, bg_arr, bg_path):
        te, ns, nq, hk = random.choice([x for x in bg_arr]), random.choice([x for x in bg_arr]), random.choice([x for x in bg_arr]), random.choice([x for x in bg_arr])
        te, ns, nq, hk = os.path.join(bg_path, te), os.path.join(bg_path, ns), os.path.join(bg_path, nq), os.path.join(bg_path, hk)

        return te, ns, nq, hk

    def gen_cmnd(self, sample_idx):
        if self.valid == False:
            te, ns, nq, hk = self.cmnd_bg_info(self.cmnd_bg, self.cmnd_bg_path)      
        else:
            te, ns, nq, hk = self.cmnd_bg_info(self.cmnd_bg_valid, self.cmnd_bg_valid_path)      

        if random.uniform(0,1) <= 0.3:
            drawer = self.cmnd_old_drawer
        else:
            drawer = self.cmnd_drawer
        
        self.draw(drawer, sample_idx, te, ns, nq, hk)

    def gen_cccd(self, sample_idx):
        if self.valid == False:
            te, ns, nq, hk = self.cccd_bg_info(self.cccd_bg, self.cccd_bg_path)      
        else:
            te, ns, nq, hk = self.cccd_bg_info(self.cccd_bg_valid, self.cccd_bg_valid_path)

        self.draw(self.cccd_drawer, sample_idx, te, ns, nq, hk)


    def generate(self):
        for i in range(self.samples):
            print(i, self.valid)

            if random.uniform(0,1) <= 0.3:
                self.gen_cccd(i)
            else:
                self.gen_cmnd(i)

def parse_arguments():
    parser = ArgumentParser()

    parser.add_argument('-t', '--train', type=int, default=1, help='Number of Train')
    parser.add_argument('-v', '--valid', type=int, default=1, help='Number of Test')

    return parser.parse_args()

if __name__ == "__main__":
    args_ = parse_arguments()

    train_gen = DataGenerator(samples = args_.train, valid = False)
    valid_gen = DataGenerator(samples = args_.valid, valid = True)
    train_gen.generate()
    valid_gen.generate()

    # text_drawer = TextDraw("data/font/arial.ttf", './')
    # text_drawer.draw_text('6.png', 'Nguyễn', 'results.png')


    # text_drawer = TextDraw("data/font/arial.ttf")
    # text_drawer.draw_text('6.png', 'Hưng', 'results.png')


    # text_drawer = TextDraw("data/font/palatino_linotype.ttf")

    # f = open('vnpernames.txt', 'r')
    # names = [x.replace('\n', '') for x in f.readlines()]

    # f = open('dates.txt', 'r')
    # dates = [x for x in f.readlines()[0].replace('\n', '').split(',')]

    # f = open('addresses.txt', 'r')
    # addresses = [x for x in f.readlines()[0].replace('\n', '').split('|')]

    # for i in range(1):
    #     name = random.choice(names)
    #     bday = random.choice(dates)
    #     addr1 = random.choice(addresses)
    #     addr2 = random.choice(addresses)

    #     print(i+1)
    #     print(name)
    #     print(bday)
    #     print(addr1)
    #     print(addr2)

    #     img_dir = 'data/crop/cmnd'
    #     imgs = os.listdir(img_dir)
    #     te = random.choice([x for x in imgs if 'te' in x])
    #     ns = random.choice([x for x in imgs if 'ns' in x])
    #     nq = random.choice([x for x in imgs if 'nq' in x])
    #     hk = random.choice([x for x in imgs if 'hk' in x])

    #     #draw te
    #     for idx, word in enumerate(name.split(' ')):
    #         text_drawer.draw_text(os.path.join(img_dir, te), word.upper(), f'{i+1}_te_{idx}.png')

    #     #draw ns
    #     text_drawer.draw_text(os.path.join(img_dir, ns), bday, f'{i+1}_ns.png')

    #     #draw nq
    #     for idx, word in enumerate(addr1.split(' ')):
    #         text_drawer.draw_text(os.path.join(img_dir, nq), word, f'{i+1}_nq_{idx}.png')
        
    #     #draw hk
    #     for idx, word in enumerate(addr2.split(' ')):
    #         text_drawer.draw_text(os.path.join(img_dir, hk), word, f'{i+1}_hk_{idx}.png')
