#!/usr/bin/python
#
# scale-for-frame is the main module, reading .jpg files from source directories named "_xxx" and
# writes them as scaled .jpg images to target directories named "xxx"
#
# M. Mueller-Westerholt, magit@mueller-westerholt.de
#
import warnings
from os import listdir, path
from os.path import join, isdir, isfile, getmtime
from pathlib import Path
from argparse import ArgumentParser

from PIL import Image, ImageDraw, ImageFont, ImageStat
from PIL.ExifTags import TAGS

defaultWorkDir = "C:/Users/Marcus/Documents/Photoframe"
# workDir = '/home/marcus/git/photoframescale/images'
targetSize = 1024, 600
fontName = 'segoeprb.ttf'
initialFontSize = 32
textBorder = (50, 50)
textColorBright = (240, 240, 240)
textColorDark = (16, 16, 16)


def build_target_dir_name(topicdirname):
    """Create a target directory file name from a topic directory file name, i.e. create xxx from _xxx"""
    if topicdirname.startswith("_"):
        return topicdirname[1:]
    return "__" + topicdirname


def get_font_at_size(fonts_path, font_name, initial_font_size, text_to_print, target_width):
    """Get the font at the right size so the text width won't exceed the targetWidth"""
    font_size = initial_font_size
    while True:
        font = ImageFont.truetype(path.join(fonts_path, font_name), font_size)
        text_width = font.getsize(text_to_print)[0]
        if text_width <= target_width:
            break
        if font_size < 9:
            break
        font_size = font_size - 1
    return font


def get_matching_text_color(im, pos, size):
    """Get a bright or a dark color combination so the text will best stand out from the image"""
    part_area = (pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
    part_image = im.crop(part_area).convert('L')
    stat = ImageStat.Stat(part_image)
    mean_brightness = stat.mean[0]
    if mean_brightness < 128:
        return textColorBright
    else:
        return textColorDark


def add_caption_to_image(im, caption_text):
    """Add a caption to the lower right corner of the image. " \
        "Font size is decremented until the text fits into half the image width"""
    draw = ImageDraw.Draw(im)
    current_dir = path.dirname(__file__)
    fonts_path = path.join(current_dir, 'fonts')
    image_size = im.size
    image_width = image_size[0]
    caption_font = get_font_at_size(fonts_path, fontName, initialFontSize, caption_text, image_width / 2)
    text_size = caption_font.getsize(caption_text)
    text_start_pos = image_size[0] - text_size[0] - textBorder[0], image_size[1] - text_size[1] - textBorder[1]
    text_color = get_matching_text_color(im, text_start_pos, text_size)
    draw.text(text_start_pos, caption_text, text_color, font=caption_font)
    return im


def apply_image_rotation_by_exif(image, exif_orientation):
    """Rotate image according to exif orientation information"""
    if exif_orientation == 3:
        result_image = image.rotate(180, expand=True)
    elif exif_orientation == 6:
        result_image = image.rotate(270, expand=True)
    elif exif_orientation == 8:
        result_image = image.rotate(90, expand=True)
    else:
        result_image = image
    return result_image


def exists_and_newer(targetfile, topicfile):
    """Check if targetfile exists and if exists, if it's newer or same timestamp than topicfile"""
    try:
        if getmtime(targetfile) >= getmtime(topicfile):
            return True
        else:
            return False
    except IOError:
        return False


def convert_topic_dir(full_topic_dir, full_target_dir, photo_topic):
    """Convert a directory full of .jpg / .jpeg files to scaled size, adding photo captions"""
    warnings.simplefilter('error', Image.DecompressionBombWarning)
    topicfiles = [f for f in listdir(full_topic_dir) if isfile(join(full_topic_dir, f))
                  and (f.lower().endswith(".jpg") or f.lower().endswith(".jpeg"))]
    for topicfile in topicfiles:
        fulltopicfile = join(full_topic_dir, topicfile)
        fulltargetfile = join(full_target_dir, topicfile)
        if not exists_and_newer(fulltargetfile, fulltopicfile):
            print("  Converting", topicfile, ": ", end='')
            try:
                im = Image.open(fulltopicfile)

                if im._getexif() is not None:
                    exif = {
                        TAGS[k]: v
                        for k, v in im._getexif().items()
                        if k in TAGS
                    }
                else:
                    exif = dict()

                if 'Orientation' in exif:
                    im = apply_image_rotation_by_exif(im, exif['Orientation'])

                if 'ImageDescription' in exif:
                    photo_description = exif['ImageDescription']
                    if photo_description.rstrip() == '':
                        photo_caption = photo_topic
                    else:
                        if photo_description.endswith('#'):
                            photo_caption = photo_description.rstrip('#')
                        else:
                            photo_caption = photo_topic + " - " + photo_description
                else:
                    photo_caption = photo_topic

                print(photo_caption)
                im.thumbnail(targetSize, Image.ANTIALIAS)
                im = add_caption_to_image(im, photo_caption)
                im.save(fulltargetfile, "JPEG")
            except IOError:
                print("cannot create target for '%s'" % fulltopicfile)
            except AttributeError:
                print("Attribute error for '%s'" % fulltopicfile)
        else:
            print("  Skipping", topicfile)


# --- main ---
parser = ArgumentParser(description='Convert jpg images for a photo frame, scaling, rotating, and adding titles')
parser.add_argument("-w", "--workdir", type=str, dest="workDir",
                    help="define working directory", default=defaultWorkDir)
args = parser.parse_args()
workDir = args.workDir
topicDirs = [f for f in listdir(workDir) if isdir(join(workDir, f)) and f.startswith("_")]
print("Topic dirs are", topicDirs)

for topicdir in topicDirs:
    targetdir = build_target_dir_name(topicdir)
    phototopic = targetdir  # change this if the caption should be different from the dir name
    print("Convert and transfer from", topicdir, "to", targetdir)
    fulltopicdir = join(workDir, topicdir)
    fulltargetdir = join(workDir, targetdir)
    Path(fulltargetdir).mkdir(exist_ok=True)
    convert_topic_dir(fulltopicdir, fulltargetdir, phototopic)
