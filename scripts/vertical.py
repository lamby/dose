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

def write_historytable(scenario,architectures,outfile):
    columns=architectures[:]
    columns.extend(['some','each'])
    print('<h2>Summary by duration</h2>',file=outfile)
    print('<table border=1><tr><th>Since</th>',file=outfile)
    for col in columns:
        print('<th>',col,'</th>',file=outfile,sep='')
    t={c:{i:'0/0' for i in conf.hlengths.keys()} for c in columns}
    for col in columns:
        if not os.path.isfile(history_verticalfile(scenario,col)):
            info('No history statistics for {a} in {s}'.format(
                    a=col,
                    s=scenario))
        else:
            infile=open(history_verticalfile(scenario,col))
            for entry in infile:
                key,value=entry.split('=')
                t[col][int(key)]=value.rstrip()
            infile.close()
    for i in conf.hlengths.keys():
        print('<tr><td>{d} days</td>'.format(d=conf.hlengths[i]),file=outfile)
        for col in columns:
            print('<td><a href=history/{a}/{d}.html>{nn}</a></td>'.format(
                    a=col,d=conf.hlengths[i],nn=t[col][i]),file=outfile)
        print('</tr>',file=outfile)
    print('</table>',file=outfile)


def write_table(timestamps,scenario,architectures):
    outfile=open(htmldir_scenario(scenario)+'/index.html', 'w')
    print(html.html_header,file=outfile)
    print(summary_header.format(scenario=scenario,
                                numberofslices=conf.slices),file=outfile)
    columns=architectures[:]
    columns.extend(['some','each'])
    for arch in columns:
        print('<th>',arch,'</th>',file=outfile,sep='')
    print('<tr><td>Today\'s Weather:</td>',file=outfile)
    for arch in columns:
        weatherfile=cachedir(timestamps[0],scenario,arch)+'/weather'
        if os.path.isfile(weatherfile):
            with open(weatherfile) as infile:
                weatherindex=int(infile.readline())
            print('<td align=center>',weather.icon(weatherindex),'</td>',
                  file=outfile,sep='')
        else:
            print('<td></td>',file=outfile)


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

    write_historytable(scenario,architectures,outfile)
    print('<p>',file=outfile)

    print(html.html_footer,file=outfile)
    outfile.close ()

###########################################################################
# top level

def build(timestamps,scenario,architectures):
    info('update vertical table for {s}'.format(s=scenario))
    write_table(timestamps,scenario,architectures)
