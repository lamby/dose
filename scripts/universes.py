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

    scenario_name = scenario['name']
    info('running debcheck for {s} on {a}'.format(a=arch,s=scenario_name))
    if (scenario['type'] == 'binary'):
        invocation = ['dose-debcheck', '-e', '-f', '--latest' ]
        for fg in scenario['fgs']:
            invocation.append('--fg')
            invocation.append(fg.format(m=conf.locations['debmirror'],a=arch))
        for bg in scenario['bgs']:
            invocation.append('--bg')
            invocation.append(bg.format(m=conf.locations['debmirror'],a=arch))
    elif (scenario['type'] == 'source'):
        invocation = ['dose-builddebcheck', '-e', '-f' ]
        invocation.append('--deb-native-arch='+arch)
        for bg in scenario['bins']:
            invocation.append(bg.format(m=conf.locations['debmirror'],a=arch))
        invocation.append(scenario['src'].format(
            m=conf.locations['debmirror']))
    else:
        warning('unknown scenario type: ' + scenario['type'])
    outfile=open(outdir + "/debcheck.out", 'w')
    try:
        subprocess.call(invocation,stdout=outfile)
    except OSError as exc:
        warning('debcheck for {s} on {a} raised {e}'.format(
            a=arch,s=scenario_name,e=exc.strerror))
    outfile.close ()

def getsources(filename):
    res=[]
    if filename[-3:]=='.gz':
        infile = codecs.getreader('utf-8')(gzip.open(filename,'r'))
    else:
        infile = open(filename)
    for line in infile:
        if line.startswith('Package:'):
            current_package=line.split()[1]
        elif line.startswith('Architecture:'):
            current_archs={arch for arch in line.split()[1:]}
            res.append((current_package,current_archs))
    infile.close()
    return(res)

#############################################################################

def archmatch(arch,wildcards):
    i=arch.find('-')
    if i == -1:
        os='linux'
        cpu=arch
    else:
        os=arch[:i]
        cpu=arch[i+1:]
    matchers={'all','any',arch,os+'-any','any-'+arch}
    return(not matchers.isdisjoint(wildcards))

class Universe:
    """
    A universe object contains information about the packages that exist
    in a certain scenario and for a certain architecture. The list
    of foreground packages is written to a file.
    """

    def __init__(self,timestamp,scenario,architecture,summary,sources):
        scenario_name=scenario['name']
        info('extracting foreground for {s} on {a}'.format(
                a=architecture,s=scenario_name))
        self.fg_packages={p for (p,a) in sources if archmatch(architecture,a)}
        summary.set_total(architecture,len(self.fg_packages))
        outdir=cachedir(timestamp,scenario_name,architecture)
        if not os.path.isdir(outdir): os.makedirs(outdir)
        with open(outdir + '/fg-packages', 'w') as outfile:
            for f in self.fg_packages: print(f,file=outfile)

    def is_in_foreground(self,package):
        '''
        tell whether a package is in the foregound
        '''
        return(package in self.fg_packages)

    def source(self,package):
        return(package)

    def source_version(self,package):
        return(0)

class BinUniverse(Universe):
    """
    A binuniverse is a universe for binary packages. It also stores, for
    any binary package name, a source package name and a source version.
    """
    
    def __init__(self,timestamp,scenario,architecture,summary):
        scenario_name=scenario['name']
        info('extracting foreground for {s} on {a}'.format(
                a=architecture,s=scenario_name))

        self.fg_packages=set()
        number_fg_packages=0
        self.source_packages=dict()
        self.source_version_table=dict()

        if scenario['type'] == 'binary' : 
            filelist = scenario['fgs']
        elif scenario['type'] == 'source' :
            filelist = [ scenario['src'] ]
        for fg in filelist:
            fg_filename = fg.format(
                m=conf.locations['debmirror'],a=architecture)
            if fg[-3:]=='.gz':
                infile = codecs.getreader('utf-8')(gzip.open(fg_filename,'r'))
            else:
                infile = open(fg_filename)
            for line in infile:
                if line.startswith('Package:'):
                    current_package=line.split()[1]
                    self.fg_packages.add(current_package)
                    number_fg_packages+=1
                if line.startswith('Source:'):
                    l=line.split()
                    self.source_packages[current_package]=l[1]
                    if len(l) == 3:
                        # the first and last character are parantheses ()
                        self.source_version_table[current_package]=l[2][1:-1]

            infile.close ()

        outdir=cachedir(timestamp,scenario_name,architecture)
        if not os.path.isdir(outdir): os.makedirs(outdir)
        with open(outdir + '/fg-packages', 'w') as outfile:
            for f in self.fg_packages: print(f,file=outfile)

        summary.set_total(architecture,number_fg_packages)
     
    def source(self,package):
        '''
        return the source package name pertaining to a binary package
        '''
        return self.source_packages.get(package,package)

    def source_version(self,package):
        '''
        return the source version of package if one was specified in the
        Packages file, or None othewise (in that case the source version
        is equal to the package version)
        '''
        return self.source_version_table.get(package)

##########################################################################
# top level

def build(timestamp,scenario,architecture):
    outdir=cachedir(timestamp,scenario['name'],architecture)
    if not os.path.isdir(outdir): os.makedirs(outdir)
    run_debcheck(scenario,architecture,outdir)
