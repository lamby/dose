# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

'''
Generation of html pages for stuff that requires accumulation over 
different timestamps.
- constructing a summary page for the last timestamps
'''
import os.path
from common import *

summary_header = '''
<h1>Summary of packages not installable in scenario {scenario}</h1>

In a pair <i>n/m</i>,
<i>n</i> is the number of packages that are build for that architecture,
<i>m</i> is the number of packages with <kbd>Architecture=all</kbd>.
<p>
<h2>Results for the last {numberofslices} days</h2>
<table border=1>
<tr>
<th>Date</th>
'''

def write_historytable(scenario,architectures,outfile):
    print('<h2>Summary by duration of non-installability</h2>',file=outfile)
    print('<table border=1><tr><th>Since</th>',file=outfile)
    for arch in architectures:
        print('<th>',arch,'</th>',file=outfile,sep='')
    t={a:{i:'0/0' for i in hlengths.keys()} for a in architectures}
    for arch in architectures:
        if not os.path.isfile(history_verticalfile(scenario,arch)):
            info('No history statistics for {a} in {s}'.format(
                    a=arch,
                    s=scenario))
        else:
            infile=open(history_verticalfile(scenario,arch))
            for entry in infile:
                key,value=entry.split('=')
                t[arch][int(key)]=value.rstrip()
            infile.close()
    for i in hlengths.keys():
        print('<tr><td>{d} days</td>'.format(d=hlengths[i]),file=outfile)
        for arch in architectures:
            print('<td><a href=history/{a}/{d}.html>{nn}</a></td>'.format(
                    a=arch,d=hlengths[i],nn=t[arch][i]),file=outfile)
        print('</tr>',file=outfile)
    print('</table>',file=outfile)


def write_table(timestamps,scenario,architectures):
    outfile=open(htmldir_scenario(scenario)+'/index.html', 'w')
    print(html_header,file=outfile)
    print(summary_header.format(scenario=scenario,
                                numberofslices=conf.slices),file=outfile)
    for arch in architectures:
        print('<th>',arch,'</th>',file=outfile,sep='')
    print('<th>some</th><th>each</th></tr>',file=outfile)
    for timestamp in timestamps:
        if not os.path.isfile(cachedir(timestamp,scenario,'summary')+'/row'):
            info('Dropping timestamp {t} from vertical table for {s}'.format(
                    t=timestamp,
                    s=scenario))
            continue
        infile=open(cachedir(timestamp,scenario,'summary')+'/row')
        contents={}
        for entry in infile:
            key,value=entry.split('=')
            contents[key]=value
        infile.close()
        print('<tr><td>',contents['date'],'</td>',file=outfile)
        for arch in architectures:
            print('<td><a href="{t}/{a}.html">{c}</a>'.format(
                    t=timestamp,
                    a=arch,
                    c=contents.get(arch,'')),file=outfile)
        for arch in ['some','each']:
            print('<td><a href="{t}/{a}.html">{c}</a>'.format(
                    t=timestamp,
                    a=arch,
                    c=contents.get(arch,'')),file=outfile)
    print('</table>',file=outfile)

    write_historytable(scenario,architectures,outfile)

    print(html_footer,file=outfile)
    outfile.close ()

###########################################################################
# top level

def build(timestamps,scenario,architectures):
    info('update vertical table for {s}'.format(s=scenario))
    write_table(timestamps,scenario,architectures)
