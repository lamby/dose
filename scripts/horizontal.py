# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

'''
Generation of html pages for stuff that requires accumulation over all
architectures: 
- pages per package that give all the different reasons that occur on some
  architecture
- summary pages for packages not installable on some architecture, or on
  each architecture.
'''

import os, datetime
from common import *
import conf, html

# map a package p that is not installable on at least one architecture
# to a function that maps a hash h to the list of architectures where
# h is the hash of the explanation for package p.
uninstallables = {}

# the set of packages that is known to be installable on at least one
# architecture.
installables_somewhere = set()

# number of packages not installables somewhere / everywhere

class Summary(object):
    """
    Horizontal summary information.
    """

    def __init__(self,scenario_name,architectures,timestamp):
        self.scenario_name = scenario_name
        self.architectures = architectures
        self.timestamp = timestamp
        self.number_total_all = dict()
        self.number_total_native = dict()
        self.number_broken_all = dict()
        self.number_broken_native = dict()

    def set_numbers(self,architecture,
                    total_all,total_native,broken_all,broken_native):
        self.number_total_all[architecture] = total_all
        self.number_total_native[architecture] = total_native
        self.number_broken_all[architecture] = broken_all
        self.number_broken_native[architecture] = broken_native
    

def analyze_horizontal(timestamp,scenario,architectures):
    '''
    fill uninstallables, and installables_somewhere
    '''

    global uninstallables, installables_somewhere

    uninstallables = {}
    installables_somewhere = set() 

    for arch in architectures:
        
        # get the set of foreground packages for this architecture
        arch_packages=open(
            cachedir(timestamp,scenario,arch)+'/fg-packages')
        foreground_here = { p.rstrip() for p in arch_packages }
        arch_packages.close()

        # iterate over the uninstallability reports for this arch, fill in
        # uninstallables, and construct the set of
        # packages uninstallable on this arch
        uninstallables_here = set()
        arch_summary=open(cachedir(timestamp,scenario,arch)+'/summary')
        for entry in arch_summary: 
            package,version,isnative_string,hash,explanation = entry.split('#')
            explanation = explanation.rstrip()
            isnative=isnative_string=='True'
            uninstallables_here.add(package)
            if not package in uninstallables:
                uninstallables[package] = { hash: {'archs'   : [arch],
                                                   'version' : version,
                                                   'isnative': isnative,
                                                   'short'   : explanation}}
            elif not hash in uninstallables[package]:
                uninstallables[package][hash] = {'archs'   : [arch],
                                                 'version' : version,
                                                 'isnative': isnative,
                                                 'short'   : explanation}
            else:
                (uninstallables[package][hash]['archs']).append(arch)
        arch_summary.close()

        # update installables_somewhere
        installables_somewhere.update(foreground_here - uninstallables_here)


def write_package_page(timestamp,scenario,architectures):
    '''
    creates for each package an html page with all reasons for 
    non-installability
    '''
    htmlpooldir = htmldir(timestamp,scenario)+'/packages'
    if not os.path.isdir(htmlpooldir): os.makedirs(htmlpooldir)

    for package in uninstallables:
        
        outfile = open('{d}/{p}.html'.format(d=htmlpooldir,p=package), 'w')
        print(html.html_header,file=outfile)
        print('<h1>Package: {p}</h1>\n<b>Scenario: {s}<br>Date: {d}</b><p>'.format(
                p=package,
                s=scenario,
                d=datetime.datetime.utcfromtimestamp(float(timestamp))),
              file=outfile)
        for hash in uninstallables[package]:
            print('<a name={h}><b>Architectures: {a}</b></a><br>'.format(
                    h=hash,
                    a=str_of_list(uninstallables[package][hash]['archs'])),
                  file=outfile)
            blob=open(cachedir(timestamp,scenario,'pool/')+str(hash))
            print(blob.read(),file=outfile)
            blob.close()
            print('<p>',file=outfile)
                  
        print(html.html_footer,file=outfile)
        outfile.close ()

#############################################################################
def write_tables(timestamp,day,scenario,what,includes,excludes,bugtable):
    '''
    Create a summary table of packages that are not installable a certain
    set of architectures. 
    '''

    daystamp=str(day)

    # assure existence of output directories:
    histcachedir=history_cachedir(scenario)
    if not os.path.isdir(histcachedir): os.makedirs(histcachedir)
    pooldir = cachedir(timestamp,scenario,'pool')
    if not os.path.isdir(pooldir): os.mkdir(pooldir)
    histhtmldir=history_htmldir(scenario,what)
    if not os.path.isdir(histhtmldir): os.makedirs(histhtmldir)
    outdir=htmldir(timestamp,scenario)
    if not os.path.isdir(outdir): os.makedirs(outdir)
    thiscachedir=cachedir(timestamp,scenario,what)
    if not os.path.isdir(thiscachedir): os.makedirs(thiscachedir)

    # fetch the history of packages
    histfile=history_cachefile(scenario,what)
    history={}
    if os.path.isfile(histfile):
        h=open(histfile)
        for entry in h:
            package,date=entry.split('#')
            history[package] = date.rstrip()
        h.close()

    # html output: a summary for this accumulator
    html_today=html.summary_multi(timestamp,scenario,what,bugtable)

    # historic html files for different time slices
    html_history={i:html.history_multi(timestamp,scenario,what,bugtable,
                                       since_days=d)
                  for i,d in conf.hlengths.items()}

    # file recording the first day of observed non-installability per package
    historyfile=open(histfile,'w')

    # count uninstallable packages per history slice
    counter={i:bicounter_multi() for i in conf.hlengths.keys()} 

    for package in sorted(includes.keys()):
        if not package in excludes:
            html_today.write(package,uninstallables[package])
            
            # write to the corresponding historic html page
            # and count archall/native uninstallable packages per slice
            if package in history:
                firstday=int(history[package])
                duration=day-firstday
                hslice=-1
                for i in sorted(conf.hlengths.keys(),reverse=True):
                    if duration >= conf.hlengths[i]:
                        hslice=i
                        break
                if hslice >= 0:
                    counter[hslice].incr(uninstallables[package])
                    html_history[hslice].write(package,
                                               uninstallables[package],
                                               since=date_of_days(firstday))

            # rewrite the history file: for each file that is now not
            # installable, write the date found in the old history_cachefile
            # if it exists, otherwise write the current day.
            print(package,history.get(package,daystamp),
                  sep='#',
                  file=historyfile)

    del html_today
    for f in html_history.values(): del f

    historyfile.close ()
    vertical=open(history_verticalfile(scenario,what),'w')
    for i in conf.hlengths.keys():
        print('{i}={c}'.format(i=i,c=str(counter[i])),file=vertical)
    vertical.close()

    # write a summary of the analysis in the cache directory
    sumfile = open(cachedir(timestamp,scenario,what)+'/summary', 'w')
    for package in sorted(includes.keys()):
        if not package in excludes:
            for hash in uninstallables[package]:
                record=uninstallables[package][hash]
                print(package,record['version'],record['isnative'],
                      hash,record['short'],'',
                      file=sumfile, sep='#',end='')
                for arch in record['archs']:
                    print(arch,file=sumfile,end=' ')
                print('',file=sumfile)
    sumfile.close()
#############################################################################

def write_row(timestamp,scenario,architectures):
    '''
    create a row of the scenario table for the current timestamp
    '''
    
    outdir=cachedir(timestamp,scenario,'summary')
    if not os.path.isdir(outdir): os.makedirs(outdir)

    row=open(outdir+'/row', 'w')
    print('date=',
          datetime.datetime.utcfromtimestamp(float(timestamp)),
          file=row,sep='')
    for arch in architectures:
        counter = bicounter()
        with open(cachedir(timestamp,scenario,arch)+'/summary') as summary:
            for entry in summary:
                counter.incr((entry.split('#'))[2] == "True")
        print('{a}={c}'.format(a=arch,c=str(counter)),file=row)

    # count packages notinstallable somewhere or everywhere
    counter_some = bicounter_multi()
    counter_each = bicounter_multi()
    for (package,record) in uninstallables.items():
        counter_some.incr(record)
        if not package in installables_somewhere:
            counter_each.incr(record)
    print('{a}={c}'.format(a='some',c=str(counter_some)),file=row)
    print('{a}={c}'.format(a='each',c=str(counter_each)),file=row)

    row.close ()
    

########################################################################
# top level
def build(timestamp,day,scenario,architectures,bugtable):
    info('build horizontal tables for {s}'.format(s=scenario))
    analyze_horizontal(timestamp,scenario,architectures)
    write_package_page(timestamp,scenario,architectures)
    write_tables(timestamp,day,scenario,
                 'some',uninstallables,set(),bugtable)
    write_tables(timestamp,day,scenario,
                 'each',uninstallables,installables_somewhere,bugtable)
    write_row(timestamp,scenario,architectures)
