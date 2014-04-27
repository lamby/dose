#!/usr/bin/python

# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

architectures = {
    'unstable' : [ 'amd64', 'armel', 'armhf', 'hurd-i386', 'i386',
                   'kfreebsd-amd64', 'kfreebsd-i386', 'mips', 'mipsel',
                   'powerpc', 's390x' ],
    'testing' :  [ 'amd64', 'armel', 'armhf', 'i386', 'kfreebsd-amd64',
                   'kfreebsd-i386', 'mips', 'mipsel', 'powerpc', 's390x' ]
}

locations = {
    'debmirror' : '/srv/mirrors/debian/dists',
    'cacheroot' : '/srv/qa.debian.org/data/dose-debcheck',
    'htmlroot'  : '/srv/qa.debian.org/web/dose/debcheck'
}

scenarios = {
    'unstable_main': {
        'archs' : architectures['unstable'],
        'fgs'   : [ '{m}/unstable/main/binary-{a}/Packages.gz' ],
        'bgs'   : []
        },
    'unstable_contrib+nonfree': {
        'archs' : architectures['unstable'],
        'fgs'   : [ '{m}/unstable/contrib/binary-{a}/Packages.gz',
                    '{m}/unstable/non-free/binary-{a}/Packages.gz' ],
        'bgs'   : [ '{m}/unstable/main/binary-{a}/Packages.gz' ]
        },
    'testing_main': {
        'archs' : architectures['testing'],
        'fgs'   : [ '{m}/testing/main/binary-{a}/Packages.gz' ],
        'bgs'   : []
        },
    'testing_contrib+nonfree': {
        'archs' : architectures['testing'],
        'fgs'   : [ '{m}/testing/contrib/binary-{a}/Packages.gz',
                    '{m}/testing/non-free/binary-{a}/Packages.gz' ],
        'bgs'   : [ '{m}/testing/main/binary-{a}/Packages.gz' ]
        }

}

slices = 7
