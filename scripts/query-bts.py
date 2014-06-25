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

# print each bug number with its package name, and all affected packages
for status in debianbts.get_status(list(bugnrs)):
    if not status.done:
        print status.bug_num, status.package,
        for p in status.affects:
            print p,
        print ''

