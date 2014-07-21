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
                

class Universe:
    """
    A universe object contains information about the packages that exist
    in a certain scenario and for a certain architecture. The list
    of foreground packages is written to a file.
    """

    def __init__(self,timestamp,scenario,architecture):
        info('extracting foreground for {s} on {a}'.format(
                a=architecture,s=scenario))

        self.fg_packages=set()
        self.source_packages=dict()

        for fg in conf.scenarios[scenario]['fgs']:
            fg_filename = fg.format(
                m=conf.locations['debmirror'],a=architecture)
            if not os.path.exists(fg_filename):
                warning('No such file: {p}, dropping from foregrounds'.format(
                        p=fg_filename,))
                continue
            elif fg[-3:]=='.gz':
                infile = codecs.getreader('utf-8')(gzip.open(fg_filename,'r'))
            else:
                infile = open(fg_filename)
            for line in infile:
                if line.startswith('Package:'):
                    current_package=line.split()[1]
                    self.fg_packages.add(current_package)
                if line.startswith('source:'):
                    current_source=line.split()[1]
                    self.source_packages[current_package]=current_source
            infile.close ()

        outdir=cachedir(timestamp,scenario,architecture)
        if not os.path.isdir(outdir): os.makedirs(outdir)
        outfile = open(outdir + '/fg-packages', 'w')
        for f in self.fg_packages: print(f,file=outfile)
        outfile.close ()
     
    def is_in_foreground(self,package):
        '''
        tell whether a package is in the foregounf
        '''
        return(package in self.fg_packages)

    def source(self,package):
        '''
        return the source package name pertaining to a binary package
        '''
        return self.source_packages.get(package,package)

##########################################################################
# top level

def build(timestamp,scenario,architecture):
    outdir=cachedir(timestamp,scenario,architecture)
    if not os.path.isdir(outdir): os.makedirs(outdir)
    run_debcheck(scenario,architecture,outdir)
