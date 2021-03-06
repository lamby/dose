# Copyright (C) 2014,2015 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

############################################################################
# please push all changes to the git repository, otherwise they might get  #
# overwritten:    git+ssh://git.debian.org/git/qa/dose.git                 #
############################################################################

import os
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
            package,version,isnative_string,hash,short = entry.split('#')
            short = short.rstrip()
            summary_prev[package]={
                'version': version,
                'isnative': isnative_string=='True',
                'hash': hash,
                'short': short
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
            package,version,isnative_string,hash,short = entry.split('#')
            short = short.rstrip()
            summary_this[package]={
                'version': version,
                'isnative': isnative_string=='True',
                'hash': hash,
                'short': short
                }
        infile.close()
    else:
        warning('{f} does not exist, skipping'.format(f=infilename))
    
    # fetch previous foreground
    infile=open(cachedir(t_prev,scenario,arch)+'/fg-packages')
    foreground_prev = { p.rstrip() for p in infile }
    infile.close()

    uninstallables_this=set(summary_this.keys())
    uninstallables_prev=set(summary_prev.keys())
    
    uninstallables_in  = uninstallables_this - uninstallables_prev
    uninstallables_out = uninstallables_prev - uninstallables_this

    # write html page for differences
    html_diff=html.diff(t_this,t_prev,scenario,arch)
    
    # in uninstallable in, and in previous foreground
    uninstallables_in_old=uninstallables_in & foreground_prev
    if len(uninstallables_in_old) > 0:
        html_diff.section('Old packages that became not installable')
        for package in sorted(uninstallables_in_old):
            record=summary_this[package]
            html_diff.write_record(package,record)
            counter_in.incr(record['isnative'])

    # in uninstallable in, but not in previous foreground
    uninstallables_in_new=uninstallables_in - foreground_prev
    if len(uninstallables_in_new) > 0:
        html_diff.section('New packages that are not installable')
        for package in sorted(uninstallables_in_new):
            record=summary_this[package]
            html_diff.write(package,record)
            counter_in.incr(record['isnative'])

    # from here on, explanations are to be found in the previous run
    html_diff.set_path_to_packages('../'+t_prev+'/packages/')

    # in uninstallable out, and in current foreground
    uninstallables_out_kept={p for p in uninstallables_out
                             if universe_this.is_in_foreground_someversion(p)}
    if len(uninstallables_out_kept) > 0:
        html_diff.section('Old packages that became installable')
        for package in sorted(uninstallables_out_kept):
            record=summary_prev[package]
            html_diff.write(package,record)
            counter_out.incr(record['isnative'])

    # in uninstallable out, but not in current foreground
    uninstallables_out_removed={p for p in uninstallables_out
                         if not universe_this.is_in_foreground_someversion(p)}
    if len(uninstallables_out_removed) > 0:
        html_diff.section('Not-installable packages that disappeared')
        for package in sorted(uninstallables_out_removed):
            record=summary_prev[package]
            html_diff.write(package,record)
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

def build_multi(t_this,t_prev,scenario,what,summary):
    '''build a difference table between two runs'''

    if not os.path.isfile(cachedir(t_prev,scenario,what)+'/summary'):
        warning('skip diff for {s} on {a} from {t1} to {t2}'.format(
                s=scenario,a=what,t1=t_prev,t2=t_this))
        return

    info('diff for {s} on {a} from {t1} to {t2}'.format(
            s=scenario,a=what,t1=t_prev,t2=t_this))

    counter_in = bicounter_multi()
    counter_out = bicounter_multi()

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
    for arch in summary.get_architectures():
        fg_file=cachedir(t_prev,scenario,arch)+'/fg-packages'
        if os.path.isfile(fg_file):
            with open(fg_file) as infile:
                for line in infile:
                    foreground_prev.add(line.rstrip())

    # fetch current foreground
    foreground_this=set()
    for arch in summary.get_architectures():
        with open(cachedir(t_this,scenario,arch)+'/fg-packages') as infile:
            for line in infile:
                foreground_this.add(line.rstrip())


    uninstallables_this=set(summary_this.keys())
    uninstallables_prev=set(summary_prev.keys())

    uninstallables_in  = uninstallables_this - uninstallables_prev
    uninstallables_out = uninstallables_prev - uninstallables_this

    # write html page for differences
    html_diff=html.diff_multi(t_this,t_prev,scenario,what)
    
    # in uninstallable in, and in previous foreground
    uninstallables_in_old = uninstallables_in & foreground_prev
    if len(uninstallables_in_old) > 0:
        html_diff.section('Old packages that became not installable')
        for package in sorted(uninstallables_in_old):
            record=summary_this[package]
            html_diff.write(package,record)
            counter_in.incr(record)

    # in uninstallable in, but not in previous foreground
    uninstallables_in_new = uninstallables_in - foreground_prev
    if len(uninstallables_in_new) > 0:
        html_diff.section('New packages that are not installable')
        for package in sorted(uninstallables_in_new):
            record=summary_this[package]
            html_diff.write(package,record)
            counter_in.incr(record)

    # from here on, explanations are to be found in the previous run
    html_diff.set_path_to_packages('../'+t_prev+'/packages/')

    # in uninstallable out, and in current foreground
    uninstallables_out_kept = uninstallables_out & foreground_this
    if len(uninstallables_out_kept) > 0:
        html_diff.section('Old packages that became installable')
        for package in sorted(uninstallables_out_kept):
            record=summary_prev[package]
            html_diff.write(package,record)
            counter_out.incr(record)

    # in uninstallable out, but not in current foreground
    uninstallables_out_removed = uninstallables_out - foreground_this
    if len(uninstallables_out_removed) > 0:
        html_diff.section('Not-installable packages that disappeared')
        for package in sorted(uninstallables_out_removed):
            record=summary_prev[package]
            html_diff.write(package,record)
            counter_out.incr(record)

    del html_diff

    # write size of the diff
    totaldiff=counter_in.total() - counter_out.total()
    if totaldiff>0:
        diffcolor='red'
    elif totaldiff<0:
        diffcolor='green'
    else:
        diffcolor='black'
    outfile=open(cachedir(t_this,scenario,what)+'/number-diff', 'w')
    print('<font color={c}>+{total_in} -{total_out}</font>'.format(
        total_in=str(counter_in),total_out=str(counter_out),c=diffcolor),
          file=outfile)
    outfile.close()
