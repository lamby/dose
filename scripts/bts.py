#!/usr/bin/python3

# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os, subprocess
import common, conf

def init():
    common.info('Initialising bug table')
    binbugs=dict()
    srcbugs=dict()
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
                    if source in srcbugs:
                        srcbugs[source] =+ bugnr
                    else:
                        srcbugs[source]=[bugnr]
                else:
                    # bug against a binary package
                    if package in binbugs:
                        binbugs[package] =+ bugnr
                    else:
                        binbugs[package]=[bugnr]
    
    return(binbugs,srcbugs)

