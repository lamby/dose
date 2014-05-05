# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os
from common import *

# update history for horizontal summaries (each,some)
def update_history_summary(day,scenario,name,packages,excludes):
    daystamp=str(day)
    
    cachedir=history_cachedir(scenario)
    if not os.path.isdir(cachedir): os.makedirs(cachedir)

    # read in the old contents of the history file
    histfile=history_cachefile(scenario,name)
    history={}
    if os.path.isfile(histfile):
        h=open(histfile)
        for entry in h:
            package,date=entry.split('#')
            history[package] = date.rstrip()
        h.close()

    # rewrite the history file: for each file that is now not installable,
    # write the date found in the old history_cachefile if it exists,
    # otherwise write the current day.
    outfile=open(histfile,'w')
    for package in packages:
        if package in excludes: continue
        print(package,history.get(package,daystamp),
              sep='#',
              file=outfile)
    outfile.close ()

