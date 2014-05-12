# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import yaml,os, hashlib, datetime
from common import *

diff_header='''
<h1>Difference for {arch} in scenario {scenario}<h1>
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

def build(t_this,t_prev,scenario,arch):
    '''build a difference table between two runs'''

    info('diff for {s} on {a} from {t1} to {t2}'.format(
            s=scenario,a=arch,t1=t_prev,t2=t_this))

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

    # fetch current foreground
    infile=open(cachedir(t_this,scenario,arch)+'/fg-packages')
    foreground_this = { p.rstrip() for p in infile }
    infile.close()

    uninstallables_this=set(summary_this.keys())
    uninstallables_prev=set(summary_prev.keys())

    uninstallables_in  = sorted(uninstallables_this - uninstallables_prev)
    uninstallables_out = sorted(uninstallables_prev - uninstallables_this)

    # write html page for differences
    outfile=open(outdir+'/'+arch+'-diff.html','w')
    print(html_header,file=outfile)
    print(diff_header.format(
            tthis=datetime.datetime.utcfromtimestamp(float(t_this)),
            tprev=datetime.datetime.utcfromtimestamp(float(t_prev)),
            arch=arch, scenario=scenario),
          file=outfile)
    
    print('<h2>Packages that became not installable</h2>',file=outfile)
    print(table_header,file=outfile)
    for package in uninstallables_in:
        if package in foreground_prev:
            record=summary_this[package]
            all_mark = '' if record['isnative'] else '[all] '
            print('<tr><td>',package,'</td>', file=outfile,sep='')
            print('<td>',all_mark,record['version'],'</td>',
                  file=outfile,sep='')
            print('<td>',pack_anchor(t_this,package,record['hash']),
                  record['explanation'],'</a>',
                  file=outfile, sep='')
    print('</table>',file=outfile)

    print('<h2>New packages that are not installable</h2>',file=outfile)
    print(table_header,file=outfile)
    for package in uninstallables_in:
        if package not in foreground_prev:
            record=summary_this[package]
            all_mark = '' if record['isnative'] else '[all] '
            print('<tr><td>',package,'</td>', file=outfile,sep='')
            print('<td>',all_mark,record['version'],'</td>',
                  file=outfile,sep='')
            print('<td>',pack_anchor(t_this,package,record['hash']),
                  record['explanation'],'</a>',
                  file=outfile, sep='')
    print('</table>',file=outfile)

    print('<h2>Packages that became installable</h2>',file=outfile)
    print(table_header,file=outfile)
    for package in uninstallables_out:
        if package in foreground_this:
            record=summary_this[package]
            all_mark = '' if record['isnative'] else '[all] '
            print('<tr><td>',package,'</td>', file=outfile,sep='')
            print('<td>',all_mark,record['version'],'</td>',
                  file=outfile,sep='')
            print('<td>',pack_anchor(t_prev,package,record['hash']),
                  record['explanation'],'</a>',
                  file=outfile, sep='')
    print('</table>',file=outfile)

    print('<h2>Not-installable packages that disappeared</h2>',file=outfile)
    print(table_header,file=outfile)
    for package in uninstallables_in:
        if package in foreground_this:
            record=summary_this[package]
            all_mark = '' if record['isnative'] else '[all] '
            print('<tr><td>',package,'</td>', file=outfile,sep='')
            print('<td>',all_mark,record['version'],'</td>',
                  file=outfile,sep='')
            print('<td>',pack_anchor(t_prev,package,record['hash']),
                  record['explanation'],'</a>',
                  file=outfile, sep='')
    print('</table>',file=outfile)

    print(html_footer,file=outfile)
    outfile.close()
