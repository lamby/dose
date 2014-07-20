# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import yaml,os, hashlib, datetime
from common import *

diff_header='''
<h1>Difference for {arch} in scenario {scenario}</h1>
<b>From {tprev} UTC<br>To {tthis} UTC</b>
<p>
<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
'''

table_header='''
<table border=1>
<tr>
<th>Package</th>
<th>Version</th>
<th>Short Explanation (click for details)</th>
'''

table_header_multi='''
<table border=1>
<tr>
<th>Package</th>
<th>Version</th>
<th>Archtectures</th>
<th>Short Explanation (click for details)</th>
'''

def build(t_this,t_prev,universe_this,scenario,arch):
    '''build a difference table between two runs'''

    if not (os.path.isfile (cachedir(t_prev,scenario,arch)+'/fg-packages')
            and os.path.isfile(cachedir(t_prev,scenario,arch)+'/summary')) :
        warning('skip diff for {s} on {a} from {t1} to {t2}'.format(
                s=scenario,a=arch,t1=t_prev,t2=t_this))
        
        return

    info('diff for {s} on {a} from {t1} to {t2}'.format(
            s=scenario,a=arch,t1=t_prev,t2=t_this))

    number_in_native=0
    number_in_archall=0
    number_out_native=0
    number_out_archall=0

    # ensure existence of output directory
    outdir=htmldir(t_this,scenario)
    if not os.path.isdir(outdir): os.makedirs(outdir)

    # fetch previous summary
    summary_prev = {}
    infilename=cachedir(t_prev,scenario,arch)+'/summary'
    if os.path.isfile(infilename):
        infile=open(infilename)
        for entry in infile:
            package,version,isnative,hash,explanation = entry.split('#')
            explanation = explanation.rstrip()
            summary_prev[package]={
                'version': version,
                'isnative': isnative=='True',
                'hash': hash,
                'explanation': explanation
                }
        infile.close()
    else:
        warning('{f} does not exist, skipping'.format(f=infilename))
                
    # fetch this summary
    summary_this = {}
    infilename=cachedir(t_this,scenario,arch)+'/summary'
    if os.path.isfile(infilename):
        infile=open(infilename)
        for entry in infile:
            package,version,isnative,hash,explanation = entry.split('#')
            explanation = explanation.rstrip()
            summary_this[package]={
                'version': version,
                'isnative': isnative=='True',
                'hash': hash,
                'explanation': explanation
                }
        infile.close()
    else:
        warning('{f} does not exist, skipping'.format(f=infilename))
    
    # fetch previous foreground
    infile=open(cachedir(t_prev,scenario,arch)+'/fg-packages')
    foreground_prev = { p.rstrip() for p in infile }
    infile.close()

    # reported uninstallable now
    uninstallables_this=set(summary_this.keys())

    # reported uninstallable previously
    uninstallables_prev=set(summary_prev.keys())
    
    # reported uninstallable now, but not previously
    uninstallables_in  = sorted(uninstallables_this - uninstallables_prev)

    # reported uninstallable previously, but not now
    uninstallables_out = sorted(uninstallables_prev - uninstallables_this)

    # write html page for differences
    outfile=open(outdir+'/'+arch+'-diff.html','w')
    print(html_header,file=outfile)
    print(diff_header.format(
            tthis=datetime.datetime.utcfromtimestamp(float(t_this)),
            tprev=datetime.datetime.utcfromtimestamp(float(t_prev)),
            arch=arch, scenario=scenario),
          file=outfile)
    
    print('<h2>Old packages that became not installable</h2>',file=outfile)
    # in uninstallable in, and in previous foreground
    print(table_header,file=outfile)
    for package in uninstallables_in:
        if package in foreground_prev:
            record=summary_this[package]
            if record['isnative']:
                all_mark=''
                number_in_native += 1
            else:
                all_mark='[all] '
                number_in_archall += 1
            print('<tr><td>',package,'</td>', file=outfile,sep='')
            print('<td>',all_mark,record['version'],'</td>',
                  file=outfile,sep='')
            print('<td>',pack_anchor(t_this,package,record['hash']),
                  record['explanation'],'</a>',
                  file=outfile, sep='')
    print('</table>',file=outfile)

    print('<h2>New packages that are not installable</h2>',file=outfile)
    # in uninstallable in, but not in previous foreground
    print(table_header,file=outfile)
    for package in uninstallables_in:
        if package not in foreground_prev:
            record=summary_this[package]
            if record['isnative']:
                all_mark=''
                number_in_native += 1
            else:
                all_mark='[all] '
                number_in_archall += 1
            print('<tr><td>',package,'</td>', file=outfile,sep='')
            print('<td>',all_mark,record['version'],'</td>',
                  file=outfile,sep='')
            print('<td>',pack_anchor(t_this,package,record['hash']),
                  record['explanation'],'</a>',
                  file=outfile, sep='')
    print('</table>',file=outfile)

    print('<h2>Old packages that became installable</h2>',file=outfile)
    # in uninstallable out, and in current foreground
    print(table_header,file=outfile)
    for package in uninstallables_out:
        if universe_this.is_in_foreground(package):
            record=summary_prev[package]
            if record['isnative']:
                all_mark=''
                number_out_native += 1
            else:
                all_mark='[all] '
                number_out_archall += 1
            print('<tr><td>',package,'</td>', file=outfile,sep='')
            print('<td>',all_mark,record['version'],'</td>',
                  file=outfile,sep='')
            print('<td>',pack_anchor(t_prev,package,record['hash']),
                  record['explanation'],'</a>',
                  file=outfile, sep='')
    print('</table>',file=outfile)

    print('<h2>Not-installable packages that disappeared</h2>',file=outfile)
    # in uninstallable out, but not in current foreground
    print(table_header,file=outfile)
    for package in uninstallables_out:
        if not universe_this.is_in_foreground(package):
            record=summary_prev[package]
            if record['isnative']:
                all_mark=''
                number_out_native += 1
            else:
                all_mark='[all] '
                number_out_archall += 1
            print('<tr><td>',package,'</td>', file=outfile,sep='')
            print('<td>',all_mark,record['version'],'</td>',
                  file=outfile,sep='')
            print('<td>',pack_anchor(t_prev,package,record['hash']),
                  record['explanation'],'</a>',
                  file=outfile, sep='')
    print('</table>',file=outfile)

    print(html_footer,file=outfile)
    outfile.close()

    # write size of the diff
    totaldiff=(number_in_native+number_in_archall-
               number_out_native-number_out_archall)
    if totaldiff>0:
        diffcolor='red'
    elif totaldiff<0:
        diffcolor='green'
    else:
        diffcolor='black'
    outfile=open(cachedir(t_this,scenario,arch)+'/number-diff', 'w')
    print('<font color={c}>+{innat}/{inall} -{outnat}/{outall}</font>'.format(
            innat=number_in_native,inall=number_in_archall,
            outnat=number_out_native,outall=number_out_archall,
            c=diffcolor),
          file=outfile)
    outfile.close()

#############################################################################

def build_multi(t_this,t_prev,scenario,what,architectures):
    '''build a difference table between two runs'''

    if not os.path.isfile(cachedir(t_prev,scenario,what)+'/summary'):
        warning('skip diff for {s} on {a} from {t1} to {t2}'.format(
                s=scenario,a=what,t1=t_prev,t2=t_this))
        return

    info('diff for {s} on {a} from {t1} to {t2}'.format(
            s=scenario,a=what,t1=t_prev,t2=t_this))

    number_in_native=0
    number_in_archall=0
    number_out_native=0
    number_out_archall=0

    # ensure existence of output directory
    outdir=htmldir(t_this,scenario)
    if not os.path.isdir(outdir): os.makedirs(outdir)

    # fetch previous summary
    summary_prev = {}
    infilename=cachedir(t_prev,scenario,what)+'/summary'
    if os.path.isfile(infilename):
        infile=open(infilename)
        for entry in infile:
            package,version,isnative,hash,explanation,archs = entry.split('#')
            explanation = explanation.rstrip()
            if package in summary_prev:
                summary_prev[package][hash]={'version': version,
                                             'isnative': isnative=='True',
                                             'explanation': explanation,
                                             'archs': archs
                                             }
            else:
                summary_prev[package]={hash:
                                           {'version': version,
                                            'isnative': isnative=='True',
                                            'explanation': explanation,
                                            'archs': archs
                                            }
                                       }
        infile.close()
    else:
        warning('{f} does not exist, skipping'.format(f=infilename))
                
    # fetch this summary
    summary_this = {}
    infilename=cachedir(t_this,scenario,what)+'/summary'
    if os.path.isfile(infilename):
        infile=open(infilename)
        for entry in infile:
            package,version,isnative,hash,explanation,archs = entry.split('#')
            explanation = explanation.rstrip()
            if package in summary_this:
                summary_this[package][hash]={
                    'version': version,
                    'isnative': isnative=='True',
                    'explanation': explanation,
                    'archs': archs
                    }
            else:
                summary_this[package]={hash:
                                           {'version': version,
                                            'isnative': isnative=='True',
                                            'explanation': explanation,
                                            'archs': archs
                                            }
                                       }
        infile.close()
    else:
        warning('{f} does not exist, skipping'.format(f=infilename))
    
    # fetch previous foreground
    foreground_prev=set()
    for arch in architectures:
        fg_file=cachedir(t_prev,scenario,arch)+'/fg-packages'
        if os.path.isfile(fg_file):
            with open(fg_file) as infile:
                for line in infile:
                    foreground_prev.add(line.rstrip())

    # fetch current foreground
    foreground_this=set()
    for arch in architectures:
        with open(cachedir(t_this,scenario,arch)+'/fg-packages') as infile:
            for line in infile:
                foreground_this.add(line.rstrip())


    uninstallables_this=set(summary_this.keys())
    uninstallables_prev=set(summary_prev.keys())

    uninstallables_in  = sorted(uninstallables_this - uninstallables_prev)
    uninstallables_out = sorted(uninstallables_prev - uninstallables_this)

    # write html page for differences
    outfile=open(outdir+'/'+what+'-diff.html','w')
    print(html_header,file=outfile)
    print(diff_header.format(
            tthis=datetime.datetime.utcfromtimestamp(float(t_this)),
            tprev=datetime.datetime.utcfromtimestamp(float(t_prev)),
            arch=what, scenario=scenario),
          file=outfile)
    
    print('<h2>Old packages that became not installable</h2>',file=outfile)
    print(table_header_multi,file=outfile)
    for package in uninstallables_in:
        if package in foreground_prev:
            print('<tr><td>',package,'</td>',sep='',file=outfile)
            continuation_line=False
            for hash in summary_this[package]:
                record=summary_this[package][hash]
                if record['isnative']:
                    all_mark=''
                    number_in_native += 1
                else:
                    all_mark='[all] '
                    number_in_archall += 1
                if continuation_line:
                    print('<tr><td></td>', file=outfile,sep='')
                print('<td>',all_mark,record['version'],'</td>',
                      file=outfile,sep='')
                print('<td>',record['archs'],'</td>',file=outfile,sep='')
                print('<td>',pack_anchor(t_this,package,hash),
                      record['explanation'],'</a>',
                      file=outfile, sep='')
                continuation_line=True
    print('</table>',file=outfile)


    print('<h2>New packages that are not installable</h2>',file=outfile)
    print(table_header_multi,file=outfile)
    for package in uninstallables_in:
        if package not in foreground_prev:
            print('<tr><td>',package,'</td>',sep='',file=outfile)
            continuation_line=False
            for hash in summary_this[package]:
                record=summary_this[package][hash]
                if record['isnative']:
                    all_mark=''
                    number_in_native += 1
                else:
                    all_mark='[all] '
                    number_in_archall += 1
                if continuation_line:
                    print('<tr><td></td>', file=outfile,sep='')
                print('<td>',all_mark,record['version'],'</td>',
                      file=outfile,sep='')
                print('<td>',record['archs'],'</td>',file=outfile,sep='')
                print('<td>',pack_anchor(t_this,package,hash),
                      record['explanation'],'</a>',
                      file=outfile, sep='')
                continuation_line=True
    print('</table>',file=outfile)


    print('<h2>Old packages that became installable</h2>',file=outfile)
    print(table_header_multi,file=outfile)
    for package in uninstallables_out:
        if package in foreground_this:
            print('<tr><td>',package,'</td>',sep='',file=outfile)
            continuation_line=False
            for hash in summary_prev[package]:
                record=summary_prev[package][hash]
                if record['isnative']:
                    all_mark=''
                    number_out_native += 1
                else:
                    all_mark='[all] '
                    number_out_archall += 1
                if continuation_line:
                    print('<tr><td></td>',file=outfile)
                print('<td>',all_mark,record['version'],'</td>',
                      file=outfile,sep='')
                print('<td>',record['archs'],'</td>',file=outfile,sep='')
                print('<td>',pack_anchor(t_prev,package,hash),
                      record['explanation'],'</a>',
                      file=outfile, sep='')
                continuation_line=True
    print('</table>',file=outfile)


    print('<h2>Not-installable packages that disappeared</h2>',file=outfile)
    print(table_header_multi,file=outfile)
    for package in uninstallables_out:
        if package not in foreground_this:
            print('<tr><td>',package,'</td>',sep='',file=outfile)
            continuation_line=False
            for hash in summary_prev[package]:
                record=summary_prev[package][hash]
                if record['isnative']:
                    all_mark=''
                    number_out_native += 1
                else:
                    all_mark='[all] '
                    number_out_archall += 1
                if continuation_line:
                    print('<tr><td></td>',file=outfile)
                print('<td>',all_mark,record['version'],'</td>',
                      file=outfile,sep='')
                print('<td>',record['archs'],'</td>',file=outfile,sep='')
                print('<td>',pack_anchor(t_prev,package,hash),
                      record['explanation'],'</a>',
                      file=outfile, sep='')
                continuation_line=True
    print('</table>',file=outfile)


    print(html_footer,file=outfile)
    outfile.close()

    # write size of the diff
    totaldiff=(number_in_native+number_in_archall-
               number_out_native-number_out_archall)
    if totaldiff>0:
        diffcolor='red'
    elif totaldiff<0:
        diffcolor='green'
    else:
        diffcolor='black'
    outfile=open(cachedir(t_this,scenario,what)+'/number-diff', 'w')
    print('<font color={c}>+{innat}/{inall} -{outnat}/{outall}</font>'.format(
            innat=number_in_native,inall=number_in_archall,
            outnat=number_out_native,outall=number_out_archall,
            c=diffcolor),
          file=outfile)
    outfile.close()
