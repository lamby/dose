#!/usr/bin/python3

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

import os, subprocess, collections
import common, conf

class Bugtable(object):
    """
    Associate bug numbers to packages.

    A bug with number n concerns a package p with source s directly
    when the bug n has Package field p, or Source field s, or p is a
    member of the Affects field of bug n. Upon initialisation, a
    bugtable object is initialised with all packages directly
    concerned by packages that have certain user-tags.
    
    A bug concerns a package p indirectly when it concern directly
    some package on one of the dependency chains from p to a problem
    reported by dose-debcheck. Indirect bugs are discovered on the fly.
    """

    def __init__(self):
        common.info('Initialising bug table')
        self.binbugs=collections.defaultdict(set)
        self.srcbugs=collections.defaultdict(set)
        self.indbugs=collections.defaultdict(set)
        # disable running query-bts, until python-debianbts on quantz.d.o
        # is upgraded to >= 2.5.2
        # query_script=conf.locations['scriptdir']+'/query-bts.py'
        # with subprocess.Popen([query_script],
        #                       stdout=subprocess.PIPE) as bts_query:
        #     for rawline in bts_query.stdout:
        #         line=rawline.split()
        #         bugnr=int(line[0])
        #         for word in line[1:]:
        #             package=str(word,'utf-8')
        #             if package[0:4] == 'src:':
        #                 # bug against a source package
        #                 source=package[4:]
        #                 self.srcbugs[source].add(bugnr)
        #             else:
        #                 # bug against a binary package
        #                 self.binbugs[package].add(bugnr)

    def dump(self):
        print('Direct Binary:')
        print('==============')
        for  p in sorted(self.binbugs.keys()):
            if self.binbugs[p]:
                print(p,self.binbugs[p])
        print('Direct Source:')
        print('==============')
        for p in sorted(self.srcbugs.keys()):
            if self.srcbugs[p]:
                print(p,self.srcbugs[p])
        print('Indirect:')
        print('=========')
        for p in sorted(self.indbugs.keys()):
            if self.indbugs[p]:
                print(p,self.indbugs[p])

    def print_direct(self,package_name,source_name,root_package,outfile):
        """
        print in html to outfile all direct bugs for binary package 
        package_name, or source_package source_name with links to the
        Debian BTS. Register the found bugs as indirect bugs of
        root_package.
        """
        for bugnr in self.binbugs[package_name] | self.srcbugs[source_name]:
            print('[<a href="http://bugs.debian.org/{n}">Bug #{n}</a>]'.format(
                    n=bugnr),
                  file=outfile,end=' ')
        self.indbugs[root_package].update(self.binbugs[package_name])
        self.indbugs[root_package].update(self.srcbugs[source_name])

    def print_source(self,package_name,outfile):
        """
        print in html to outfile  all direct bugs for source package
        package_name, with link to the BTS.
        """
        for bugnr in self.srcbugs[package_name]:
            print('[<a href="http://bugs.debian.org/{n}">Bug #{n}</a>]'.format(
                    n=bugnr),
                  file=outfile,end=' ')

    def print_indirect(self,package_name,outfile):
        """
        print in html to outfile all indirect bugs for package_name, with
        links to the Debian BTS.
        """
        for bugnr in self.indbugs[package_name]:
            print('[<a href="http://bugs.debian.org/{n}">#{n}</a>]'.format(
                    n=bugnr),
                  file=outfile,end=' ')
