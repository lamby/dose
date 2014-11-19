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

    def __init__(self,scenario_name,timestamp):
        self.scenario_name = scenario_name

        self.architectures = []
        # we only keep architectures for which all the files exist
        for architecture in conf.scenarios[scenario_name]['archs']:
            filelist=conf.scenarios[scenario_name]['fgs'] + \
                      conf.scenarios[scenario_name]['bgs']
            for fg in filelist:
                fg_filename = fg.format(
                    m=conf.locations['debmirror'],a=architecture)
                if not os.path.exists(fg_filename):
                    warning('No such file: {p}, dropping architecture'.format(
                        p=fg_filename,))
                    break
            else:
                self.architectures.append(architecture)

        self.timestamp = timestamp
        self.number_broken = dict()  # arch -> bicounter
        self.history_broken = dict() # arch -> slicenr -> bicounter
        self.number_total = dict()   # arch -> number

    def set_total(self,architecture,number):
        self.number_total[architecture] = number
    
    def get_total(self,architecture):
        return(self.number_total[architecture])

    def set_broken(self,architecture,counter):
        self.number_broken[architecture] = counter

    def get_broken(self,architecture):
        return(self.number_broken[architecture])

    def set_history_broken(self,architecture,d):
        self.history_broken[architecture] = d

    def get_history_broken(self,architecture):
        return(self.history_broken[architecture])

    def get_percentage(self,architecture):
        total_packages=self.get_total(architecture)
        broken_packages=(self.get_broken(architecture)).total()
        if total_packages==0:
            percentage=0
        else:
            percentage=100*broken_packages/total_packages
            return(percentage)

    def get_architectures(self):
        return(self.architectures)

    def dump(self):
        print('Scenario: ', self.scenario_name)
        print('Architectures: ', self.architectures),
        print('Timestamp: ', self.timestamp)
        print('Broken archAll: ', self.number_broken_all)
        print('Broken native: ', self.number_broken_native)
        print('Total ', self.number_total)

    def to_cache(self):
        utc_time=datetime.datetime.utcfromtimestamp(float(self.timestamp))
        outdir=cachedir(self.timestamp,self.scenario_name,'summary')
        if not os.path.isdir(outdir): os.makedirs(outdir)
        with open(outdir+'/row', 'w') as row:
            print('date=',utc_time,file=row,sep='')
            for arch in self.architectures:
                print('{a}={c}'.format(a=arch,c=str(self.get_broken(arch))),
                      file=row)
            print('{a}={c}'.format(a='some',c=str(self.get_broken('some'))),
                  file=row)
            print('{a}={c}'.format(a='each',c=str(self.get_broken('each'))),
                  file=row)

############################################################################

def analyze_horizontal(timestamp,scenario,summary):
    '''
    fill uninstallables, and installables_somewhere
    '''

    global uninstallables, installables_somewhere

    uninstallables = {}
    installables_somewhere = set() 

    for arch in summary.get_architectures():

        counter = bicounter()
        
        # get the set of foreground packages for this architecture
        with open(cachedir(timestamp,scenario,arch)+'/fg-packages') as fg:
            foreground_here = { p.rstrip() for p in fg }

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
            counter.incr(isnative)
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
        summary.set_broken(arch,counter)

        # update installables_somewhere
        installables_somewhere.update(foreground_here - uninstallables_here)

    # count packages notinstallable somewhere or everywhere
    counter_some = bicounter_multi()
    counter_each = bicounter_multi()
    for (package,record) in uninstallables.items():
        counter_some.incr(record)
        if not package in installables_somewhere:
            counter_each.incr(record)
    summary.set_broken('some',counter_some)
    summary.set_broken('each',counter_each)
    total_number_packages = counter_each.total() + len(installables_somewhere)
    summary.set_total('some',total_number_packages)
    summary.set_total('each',total_number_packages)

############################################################################
def write_package_pages(timestamp,scenario):
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
def write_tables(timestamp,day,scenario,what,includes,excludes,
                 bugtable,summary):
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
    html_today=html.summary_multi(timestamp,scenario,what,bugtable,
                                  summary.get_total(what))

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
    summary.set_history_broken(what,counter)

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

########################################################################
# top level
def build(timestamp,day,scenario,bugtable,summary):
    info('build horizontal tables for {s}'.format(s=scenario))
    analyze_horizontal(timestamp,scenario,summary)
    write_package_pages(timestamp,scenario)
    write_tables(timestamp,day,scenario,
                 'some',uninstallables,set(),bugtable,summary)
    write_tables(timestamp,day,scenario,
                 'each',uninstallables,installables_somewhere,bugtable,summary)
    summary.to_cache()
