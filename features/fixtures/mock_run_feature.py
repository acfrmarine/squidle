#! /usr/bin/env python
import glob
import os
import json
from extractors.extractor import extractor
from descriptors.testdesc import TestDesc
features = json.load(open(meta.json))
imgdir = '/scratch/partner464/catamihpc' 
savedir = '/scratch/partner464/catamihpc/output/' 
filelist = glob.glob(imgdir + '*.jpg')
os.chdir('/scratch/partner464/catamihpc')
for im in features.filelist:
    os.system("wget ' + im + ' ")
os.chdir(/home/catamihpc/bin/libfeature)
desc = TestDesc()
extractor(filelist, savedir, desc)