# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os
from common import *

# update history for an arch (where we have a report in yaml)
def update_history_arch(day,scenario,arch,report):
    daystamp=str(day)

    # read in the old contents of the history file
    histfile=history_cachefile(scenario,arch)
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
    cachedir=history_cachedir(scenario)
    if not os.path.isdir(cachedir): os.makedirs(cachedir)
    outfile=open(histfile,'w')
    if report['report']:
        for stanza in report['report']:
            package  = stanza['package']
            print(package,history.get(package,daystamp),
                  sep='#',
                  file=outfile)
    outfile.close ()

    # write summaries in history html files
    htmldir=history_htmldir(scenario,arch)
    if not os.path.isdir(htmldir): os.makedirs(htmldir)
    hlengths={0:2,1:4,2:8,3:16,4:32,5:64,6:128,7:256,8:512}
    hfiles={i:open(history_htmlfile(scenario,arch,d),'w')
            for i,d in hlengths.items()}
    if report['report']:
        for stanza in report['report']:
            package  = stanza['package']
            if package in history:
                firstday=int(history[package])
                duration=day-firstday
                for i in sorted(hlengths.keys(),reverse=True):
                    if duration >= hlengths[i]:
                        print(package,file=hfiles[i])
                        break
    for f in hfiles.values(): f.close()

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

