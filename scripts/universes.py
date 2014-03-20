# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Functions that operate on package universes.
"""

import os, subprocess, gzip, codecs
import conf
from common import *

def run_debcheck(scenario,arch,outdir):

    """
    run dose-debcheck and store the resulting report
    """

    info('running debcheck for {s} on {a}'.format(a=arch,s=scenario))
    invocation = ['dose-debcheck', '--explain', '--failures', '--latest' ]
    for fg in conf.scenarios[scenario]['fgs']:
        invocation.append('--fg')
        invocation.append(
            fg.format(m=conf.locations['debmirror'],a=arch))
    for bg in conf.scenarios[scenario]['bgs']:
        invocation.append('--bg')
        invocation.append(
            bg.format(m=conf.locations['debmirror'],a=arch))

    outfile=open(outdir + "/debcheck.out", 'w')
    subprocess.call(invocation,stdout=outfile)
    outfile.close ()
                

def get_fg_packages(scenario,arch,outdir):

    """
    create a list of foreground packages
    """
    
    info('extracting foreground for {s} on {a}'.format(a=arch,s=scenario))
    packages=set()
    for fg in conf.scenarios[scenario]['fgs']:
        if fg[-3:]=='.gz':
            infile = codecs.getreader('utf-8')(gzip.open(
                    fg.format(m=conf.locations['debmirror'],a=arch),'r'))   
        else:
            infile = open(
                fg.format(m=conf.locations['debmirror'],a=arch))
        for line in infile:
            if line.startswith('Package:'):
                packages.add(line.split()[1])
        infile.close ()
                
    outfile = open(outdir + '/fg-packages', 'w')
    for f in packages: print(f,file=outfile)
    outfile.close ()

##########################################################################
# top level

def build(timestamp,scenario,architecture):
    outdir=cachedir(timestamp,scenario,architecture)
    if not os.path.isdir(outdir): os.makedirs(outdir)
    
    run_debcheck(scenario,architecture,outdir)
    get_fg_packages(scenario,architecture,outdir)
