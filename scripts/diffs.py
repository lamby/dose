# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import yaml,os, hashlib, datetime
import html
from common import *

def build(t_this,t_prev,universe_this,scenario,arch):
    '''build a difference table between two runs'''

    if not (os.path.isfile (cachedir(t_prev,scenario,arch)+'/fg-packages')
            and os.path.isfile(cachedir(t_prev,scenario,arch)+'/summary')) :
        warning('skip diff for {s} on {a} from {t1} to {t2}'.format(
                s=scenario,a=arch,t1=t_prev,t2=t_this))
        
        return

    info('diff for {s} on {a} from {t1} to {t2}'.format(
            s=scenario,a=arch,t1=t_prev,t2=t_this))

    counter_in = bicounter()
    counter_out = bicounter()

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
    html_diff=html.diff(t_this,t_prev,scenario,arch)
    
    html_diff.section('Old packages that became not installable')
    # in uninstallable in, and in previous foreground
    for package in uninstallables_in:
        if package in foreground_prev:
            record=summary_this[package]
            html_diff.write(package,record['isnative'],record['version'],
                            record['hash'],record['explanation'])
            counter_in.incr(record['isnative'])

    html_diff.section('New packages that are not installable')
    # in uninstallable in, but not in previous foreground
    for package in uninstallables_in:
        if package not in foreground_prev:
            record=summary_this[package]
            html_diff.write(package,record['isnative'],record['version'],
                            record['hash'],record['explanation'])
            counter_in.incr(record['isnative'])

    # from here on, explanations are to be found in the previous run
    html_diff.set_path_to_packages('../'+t_prev+'/packages/')

    html_diff.section('Old packages that became installable')
    # in uninstallable out, and in current foreground
    for package in uninstallables_out:
        if universe_this.is_in_foreground(package):
            record=summary_prev[package]
            html_diff.write(package,record['isnative'],record['version'],
                            record['hash'],record['explanation'])
            counter_out.incr(record['isnative'])

    html_diff.section('Not-installable packages that disappeared')
    # in uninstallable out, but not in current foreground
    for package in uninstallables_out:
        if not universe_this.is_in_foreground(package):
            record=summary_prev[package]
            html_diff.write(package,record['isnative'],record['version'],
                            record['hash'],record['explanation'])
            counter_out.incr(record['isnative'])

    del html_diff

    # write size of the diff
    totaldiff=counter_in.total() - counter_out.total()
    if totaldiff>0:
        diffcolor='red'
    elif totaldiff<0:
        diffcolor='green'
    else:
        diffcolor='black'
    outfile=open(cachedir(t_this,scenario,arch)+'/number-diff', 'w')
    print('<font color={c}>+{total_in} -{total_out}</font>'.format(
            total_in=str(counter_in),total_out=str(counter_out),c=diffcolor),
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

    # fetch previous summary
    summary_prev = {}
    infilename=cachedir(t_prev,scenario,what)+'/summary'
    if os.path.isfile(infilename):
        infile=open(infilename)
        for entry in infile:
            package,version,isnative,hash,explanation,archs = entry.split('#')
            explanation = explanation.rstrip()
            archs = archs.split()
            if package in summary_prev:
                summary_prev[package][hash]={'version': version,
                                             'isnative': isnative=='True',
                                             'short': explanation,
                                             'archs': archs
                                             }
            else:
                summary_prev[package]={hash:
                                           {'version': version,
                                            'isnative': isnative=='True',
                                            'short': explanation,
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
            archs = archs.split()
            if package in summary_this:
                summary_this[package][hash]={
                    'version': version,
                    'isnative': isnative=='True',
                    'short': explanation,
                    'archs': archs
                    }
            else:
                summary_this[package]={hash:
                                           {'version': version,
                                            'isnative': isnative=='True',
                                            'short': explanation,
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
    html_diff=html.diff_multi(t_this,t_prev,scenario,what)
    
    html_diff.section('Old packages that became not installable')
    # in uninstallable in, and in previous foreground
    for package in uninstallables_in:
        if package in foreground_prev:
            record=summary_this[package]
            firsthash=list(record.keys())[0]
            html_diff.write(package,record)
            if record[firsthash]['isnative']:
                number_in_native += 1
            else:
                number_in_archall += 1

    html_diff.section('New packages that are not installable')
    # in uninstallable in, but not in previous foreground
    for package in uninstallables_in:
        if package not in foreground_prev:
            record=summary_this[package]
            firsthash=list(record.keys())[0]
            html_diff.write(package,record)
            if record[firsthash]['isnative']:
                number_in_native += 1
            else:
                number_in_archall += 1

    # from here on, explanations are to be found in the previous run
    html_diff.set_path_to_packages('../'+t_prev+'/packages/')

    html_diff.section('Old packages that became installable')
    # in uninstallable out, and in current foreground
    for package in uninstallables_out:
        if package in foreground_this:
            record=summary_prev[package]
            firsthash=list(record.keys())[0]
            html_diff.write(package,record)
            if record[firsthash]['isnative']:
                number_out_native += 1
            else:
                number_out_archall += 1

    html_diff.section('Not-installable packages that disappeared')
    # in uninstallable out, but not in current foreground
    for package in uninstallables_out:
        if package not in foreground_this:
            record=summary_prev[package]
            firsthash=list(record.keys())[0]
            html_diff.write(package,record)
            if record[firsthash]['isnative']:
                number_out_native += 1
            else:
                number_out_archall += 1

    del html_diff

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
