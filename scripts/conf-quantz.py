#!/usr/bin/python

# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

verbose=False

locations = {
    'debmirror' : '/srv/mirrors/debian/dists',
    'cacheroot' : '/srv/qa.debian.org/data/dose-debcheck',
    'htmlroot'  : '/srv/qa.debian.org/web/dose/debcheck',
    'scriptdir' : '/srv/qa.debian.org/dose'
}

def _get_architectures(archs):
    import os.path as osp
    from debian import deb822

    for dist in archs:
        path = osp.join(locations['debmirror'], dist, 'Release')
        with open(path) as fp:
            release = deb822.Release(fp)
        archs[dist] = [arch for arch in release['Architectures'].split()
                       if arch not in excluded_archs]

excluded_archs = ('sparc')
architectures = {
    'testing': None,
    'unstable': None,
}
_get_architectures(architectures)

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

# number of runs that are diplays
slices = 7

# timeslices for the "summary by duration"
hlengths={0:2,1:4,2:8,3:16,4:32,5:64,6:128}

