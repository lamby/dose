#!/usr/bin/python

# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os

home=os.getenv("HOME")

locations = {
    'debmirror' : '/srv/mirrors/debian/dists',
    'cacheroot' : '/srv/qa.debian.org/data/dose-debcheck',
    'htmlroot'  : '/srv/qa.debian.org/web/dose/debcheck'
}

scenarios = {
    'sid_main': {
        'archs' : [ 'amd64', 'i386', 'powerpc' ],
        'fgs'   : [ '{m}/unstable/main/binary-{a}/Packages' ],
        'bgs'   : []
        }
}

slices = 7
