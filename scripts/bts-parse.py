#!/usr/bin/python2.7

# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import debianbts
import itertools

# get the numbers of all bugs with usertag edos-*
umail='treinen@debian.org'
utags=['edos-outdated', 'edos-uninstallable']
bugnrs=itertools.chain.from_iterable(
    debianbts.get_usertag(umail,*utags).values())

binbugs=dict()
srcbugs=dict()
statuslist=debianbts.get_status(list(bugnrs))

for status in statuslist:
    if not status.done:
        number=status.bug_num
        package=status.package
        if package[0:4] == 'src:':
            # bug against a source package
            source=package[4:]
            if source in srcbugs:
                srcbugs[source] =+ number
            else:
                srcbugs[source]=[number]
        else:
            # bug against a binary package
            if package in binbugs:
                binbugs[package] =+ number
            else:
                binbugs[package]=[number]

        for p in status.affects:
            if p in binbugs:
                binbugs[p] =+ number
            else:
                binbugs[p]=[number]

out=open('binary','w')
for p in binbugs.keys():
    print >> out, '{p}'.format(p=p),
    for n in binbugs[p]:
        print >> out, '{n} '.format(n=n),
        print >> out, ''
out.close()

out=open('source','w')
for p in srcbugs.keys():
    print >> out, '{p}'.format(p=p),
    for n in srcbugs[p]:
        print >> out, '{n} '.format(n=n),
        print >> out, ''
out.close()

