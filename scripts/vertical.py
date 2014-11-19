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
import weather, html, conf
from common import *

summary_header = '''
<h1>Packages not installable in scenario {scenario}</h1>

In a pair <i>n/m</i>,
<i>n</i> is the number of packages that are build for that architecture,
<i>m</i> is the number of packages with <kbd>Architecture=all</kbd>.
<p>
<h2>Summary for the last {numberofslices} days</h2>
<table border=1>
<tr>
<th>Date</th>
'''

def write_historytable(scenario,architectures,summary,outfile):
    columns=architectures[:]
    columns.extend(['some','each'])
    print('<h2>Summary by duration</h2>',file=outfile)
    print('<table border=1><tr><th>Since</th>',file=outfile)
    for col in columns:
        print('<th>',col,'</th>',file=outfile,sep='')
    for i in conf.hlengths.keys():
        print('<tr><td>{d} days</td>'.format(d=conf.hlengths[i]),file=outfile)
        for col in columns:
            print('<td><a href=history/{a}/{d}.html>{nn}</a></td>'.format(
                    a=col,d=conf.hlengths[i],
                    nn=str(summary.get_history_broken(col)[i])),
                  file=outfile)
        print('</tr>',file=outfile)
    print('</table>',file=outfile)


def write_table(timestamps,scenario,summary):
    outfile=open(htmldir_scenario(scenario)+'/index.html', 'w')
    print(html.html_header,file=outfile)
    print(summary_header.format(scenario=scenario,
                                numberofslices=conf.slices),file=outfile)
    architectures=summary.get_architectures()
    columns=architectures[:]
    columns.extend(['some','each'])
    for architecture in columns:
        print('<th>',architecture,'</th>',file=outfile,sep='')

    print('<tr><td>Today\'s Weather:</td>',file=outfile)
    for architecture in columns:
        print('<td align=center>',
              weather.icon_of_percentage(summary.get_percentage(architecture)),
              '</td>',
              file=outfile,sep='')

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
        if timestamp != timestamps[-1]:
            # dont print a diff for the last line
            print('<tr><td>Diff</td>',file=outfile)
            for arch in columns:
                dfn=cachedir(timestamp,scenario,arch)+'/number-diff'
                if os.path.isfile(dfn):
                    with open(dfn) as infile:
                        line=infile.readline()
                    line.rstrip()
                    print('<td><a href="{t}/{a}-diff.html">{c}<a/></td>'.format(
                            t=timestamp,a=arch,c=line),
                          sep='',file=outfile)
                else:
                    print('<td>N/A</td>',file=outfile)
    print('</table>',file=outfile)

    write_historytable(scenario,architectures,summary,outfile)
    print('<p>',file=outfile)

    print(html.html_footer,file=outfile)
    outfile.close ()

###########################################################################
# top level

def build(timestamps,scenario,summary):
    info('update vertical table for {s}'.format(s=scenario))
    write_table(timestamps,scenario,summary)
