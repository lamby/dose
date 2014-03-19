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
    'unstable_main': {
        'archs' : [ 'amd64', 'armel', 'armhf', 'hurd-i386', 'i386',
                    'kfreebsd-amd64', 'kfreebsd-i386',
                    'mips', 'mipsel', 'powerpc', 's390x', 'sparc' ],
        'fgs'   : [ '{m}/unstable/main/binary-{a}/Packages.gz' ],
        'bgs'   : []
        }
}

slices = 7
