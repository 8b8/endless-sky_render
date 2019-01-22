import tarfile
import requests
import json
import os
import cv2
import pathlib

"""
All paths are from my own (Linux) computer, to render automatically you need to adjust/change all of them
blender version 2.8 required, check 'builder.blender.org'
rendered_dir needs to match the img_name path in render.py
"""
user = ""

rendered_dir = "rendered/{}.png" #needs to match the directory in render.py
blender = "blender"
arg = "-b blends/{}.blend -P blends/render.py"
#arg = "blends/{}.blend -P blends/render.py"
ship_txt = "/home/{}/Downloads/ships.txt"
blend_dir = "blends/"


use_downsample = True


def ship_dict_get():
    render_info_ = requests.get("https://raw.githubusercontent.com/8b8/endless-sky_render/master/render_info.txt").content.decode()
    try:
        os.mkdir("blends/")
    except:
        print("blends directory already exists")
    
    with open("blends/render_info.txt",'w') as f:
        f.write(render_info_)
    if not "render.py" in os.listdir("blends/"):
        with open("blends/render.py","w") as f:
            f.write(requests.get("https://raw.githubusercontent.com/8b8/endless-sky_render/master/render.py").content.decode())
    ship_dict = {}
    for line in render_info_.split('\n'):
        if line.startswith('ship'):
            ship = line[6:][:]
            ship_dict.update({ship : {}})
        if line.find('sprite') > 0:
            ship_dict[ship].update({'sprite': line.split('\t')[-1]})
        if line.find('shape') > 0:
            ship_dict[ship].update({'shape': [int(x) for x in line.split('\t')[-1][1:-2].split(',')]})
    return ship_dict



def downsample(ship): #Downsample for increased sharpness
    if use_downsample:
        ship_img = cv2.imread(rendered_dir.format(ship), cv2.IMREAD_UNCHANGED)
        ship_img_half = cv2.resize(ship_img, None, fx = 0.5, fy=0.5,interpolation=cv2.INTER_LANCZOS4)
        cv2.imwrite(rendered_dir.format(ship),ship_img_half)






def check_files(ship_dict):
    all_files_present = True
    files = os.listdir()
    if not "blends" in files:
        all_files_present = False
    else:
        blends = os.listdir('blends/')
        for key, item in ship_dict.items():
            if not item['sprite']+'.blend' in blends:
                print(item['sprite']+'.blend'+" not found")
                all_files_present = False
    if not all_files_present:
        print("Files Mssing")
    return all_files_present


def download_files():
    blend_tar = requests.get("https://www.dropbox.com/s/9w4khx0p33ctjbd/blends.tar.xz?dl=1")
    with open("blend_tar.tar.xz","wb") as f:
        f.write(blend_tar.content)
    tar = tarfile.open("blend_tar.tar.xz")
    tar.extractall()


def main():
    ship_dict = ship_dict_get()
    if not check_files(ship_dict):
        print('redownload files')
        download_files()
    else:
        print('all files present')
    for ship, item in ship_dict.items():
        try:
            print(arg.format(item['sprite']))
            #if "bulk" in item['sprite']:
            os.system(blender+" "+arg.format(item['sprite'].replace(" ","\ ")))
            downsample(item['sprite'])
            #break
        except:
            print("FAILED ON {}".format(ship))
            break

if __name__ == "__main__":
    main()
