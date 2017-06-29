#!/usr/bin/env python

###############################################################################
# iscegeo2geotiff
#
# Project:  APD_INSAR 
# Purpose:  Convert ISCE .geo files into geotiffs
#          
# Author:   Tom Logan, Jeremy Nicoll
#
###############################################################################
# Copyright (c) 2017, Alaska Satellite Facility
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
# 
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
###############################################################################
import sys
import os
import re
from lxml import etree
import numpy as np
from osgeo import gdal
from execute import execute


def convert_files():

    # Create the colorized browse jpeg
    cmd = "mdx.py filt_topophase.unw.geo -kml filt_topophase.unw.geo.kml"
    execute(cmd)

    cmd = "pngtopnm filt_topophase.unw.geo.png | ppmtojpeg > colorized.jpg"
    execute(cmd)

    # Create two geotiffs from the two banded image
    root = etree.parse("filt_topophase.unw.geo.xml")
    rt = root.getroot()
    for child in rt:
        if child.attrib['name'] == 'width':
            width_str = child[0].text
	    width = int(width_str)
            print "Image width %i" % width
        if child.attrib['name'] == 'length':
            length_str = child[0].text
	    length = int(length_str)
            print "Image length %i" % length

    fullAmp = np.zeros((length, width), dtype = np.float32)
    fullPhase = np.zeros((length, width), dtype = np.float32)
    with open('filt_topophase.unw.geo', 'rb') as fp:
        for i in range(length):
            fullAmp[i] = np.fromfile(fp, dtype = np.float32, count = width)
            fullPhase[i] = np.fromfile(fp, dtype = np.float32, count = width)

    os.chdir("..")
    execute("isce2gis.py envi -i merged/filt_topophase.unw.geo")
    os.chdir("merged")
    file = open("filt_topophase.unw.geo.hdr","r")
    for line in file:
        if re.search("coordinate",line):
	    save1 = line
        if re.search("map.info",line):
	    save2 = line
    file.close
    
    fullPhase.tofile("filt_topophase.unw.phase.bin");
    makeEnviHdr("filt_topophase.unw.phase.bin.hdr",width,length,save1,save2);
    gdal.Translate("phase.tif","filt_topophase.unw.phase.bin",creationOptions = ['COMPRESS=PACKBITS'])
    
    fullAmp.tofile("filt_topophase.unw.amp.bin");
    makeEnviHdr("filt_topophase.unw.amp.bin.hdr",width,length,save1,save2);
    gdal.Translate("amp.tif","filt_topophase.unw.amp.bin",creationOptions = ['COMPRESS=PACKBITS'])
    
    # Create the coherence image
    makeEnviHdr("phsig.cor.geo.hdr",width,length,save1,save2);
    gdal.Translate("coherence.tif","phsig.cor.geo",creationOptions = ['COMPRESS=PACKBITS'])


def makeEnviHdr(fileName,width,length,save1,save2):
    f = open(fileName,'w');
    f.write("ENVI");
    f.write("description = {Data product generated using ISCE}\n");
    f.write("samples = %i\n" % width);
    f.write("lines   = %i\n" %length);
    f.write("bands   = 1\n");
    f.write("header offset = 0\n");
    f.write("file type = ENVI Standard\n");
    f.write("data type = 4\n");
    f.write("interleave = bip\n");
    f.write("byte order = 0\n");
    f.write("%s\n" % save1);
    f.write("%s\n" % save2);

def main():
  convert_files()

if __name__ == "__main__":
  main()

    
    

