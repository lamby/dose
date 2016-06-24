# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

############################################################################
# please push all changes to the git repository, otherwise they might get  #
# overwritten:    git+ssh://git.debian.org/git/qa/dose.git                 #
############################################################################

"""
Functions that operate on package universes.
"""

import os, subprocess, gzip, lzma, codecs
import conf
from common import *

def openr(filename):

    """
    open a possibly compressed file for reading
    """
    
    if filename[-3:]=='.gz':
        reader = codecs.getreader('utf-8')(gzip.open(filename,mode='r'))
    elif filename[-3:]=='.xz':
        reader = codecs.getreader('utf-8')(lzma.open(filename,mode='r'))
    else:
        reader = open(filename,mode='r')
    return(reader)

def uncompress(to_uncompress):

    """
    Uncompress (xz) all files as given by to_uncompress, then reset 
    to_uncompress to the empty list.
    """

    print(to_uncompress)
    for (orig,new) in to_uncompress:
        if not os.path.exists(new):
            os.makedirs(os.path.dirname(new))
            with open(new,mode='w') as outfile:
                subprocess.call(['unxz', orig],stdout=outfile)
    to_uncompress.clear()

def realfilename(filespec,architecture,outdir,to_uncompress):

    """
    translates a specification string of a filename (a format) into
    a real file name, taking into account the architecture.
 
    Modifies to_uncompress.
    """
    
    if filespec[-3:]=='.xz':
        # for xz files, the real file name is a cached file since we have
        # to explicitely uncompress these files. Uncompressed xz files
        # are cached under the directory specified by the cacheroot
        # configuration variable.
        f=filespec.format(m=outdir,a=architecture)
        f=f[:-3]
        orig=filespec.format(m=conf.locations['debmirror'],a=architecture)
        to_uncompress.append((orig,f))
    else:
        f=filespec.format(m=conf.locations['debmirror'],a=architecture)
    return(f)
    
def run_debcheck(scenario,arch,outdir):

    """
    run dose-debcheck and store the resulting report
    """

    scenario_name = scenario['name']
    to_uncompress = [] 
    info('running debcheck for {s} on {a}'.format(a=arch,s=scenario_name))
    if (scenario['type'] == 'binary'):
        invocation = ['dose-debcheck', '-e', '-f', '--latest' ]
        invocation.append('--deb-native-arch='+arch)
        for fg in scenario['fgs']:
            invocation.append('--fg')
            invocation.append(realfilename(fg,arch,outdir,to_uncompress))
        for bg in scenario['bgs']:
            invocation.append('--bg')
            invocation.append(realfilename(bg,arch,outdir,to_uncompress))
    elif (scenario['type'] == 'source'):
        invocation = ['dose-builddebcheck', '-e', '-f', '--quiet' ]
        invocation.append('--deb-native-arch='+arch)
        for bg in scenario['bins']:
            invocation.append(realfilename(bg,arch,outdir,to_uncompress))
        invocation.append(realfilename(scenario['src'],arch,outdir,to_uncompress))
    else:
        warning('unknown scenario type: ' + scenario['type'])
    outfile=open(outdir + "/debcheck.out", 'w')
    try:
        uncompress(to_uncompress)
        subprocess.call(invocation,stdout=outfile)
    except OSError as exc:
        warning('debcheck for {s} on {a} raised {e}'.format(
            a=arch,s=scenario_name,e=exc.strerror))
    outfile.close ()

def getsources(filename):
    # scans file named filename for source package stanzas.
    # returns a pair of hashtables, associating to each source package name
    # found the contents of Architecture:, resp Version:, field of the last
    # occurrence. Stanzas with 'Extra-Source-Only: yes' are skipped.
    version_table={}
    archs_table={}
    saved=True
    infile = openr(filename)
    for line in infile:
        if line.startswith('Package:'):
            current_package=line.split()[1]
            saved=False
            current_extra_source_only=False
        elif line.startswith('Architecture:'):
            current_archs={arch for arch in line.split()[1:]}
        elif line.startswith('Extra-Source-Only:'):
            current_extra_source_only=line.endswith('yes\n')
        elif line.startswith('Version:'):
            current_version=line.split()[1]
        elif line.isspace() and not saved and not current_extra_source_only:
            archs_table[current_package]=current_archs
            version_table[current_package]=current_version
            saved=True
    if not saved and not current_extra_source_only:
        archs_table[current_package]=current_archs
        version_table[current_package]=current_version
    infile.close()
    return((version_table,archs_table))

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

class SrcUniverse:
    """
    A universe object contains information about the source
    packages that exist in a certain scenario.
    architecture. The list of foreground packages is written to a
    file.
    """

    def __init__(self,timestamp,scenario,architecture,summary,
                 versions_table,archs_table):
        scenario_name=scenario['name']
        info('extracting foreground for {s} on {a}'.format(
                a=architecture,s=scenario_name))
        self.fg_packages={p:v for (p,v) in versions_table.items()
                          if archmatch(architecture,archs_table[p])}
        summary.set_total(architecture,len(self.fg_packages))
        outdir=cachedir(timestamp,scenario_name,architecture)
        if not os.path.isdir(outdir): os.makedirs(outdir)
        with open(outdir + '/fg-packages', 'w') as outfile:
            for f in self.fg_packages: print(f,file=outfile)

        # collect source package name and version for binary packages
        self.source_packages=dict()
        self.source_version_table=dict()
        for inputspec in scenario['bins']:
            inputpath = inputspec.format(
                m=conf.locations['debmirror'],a=architecture)
            infile = openr(inputpath)
            for line in infile:
                if line.startswith('Package:'):
                    current_package=line.split()[1]
                if line.startswith('Source:'):
                    l=line.split()
                    self.source_packages[current_package]=l[1]
                    if len(l) == 3:
                        # the first and last character are parantheses ()
                        self.source_version_table[current_package]=l[2][1:-1]
            infile.close ()

            
    def is_in_foreground(self,package_name,version):
        '''
        tell whether a package is in the foregound
        '''
        try:
            return(version == self.fg_packages[package_name])
        except KeyError:
            return(False)

    def is_in_foreground_someversion(self,package_name):
        '''
        tell whether a package is in the foregound for any version
        '''
        return(package_name in self.fg_packages.keys())

    def source(self,package):
        '''
        return the source package name pertaining to a binary package
        '''
        return self.source_packages.get(package,package)

    def source_version(self,package):
        '''
        return the source version of package if one was specified in the
        Packages file, or None otherwise (in that case the source version
        is equal to the package version)
        '''
        return self.source_version_table.get(package)

#############################################################################
class BinUniverse:
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

        for inputspec in scenario['fgs']:
            inputpath = inputspec.format(
                m=conf.locations['debmirror'],a=architecture)
            infile = openr(inputpath)
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

        for inputspec in scenario['bgs']:
            inputpath = inputspec.format(
                m=conf.locations['debmirror'],a=architecture)
            infile = openr(inputpath)
            for line in infile:
                if line.startswith('Package:'):
                    current_package=line.split()[1]
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

    def is_in_foreground(self,package_name,version):
        '''
        tell whether a package is in the foregound
        '''
        return(package_name in self.fg_packages)

    def is_in_foreground_someversion(self,package_name):
        '''
        tell whether a package is in the foregound for any version
        '''
        return(package_name in self.fg_packages)

    def source(self,package):
        '''
        return the source package name pertaining to a binary package
        '''
        return self.source_packages.get(package,package)

    def source_version(self,package):
        '''
        return the source version of package if one was specified in the
        Packages file, or None otherwise (in that case the source version
        is equal to the package version)
        '''
        return self.source_version_table.get(package)

##########################################################################
# top level

def build(timestamp,scenario,architecture):
    outdir=cachedir(timestamp,scenario['name'],architecture)
    if not os.path.isdir(outdir): os.makedirs(outdir)
    run_debcheck(scenario,architecture,outdir)
