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
<th>Tracking</th>
'''

summary_history_header = '''
<h1>Packages not installable on {what} architecture in scenario {scenario}
for {d} days</h1>
<b>Date: {utctime} UTC</b>
<p>

Packages that have been continuously found to be not installable
(not necessarily in the same version,
 not necessarily on the same architectures,
 and not necessarily with the same explanation all the time).<p>
<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
<p>
<table border=1>
<tr>
<th>Package</th>
<th>Since</th>
<th>Version today</th>
<th>Architectures</th>
<th>Short explanation as of today (click for details)</th>
<th>Tracking</th>
'''

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
            package,version,isnative,hash,explanation = entry.split('#')
            explanation = explanation.rstrip()
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
        print(html_header,file=outfile)
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
                  
        print(html_footer,file=outfile)
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
    outfile = open('{d}/{w}.html'.format(d=outdir,w=what), 'w')
    print(html_header,file=outfile)
    print(summary_header.format(
            timestamp=str(timestamp),
            scenario=scenario,
            what=what,
            utctime=datetime.datetime.utcfromtimestamp(float(timestamp))),
          file=outfile)

    # historic html files for different time slices
    hfiles={i:open(history_htmlfile(scenario,what,d),'w')
            for i,d in hlengths.items()}
    for i in hfiles.keys():
        print(html_header,file=hfiles[i])
        print(summary_history_header.format(
                timestamp=str(timestamp),
                scenario=scenario,
                what=what,
                d=hlengths[i],
                utctime=datetime.datetime.utcfromtimestamp(float(timestamp))),
              file=hfiles[i])

    # file recording the first day of observed non-installability per package
    historyfile=open(histfile,'w')

    # number of uninstallable arch=all packages per slice
    count_archall={i:0 for i in hlengths.keys()}
    # number of uninstallable native packages per slice
    count_natives={i:0 for i in hlengths.keys()}

    for package in sorted(includes.keys()):
        if not package in excludes:

            # write to html file for that day
            number_of_hashes=len(uninstallables[package])
            if number_of_hashes > 1:
                multitd='<td rowspan="'+str(number_of_hashes)+'">'
            else:
                multitd='<td>'
            print('<tr>',multitd,package,'</td>',file=outfile,sep='')
            continuation_line=False
            for hash in uninstallables[package]:
                if continuation_line:
                    print('<tr>',file=outfile)
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
                print('<td>',
                      pack_anchor(timestamp,package,hash),
                      uninstallables[package][hash]['short'],
                      '</a></td>',
                      file=outfile,sep='')
                if not continuation_line:
                    print(multitd,file=outfile,end='')
                    bugtable.print_indirect(package,outfile)
                    print('</td>',file=outfile,end='')
                continuation_line=True

            # write to the corresponding historic html page
            # and count archall/native uninstallable packages per slice
            if package in history:
                firstday=int(history[package])
                duration=day-firstday
                for i in sorted(hlengths.keys(),reverse=True):
                    if duration >= hlengths[i]:
                        if uninstallables[package][hash]['isnative'] == 'True':
                            count_natives[i] += 1
                        else:
                            count_archall[i] += 1
                        number_of_hashes=len(uninstallables[package])
                        if number_of_hashes > 1:
                            multitd='<td rowspan="'+str(number_of_hashes)+'">'
                        else:
                            multitd='<td>'
                        print('<tr>',multitd,package,'</td>',file=hfiles[i],sep='')
                        print(multitd,date_of_days(firstday),'</td>',
                              file=hfiles[i],sep="")
                        continuation_line=False
                        for hash in uninstallables[package]:
                            if continuation_line==True:
                                 print('<tr>',file=hfiles[i])
                            if uninstallables[package][hash]['isnative'] == 'True':
                                all_mark = '' 
                            else:
                                all_mark='[all]'
                            print('<td>',
                                  all_mark,
                                  uninstallables[package][hash]['version'],
                                  '</td>',
                                  file=hfiles[i],sep='')
                            print('<td>',file=hfiles[i],end='')
                            for arch in uninstallables[package][hash]['archs']:
                                print(arch, file=hfiles[i], end=' ')
                            print('</td>',file=hfiles[i],end='')
                            print('<td>',pack_anchor_from_hist(
                                    timestamp,package,hash),
                                  uninstallables[package][hash]['short'],
                                  '</a></td>',
                                  file=hfiles[i], sep='')
                            if not continuation_line:
                                print(multitd,file=hfiles[i],end='')
                                bugtable.print_indirect(package,hfiles[i])
                                print('</td>',file=hfiles[i],end='')
                            continuation_line=True
                        break

            # rewrite the history file: for each file that is now not
            # installable, write the date found in the old history_cachefile
            # if it exists, otherwise write the current day.
            print(package,history.get(package,daystamp),
                  sep='#',
                  file=historyfile)

    print('</table>',html_footer,file=outfile)
    outfile.close ()
    for f in hfiles.values():
        print('</table>',html_footer,file=f)
        f.close()
    historyfile.close ()
    vertical=open(history_verticalfile(scenario,what),'w')
    for i in hlengths.keys():
        print('{i}={cn}/{ca}'.format(
                i=i,cn=count_natives[i],ca=count_archall[i]),file=vertical)
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
def build(timestamp,day,scenario,architectures,bugtable):
    info('build horizontal tables for {s}'.format(s=scenario))
    analyze_horizontal(timestamp,scenario,architectures)
    write_package_page(timestamp,scenario,architectures)
    write_tables(timestamp,day,scenario,
                 'some',uninstallables,set(),bugtable)
    write_tables(timestamp,day,scenario,
                 'each',uninstallables,installables_somewhere,bugtable)
    write_row(timestamp,scenario,architectures)
