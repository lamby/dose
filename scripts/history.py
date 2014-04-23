# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os
from common import *

# update history for an arch (where we have a report in yaml)
def update_history_arch(daystamp,scenario,arch,report):
    dir=history_cachedir(scenario)
    if not os.path.isdir(dir): os.makedirs(dir)

    # read in the old contents of the history file
    histfile=historyfile(scenario,arch)
    history={}
    if os.path.isfile(histfile):
        h=open(histfile)
        for entry in h:
            package,date=entry.split('#')
            history[package] = date.rstrip()
        h.close()

    # rewrite the history file: for each file that is now not installable,
    # write the date found in the old historyfile if it exists, otherwise
    # write the current day.
    outfile=open(histfile,'w')
    if report['report']:
        for stanza in report['report']:
            package  = stanza['package']
            print(package,history.get(package,daystamp),
                  sep='#',
                  file=outfile)
    outfile.close ()

# update history for horizontal summaries (each,some)
def update_history_summary(daystamp,scenario,name,packages,excludes):
    dir=history_cachedir(scenario)
    if not os.path.isdir(dir): os.makedirs(dir)

    # read in the old contents of the history file
    histfile=historyfile(scenario,name)
    history={}
    if os.path.isfile(histfile):
        h=open(histfile)
        for entry in h:
            package,date=entry.split('#')
            history[package] = date.rstrip()
        h.close()

    # rewrite the history file: for each file that is now not installable,
    # write the date found in the old historyfile if it exists, otherwise
    # write the current day.
    outfile=open(histfile,'w')
    for package in packages:
        if package in excludes: continue
        print(package,history.get(package,daystamp),
              sep='#',
              file=outfile)
    outfile.close ()

