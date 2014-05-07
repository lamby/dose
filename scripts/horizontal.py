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

# map a hash of explanation to a short explanation
shortexplanation = {}

# map a package p that is not installable on at least one architecture
# to a function that maps a hash h to the list of architectures where
# h is the hash of the explanation for package p.
uninstallables = {}

# the set of packages that is known to be installable on at least one
# architecture.
installables_somewhere = set()

# number of packages not installables somewhere / everywhere

summary_header='''
<h1>Packages not installable on {what} architecture in scenario {scenario}</h1>
<b>Date: {utctime} UTC</b>
<p>
<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
<p>
<table border=1>
<tr>
<th>Package</th>
<th>Version</th>
<th>Architectures</th>
<th>Short Explanation (click for details)</th>
'''

def analyze_horizontal(timestamp,scenario,architectures):
    '''
    fill shortexplanation, uninstallables, and installables_somewhere
    '''

    global shortexplanation, uninstallables, installables_somewhere

    shortexplanation = {}
    uninstallables = {}
    installables_somewhere = set() 

    for arch in architectures:
        
        # get the set of foreground packages for this architecture
        arch_packages=open(
            cachedir(timestamp,scenario,arch)+'/fg-packages')
        foreground_here = { p.rstrip() for p in arch_packages }
        arch_packages.close()

        # iterate over the uninstallability reports for this arch, fill in
        # uninstallables and shortexplanation, and construct the set of
        # packages uninstallable on this arch
        uninstallables_here = set()
        arch_summary=open(cachedir(timestamp,scenario,arch)+'/summary')
        for entry in arch_summary: 
            package,version,isnative,hash,explanation = entry.split('#')
            explanation = explanation.rstrip()
            uninstallables_here.add(package)
            if not package in uninstallables:
                uninstallables[package] = { hash: {'archs'   : [arch],
                                                   'version' : version,
                                                   'isnative': isnative}}
                shortexplanation[hash] = explanation
            elif not hash in uninstallables[package]:
                uninstallables[package][hash] = {'archs'   : [arch],
                                                 'version' : version,
                                                 'isnative': isnative}
                shortexplanation[hash] = explanation
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
        print(html_header,file=outfile)
        print('<h1>Package: {p}</h1><h1>Scenario: {s}</h1><h1>Date: {d}</h1>'.format(
                p=package,
                s=scenario,
                d=datetime.datetime.utcfromtimestamp(float(timestamp))),
              file=outfile)
        for hash in uninstallables[package]:
            print('<hr><a name={h}><b>Architectures: {a}</b></a><br>'.format(
                    h=hash,
                    a=str_of_list(uninstallables[package][hash]['archs'])),
                  file=outfile)
            blob=open(cachedir(timestamp,scenario,'pool/')+str(hash))
            print(blob.read(),file=outfile)
            blob.close()
                  
        print(html_footer,file=outfile)
        outfile.close ()

#############################################################################
def write_tables(timestamp,day,scenario,what,includes,excludes):
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
    outfile = open('{d}/{w}.html'.format(d=outdir,w=what), 'w')
    print(html_header,file=outfile)
    print(summary_header.format(
            timestamp=str(timestamp),
            scenario=scenario,
            what=what,
            utctime=datetime.datetime.utcfromtimestamp(float(timestamp))),
          file=outfile)

    # file recording the first day of observed non-installability per package
    historyfile=open(histfile,'w')

    for package in sorted(includes.keys()):
        if not package in excludes:

            # write to html file for that day
            print('<tr><td>',package,'</td>',file=outfile,sep='')
            continuation_line=False
            for hash in uninstallables[package]:
                if continuation_line:
                    print('<tr><td></td>',file=outfile)
                if uninstallables[package][hash]['isnative'] == 'True':
                    all_mark = '' 
                else:
                    all_mark='[all]'
                print('<td>',
                      all_mark,uninstallables[package][hash]['version'],
                      '</td>',
                      file=outfile,sep='')
                print('<td>',file=outfile,end='')
                for arch in uninstallables[package][hash]['archs']:
                    print(arch, file=outfile, end=' ')
                print('</td>',file=outfile,end='')
                print('<td>',pack_anchor(timestamp,package,hash),
                      file=outfile,sep='',end='')
                print(shortexplanation[hash],'</a><td>',file=outfile,sep='')
                continuation_line=True


            # rewrite the history file: for each file that is now not
            # installable, write the date found in the old history_cachefile
            # if it exists, otherwise write the current day.
            print(package,history.get(package,daystamp),
                  sep='#',
                  file=historyfile)

    print('</table>',html_footer,file=outfile)
    outfile.close ()
    historyfile.close ()


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
        count_natives=0
        count_archall=0
        summary=open(cachedir(timestamp,scenario,arch)+'/summary')
        for entry in summary:
            if (entry.split('#'))[2] == "True":
                count_natives += 1
            else:
                count_archall += 1
        summary.close()
        print('{a}={cn}/{ca}'.format(
                cn=count_natives,
                ca=count_archall,
                a=arch),
              file=row,sep='')

    # count packages notinstallable somewhere or everywhere
    countsome_natives=0
    countsome_archall=0
    counteach_natives=0
    counteach_archall=0
    for package in uninstallables:
        isnative=False
        for h in uninstallables[package]:
            if uninstallables[package][h]['isnative'] == 'True':
                isnative = True
                break
        if isnative:
            countsome_natives += 1
        else:
            countsome_archall += 1
        if not package in installables_somewhere:
            if isnative:
                counteach_natives += 1
            else:
                counteach_archall += 1

    print('{a}={cn}/{ca}'.format(
            cn=countsome_natives,
            ca=countsome_archall,
            a='some'),
          file=row,sep='')
    print('{a}={cn}/{ca}'.format(
            cn=counteach_natives,
            ca=counteach_archall,
            a='each'),
          file=row,sep='')

    row.close ()
    

########################################################################
# top level
def build(timestamp,day,scenario,architectures):
    info('build horizontal tables for {s}'.format(s=scenario))
    analyze_horizontal(timestamp,scenario,architectures)
    write_package_page(timestamp,scenario,architectures)
    write_tables(timestamp,day,scenario,
                 'some',uninstallables,set())
    write_tables(timestamp,day,scenario,
                 'each',uninstallables,installables_somewhere)
    write_row(timestamp,scenario,architectures)
