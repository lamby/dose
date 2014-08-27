#!/usr/bin/python

# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

architectures = {
    'unstable' : [ 'amd64', 'arm64', 'armel', 'armhf', 'hurd-i386', 'i386',
                   'kfreebsd-amd64', 'kfreebsd-i386', 'mips', 'mipsel',
                   'powerpc', 'ppc64el', 's390x' ],
    'testing' :  [ 'amd64', 'armel', 'armhf', 'i386', 'kfreebsd-amd64',
                   'kfreebsd-i386', 'mips', 'mipsel', 'powerpc', 's390x' ]
}

locations = {
    'debmirror' : '/srv/mirrors/debian/dists',
    'cacheroot' : '/srv/qa.debian.org/data/dose-debcheck',
    'htmlroot'  : '/srv/qa.debian.org/web/dose/debcheck',
    'scriptdir' : '/home/treinen/dose/scripts'
}

scenarios = {
    'unstable_main': {
        'archs' : architectures['unstable'],
        'fgs'   : [ '{m}/unstable/main/binary-{a}/Packages.gz' ],
        'bgs'   : [],
        'description' : 'Debian unstable (main only)'
        },
    'unstable_contrib+nonfree': {
        'archs' : architectures['unstable'],
        'fgs'   : [ '{m}/unstable/contrib/binary-{a}/Packages.gz',
                    '{m}/unstable/non-free/binary-{a}/Packages.gz' ],
        'bgs'   : [ '{m}/unstable/main/binary-{a}/Packages.gz' ],
        'description' : 'Debian unstable (contrib and non-free only)'
        },
    'testing_main': {
        'archs' : architectures['testing'],
        'fgs'   : [ '{m}/testing/main/binary-{a}/Packages.gz' ],
        'bgs'   : [],
        'description' : 'Debian testing (main only)'
        },
    'testing_contrib+nonfree': {
        'archs' : architectures['testing'],
        'fgs'   : [ '{m}/testing/contrib/binary-{a}/Packages.gz',
                    '{m}/testing/non-free/binary-{a}/Packages.gz' ],
        'bgs'   : [ '{m}/testing/main/binary-{a}/Packages.gz' ],
        'description' : 'Debian testing (contrib and non-free only)'
        }

}

slices = 7
