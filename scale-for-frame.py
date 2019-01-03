#!/usr/bin/python
#
# scale-for-frame is the main module, reading .jpg files from source directories named "_xxx" and
# writes them as scaled .jpg images to target directories named "xxx"
#
# M. Mueller-Westerholt, ma2018@mueller-westerholt.de
#

from PIL import Image
from os import listdir
from os.path import join, isdir, isfile
from pathlib import Path
from shutil import copystat

workdir="C:/Users/Marcus/Documents/Photoframe"
targetsize = 1024, 600

def buildTargetDirName(topicdirname):
    "Create a target directory file name from a topic directory file name, i.e. create xxx from _xxx"
    if topicdirname.startswith("_"):
        return topicdirname[1:]
    return "__" + topicdirname

def convertTopicDir(fulltopicdir, fulltargetdir):
    "Convert a directory full of .jpg / .jpeg files to scaled size"
    topicfiles = [f for f in listdir(fulltopicdir) if isfile(join(fulltopicdir, f)) \
                  and (f.lower().endswith(".jpg") or f.lower().endswith(".jpeg"))]
    for topicfile in topicfiles:
        fulltopicfile = join(fulltopicdir, topicfile)
        fulltargetfile = join(fulltargetdir, topicfile)
        print("Converting", topicfile)
        try:
            im = Image.open(fulltopicfile)
            im.thumbnail(targetsize, Image.ANTIALIAS)
            im.save(fulltargetfile, "JPEG")
        except IOError:
            print("cannot create target for '%s'" % fulltopicfile)

# --- main ---
topicdirs = [f for f in listdir(workdir) if isdir(join(workdir, f)) and f.startswith("_")]

print("Topic dirs are", topicdirs)

for topicdir in topicdirs:
    targetdir = buildTargetDirName(topicdir)
    print("Convert and transfer from", topicdir, "to", targetdir)
    fulltopicdir = join(workdir, topicdir)
    fulltargetdir = join(workdir, targetdir)
    Path(fulltargetdir).mkdir(exist_ok=True)
    convertTopicDir(fulltopicdir, fulltargetdir)