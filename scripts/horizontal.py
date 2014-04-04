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
import history

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

summarytable_header="""
<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
<p>
<table border=1>
<tr>
<th>Package</th>
<th>Version</th>
<th>Architectures</th>
<th>Short Explanation (click for details)</th>"""

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

def write_tables(timestamp,scenario,architectures):
    '''
    Create a summary table of packages that are not installable on
    some architectures, and on each architecture
    '''

    outdir=htmldir(timestamp,scenario)
    if not os.path.isdir(outdir): os.makedirs(outdir)
    out_some = open(outdir+'/some.html', 'w')
    out_each = open(outdir+'/each.html', 'w')
    
    print(html_header,
          '<h1>Package not installable on some architectures</h1>',
          summarytable_header,
          file=out_some)
    print(html_header,
          '<h1>Packages not installable on any architecture</h1>',
          summarytable_header,
          file=out_each)
    for package in sorted(uninstallables.keys()):
        print('<tr><td>',package,'</td>',file=out_some,sep='')
        continuation_line=False
        for hash in uninstallables[package]:
            if continuation_line:
                    print('<tr><td></td>',file=out_some)
            if uninstallables[package][hash]['isnative'] == 'True':
                all_mark = '' 
            else:
                all_mark='[all]'
            print('<td>',
                  all_mark,uninstallables[package][hash]['version'],
                  '</td>',
                  file=out_some,sep='')
            print('<td>',file=out_some,end='')
            for arch in uninstallables[package][hash]['archs']:
                print(arch, file=out_some, end=' ')
            print('</td>',file=out_some,end='')
            print('<td>',pack_anchor(timestamp,package,hash),
                  file=out_some,sep='',end='')
            print(shortexplanation[hash],'</a><td>',file=out_some,sep='')
            continuation_line=True

        if not package in installables_somewhere:
            print('<tr><td>',package,'</td>',file=out_each,sep='')
            continuation_line=False
            for hash in uninstallables[package]:
                if continuation_line:
                    print('<tr><td></td>',file=out_each)
                if uninstallables[package][hash]['isnative'] == 'True':
                    all_mark = '' 
                else:
                    all_mark='[all]'
                print('<td>',
                      all_mark,uninstallables[package][hash]['version'],
                      '</td>',
                      file=out_each,sep='')
                print('<td>',file=out_each,end='')
                for arch in uninstallables[package][hash]['archs']:
                    print(arch, file=out_each, end=' ')
                print('</td>',file=out_each)
                print('<td>',pack_anchor(timestamp,package,hash),
                      file=out_each,sep='',end='')
                print(shortexplanation[hash],'</a></td>',file=out_each,sep='')
                continuation_line=True

    print('</table>',html_footer,file=out_some)
    print('</table>',html_footer,file=out_each)
    out_some.close ()
    out_each.close ()

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
def build(timestamp,daystamp,scenario,architectures):
    info('build horizontal tables for {s}'.format(s=scenario))
    analyze_horizontal(timestamp,scenario,architectures)
    write_package_page(timestamp,scenario,architectures)
    write_tables(timestamp,scenario,architectures)
    write_row(timestamp,scenario,architectures)
    history.update_history_summary(daystamp,scenario,'some',
                                   uninstallables, set())
    history.update_history_summary(daystamp,scenario,'each',
                                   uninstallables, installables_somewhere)
