#!/usr/bin/python
#
# scale-for-frame is the main module, reading .jpg files from source directories named "_xxx" and
# writes them as scaled .jpg images to target directories named "xxx"
#
# M. Mueller-Westerholt, magit@mueller-westerholt.de
#
import warnings
from os import listdir, path
from os.path import join, isdir, isfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

# workdir="C:/Uoers/Marcus/Documents/Photoframe"
workDir = '/home/marcus/git/photoframescale/images'
targetSize = 1024, 600
fontName = 'LHANDW.TTF'
initialFontSize = 32
textBorder = (50, 50)
textColorBright = (240, 240, 240)
textColorDark = (16, 16, 16)

def buildTargetDirName(topicdirname):
    "Create a target directory file name from a topic directory file name, i.e. create xxx from _xxx"
    if topicdirname.startswith("_"):
        return topicdirname[1:]
    return "__" + topicdirname

def getFontAtSize(fontsPath, fontName, initialFontSize, textToPrint, targetWidth):
    "Get the font at the right size so the text width won't exceed the targetWidth"
    fontSize = initialFontSize
    while True:
        font = ImageFont.truetype(path.join(fontsPath, fontName), fontSize)
        textWidth = font.getsize(textToPrint)[0]
        if textWidth <= targetWidth:
            break
        if fontSize < 9:
            break
        fontSize = fontSize - 1
    return font

def getMatchingTextColor(im, pos, size):
    "Get a bright or a dark color combination so the text will best stand out from the image"
    partArea = (pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
    partImage = im.crop(partArea).convert('L')
    stat = ImageStat.Stat(partImage)
    meanBrightness = stat.mean[0]
    if meanBrightness < 128:
        return textColorBright
    else:
        return textColorDark

def addCaptionToImage(im, captionText):
    "Add a caption to the lower right corner of the image. Font size is decremented until the text fits into half the image width"
    draw = ImageDraw.Draw(im)
    currentDir = path.dirname(__file__)
    fontsPath = path.join(currentDir, 'fonts')
    imageSize = im.size
    imageWidth = imageSize[0]
    captionFont = getFontAtSize(fontsPath, fontName, initialFontSize, captionText, imageWidth / 2)
    textSize = captionFont.getsize(captionText)
    textStartPos = imageSize[0] - textSize[0] - textBorder[0], imageSize[1] - textSize[1] - textBorder[1]
    textColor = getMatchingTextColor(im, textStartPos, textSize)
    draw.text(textStartPos, captiontext, textColor, font=captionFont)
    return im

def convertTopicDir(fulltopicdir, fulltargetdir, captiontext):
    "Convert a directory full of .jpg / .jpeg files to scaled size"
    warnings.simplefilter('error', Image.DecompressionBombWarning)
    topicfiles = [f for f in listdir(fulltopicdir) if isfile(join(fulltopicdir, f)) \
                  and (f.lower().endswith(".jpg") or f.lower().endswith(".jpeg"))]
    for topicfile in topicfiles:
        fulltopicfile = join(fulltopicdir, topicfile)
        fulltargetfile = join(fulltargetdir, topicfile)
        print("Converting", topicfile)
        try:
            im = Image.open(fulltopicfile)
            im.thumbnail(targetSize, Image.ANTIALIAS)
            im = addCaptionToImage(im, captiontext)
            im.save(fulltargetfile, "JPEG")
        except IOError:
            print("cannot create target for '%s'" % fulltopicfile)

# --- main ---
topicdirs = [f for f in listdir(workDir) if isdir(join(workDir, f)) and f.startswith("_")]

print("Topic dirs are", topicdirs)

for topicdir in topicdirs:
    targetdir = buildTargetDirName(topicdir)
    captiontext = targetdir # change this if the caption should be different from the dir name
    print("Convert and transfer from", topicdir, "to", targetdir)
    fulltopicdir = join(workDir, topicdir)
    fulltargetdir = join(workDir, targetdir)
    Path(fulltargetdir).mkdir(exist_ok=True)
    convertTopicDir(fulltopicdir, fulltargetdir, captiontext)