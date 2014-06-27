#!/usr/bin/python3

# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os, subprocess, collections
import common, conf

class Bugtable(object):
    """
    represents a collection of relevant bugs obtained from the Debian
    BTS, together with the information which binary or source packages
    are directly (when mentionend in the bug attributes) or
    indirectly (via a dependency chain) concerned.
    """

    def __init__(self):
        common.info('Initialising bug table')
        self.binbugs=collections.defaultdict(list)
        self.srcbugs=collections.defaultdict(list)
        script=conf.locations['scriptdir']+'/query-bts.py'
        with subprocess.Popen(script,stdout=subprocess.PIPE) as bts_answer:
            for rawline in bts_answer.stdout:
                line=rawline.split()
                bugnr=str(line[0],'utf-8')
                for word in line[1:]:
                    package=str(word,'utf-8')
                    if package[0:4] == 'src:':
                        # bug against a source package
                        source=package[4:]
                        self.srcbugs[source].append(bugnr)
                    else:
                        # bug against a binary package
                        self.binbugs[package].append(bugnr)
    
    def print_direct(self,package_name,outfile):
        """
        print in html to outfile all direct bugs for package_name, with
        links to the Debian BTS.
        """
        for bugnr in self.binbugs[package_name]:
            print('[<a href="http://bugs.debian.org/{n}">Bug #{n}</a>]'.format(
                    n=bugnr),
                  file=outfile,end=' ')


