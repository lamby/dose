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

import os, hashlib, datetime, re
import html, conf
from common import *

from yaml import load
try:
    from yaml import CBaseLoader as Loader
except ImportError:
    from yaml import BaseLoader as Loader
    warning('YAML C-library not available, falling back to python')

format_short_dep="unsatisfied dependency on {d}"
format_short_con="conflict between {c1} and {c2}"

#######################################################################
# remove a prefix p of length n from a string s, or a prefix 'src%3a'
def ccp(s,p,n):
    if s.startswith(p):
        return(s[n:])
    elif s.startswith('src%3a'):
        return(s[6:])
    elif s.startswith('src:'):
        return(s[4:])
    else:
        return(s)

##########################################################################
# hashing reasons

def freeze_recursive(structure,p,n):
    '''
    recursively transform dictionaries into hashable structures
    '''
    
    if isinstance(structure,list):
        return([freeze_recursive(x,p,n) for x in structure])
    elif isinstance(structure,dict):
        return( [ (key,freeze_recursive(structure[key],p,n)) 
                  for key in sorted(structure.keys ())
                  if not key in {'architecture', 'source', 'essential'} ])
    else:
        return(ccp(structure,p,n))

def hash_reasons(structure,p,n):
    '''
    return a hash of a set of reasons, abstracting from architecture.
    p is the architecture prefix from which we wish to abstract, n its length
    '''

    return(hashlib.md5(str(freeze_recursive(structure,p,n)).encode()).hexdigest())


########################################################################
# summaries of reasons

def summary_of_reason (reason,p,n):
    '''
    return a summary of one reason
    '''

    if 'missing' in reason:
        return(format_short_dep.format(
                d=ccp(reason['missing']['pkg']['unsat-dependency'],p,n)))
    elif 'conflict' in reason:
        return(format_short_con.format(
                c1=ccp(reason['conflict']['pkg1']['package'],p,n),
                c2=ccp(reason['conflict']['pkg2']['package'],p,n)))
    else:
        raise Exception('Unknown reason')

def summary_of_reasons (reasons,p,n):
    '''
    return a summary of a list of reasons
    '''
    
    head, *tail = reasons
    summary=summary_of_reason(head,p,n)
    for reason in tail:
        summary += '; ' + summary_of_reason(reason,p,n)
    return(summary)


#######################################################################
# detailed printing of reasons

def print_reason(root_package,root_version,scenario_type,
                 reason,outfile,universe,arch,bugtable,uninstallables):
    '''
    Detailed printing of reason why root_package (root_version) is
    not installable, in HTML to outfile.

    Each reason is either a missing dependency of one single package,
    or a conflict between two packages. There may exist multiple dependency
    chains from the root_package to the package with missing dependency, or
    to each of the conflicting packages. In case of a package conflict,
    there also may no dependency chain in case the conflciting package is
    essential.
    '''

    p=arch+':'
    n=len(p)
    
    def print_p(package,version,root_package):
        '''print a single package as part of a detailed explanation'''

        source=universe.source(package)
        source_version=universe.source_version(package)
        if not source_version: source_version = version

        if package in uninstallables and package != root_package:
            print('<a href={p}.html>{p}</a>'.format(p=package),
                  file=outfile,end=' ')
        else:
            print(package,file=outfile,end=' ')
        print('(',version,')',file=outfile,sep='')
        print('[<a href=https://tracker.debian.org/pkg/',source,'>PTS</a>]',
              file=outfile,sep='')
        print('[<a href=http://sources.debian.net/src/{s}/{v}/debian/control>ctrl</a>]'.format(s=source,v=source_version),file=outfile)
        bugtable.print_direct(package,source,root_package,outfile)
        print('<br>',file=outfile)

    def print_s(package,version):
        '''print a single source package (which must be the root)'''
        print('src:',package,file=outfile,sep='',end=' ')
        print('(',version,')',file=outfile,sep='')
        print('[<a href=https://packages.qa.debian.org/',package,'>PTS</a>]',
              file=outfile,sep='')
        print('[<a href=http://sources.debian.net/src/{s}/{v}/debian/control>ctrl</a>]'.format(s=package,v=version),file=outfile)
        bugtable.print_source(package,outfile)
        print('<br>',file=outfile)
        
    virtualdep_re=re.compile('\| --virtual-\S+\s*')
    def sanitize_d(dependency):
        '''drop --virtual-* packages, see upstream bug report #17736'''
        return(virtualdep_re.sub('',dependency))

    def print_d(dependency):
        '''print a dependency as part of a detailed explanation'''
        print('&nbsp;&nbsp;&nbsp;&darr;&nbsp;',
              ccp(sanitize_d(dependency),p,n),'<br>',
              file=outfile,sep='')

    def print_depchain(depchain):
        '''print a single dependency chain'''
    
        root_package=ccp(depchain['depchain'][0]['package'],p,n)
        firstiteration=True
        for member in depchain['depchain']:
            package=ccp(member['package'],p,n)
            if not firstiteration:
                print_p(package,member['version'],root_package)
            print_d(member['depends'])
            firstiteration=False

    def print_depchains(depchains):
        '''print multiple dependency chains'''

        if not depchains:
            return
        elif len(depchains) == 1:
            print_depchain(depchains[0])
        else:
            print('<table><tr>',file=outfile)
            for depchain in depchains:
                print('<td>',file=outfile)
                print_depchain(depchain)
                print('</td>',file=outfile)
            print('</tr></table>',file=outfile)

    print('<table>',file=outfile)
    if 'missing' in reason:
        last_package=ccp(reason['missing']['pkg']['package'],p,n)
        last_version=reason['missing']['pkg']['version']
        last_dependency=reason['missing']['pkg']['unsat-dependency']

        if root_package == last_package :
            # no dependency chain - the root package itself has an
            # unsatisfied dependency
            print('<tr><td>',file=outfile)
            if scenario_type == 'binary':
                print_p(root_package,root_version,root_package)
            elif scenario_type == 'source':
                print_s(root_package,root_version)
            else:
                warning('unknown scenario type: '+scenario_type)
            print_d(last_dependency)
            print('<font color=red>MISSING</font>',file=outfile)
            print('</td></tr>',file=outfile)
        else:
            depchains=reason['missing']['depchains']
            if len(depchains)==1 :
                # only one dependency chain
                print('<tr><td>',file=outfile)
                if scenario_type == 'binary':
                    print_p(root_package,root_version,root_package)
                elif scenario_type == 'source':
                    print_s(root_package,root_version)
                print_depchains(depchains)
                print_p(last_package,last_version,root_package)
                print_d(last_dependency)
                print('<font color=red>MISSING</font>',file=outfile)
                print('</td></tr>',file=outfile)
            else :
                # multiple dependency chains
                print('<tr><td style="text-align:center">',file=outfile)
                if scenario_type == 'binary':
                    print_p(root_package,root_version,root_package)
                elif scenario_type == 'source':
                    print_s(root_package,root_version)
                print('</td></tr><tr><td>',file=outfile)
                print_depchains(depchains)
                print('</td></tr><tr><td style="text-align:center">',
                      '<table><tr><td>',file=outfile,sep='')
                print_p(last_package,last_version,root_package)
                print_d(last_dependency)
                print('<font color=red>MISSING</font></td></tr></table>',
                      file=outfile)
    elif 'conflict' in reason:
        last_package1=ccp(reason['conflict']['pkg1']['package'],p,n)
        last_package2=ccp(reason['conflict']['pkg2']['package'],p,n)
        last_version1=reason['conflict']['pkg1']['version']
        last_version2=reason['conflict']['pkg2']['version']
        
        print('<tr><td style="text-align:center" colspan=2>',file=outfile)
        if scenario_type == 'binary':
            print_p(root_package,root_version,root_package)
        elif scenario_type == 'source':
            print_s(root_package,root_version)
        print('</td></tr>',file=outfile)
        print('<tr><td>',file=outfile)
        if 'depchain1' in reason['conflict']:
            print_depchains(reason['conflict']['depchain1'])
        print('</td><td>',file=outfile)
        if 'depchain2' in reason['conflict']:
            print_depchains(reason['conflict']['depchain2'])
        print('</td></tr>',file=outfile)
        print('<tr><td style="text-align:center">',file=outfile)
        print_p(last_package1,last_version1,root_package)
        print('</td><td style="text-align:center">',file=outfile)
        print_p(last_package2,last_version2,root_package)
        print('</td></tr><tr><td style="text-align:center" colspan=2>',
              file=outfile)
        print('<font color=red>CONFLICT</font></td></tr>',file=outfile)
    else:
        raise Exception('Unknown reason')
    print('</table>',file=outfile)


def create_reasons_file(package,version,scenario_type,reasons,reasons_summary,
                        outfile_name,universe,arch,bugtable,uninstallables):
    '''
    print to outfile_name the detailed explanation why (package,version) is
    not installable, according to reason.
    '''
    
    outfile=open(outfile_name, 'w')

    print('Summary: ',reasons_summary,'<p>',file=outfile)
    
    if len(reasons)==1:
        print_reason(package,version,scenario_type,reasons[0],outfile,
                     universe,arch,bugtable,uninstallables)
    else:
        print('Conjunction of multiple reasons:','<ol>',file=outfile)
        for reason in reasons:
            print('<li>',file=outfile)
            print_reason(package,version,scenario_type,reason,outfile,
                         universe,arch,bugtable,uninstallables)
        print('</ol>',file=outfile)

    outfile.close ()

#########################################################################
# top level 
def build(timestamp,day,universe,scenario,arch,bugtable,summary):
    '''
    summarize a complete output produced by dose-debcheck to outfilename,
    and prettyprint chunks of detailed explanations that do not yet exist in 
    the pool.
    '''

    daystamp=str(day)
    scenario_name=scenario['name']

    info('building report for {s} on {a}'.format(s=scenario_name,a=arch))

    # assure existence of output directories:
    histcachedir=history_cachedir(scenario_name)
    if not os.path.isdir(histcachedir): os.makedirs(histcachedir)
    pooldir = cachedir(timestamp,scenario_name,'pool')
    if not os.path.isdir(pooldir): os.makedirs(pooldir)

    # fetch the report obtained from dose-debcheck
    reportfile = open(cachedir(timestamp,scenario_name,arch)+'/debcheck.out')
    report = load(reportfile, Loader=Loader)
    reportfile.close()

    # fetch the history of packages
    histfile=history_cachefile(scenario_name,arch)
    history={}
    if os.path.isfile(histfile):
        h=open(histfile)
        for entry in h:
            package,date=entry.split('#')
            history[package] = date.rstrip()
        h.close()

    # HTML file object for the day and historical summaries
    html_today=html.summary(timestamp,scenario_name,arch,bugtable,
                            summary.get_total(arch))
    html_history={i:html.history(timestamp,scenario_name,arch,bugtable,d)
                  for i,d in conf.hlengths.items()}

    # a summary of the analysis in the cache directory
    sumfile = open(cachedir(timestamp,scenario_name,arch)+'/summary', 'w')

    # file recording the first day of observed non-installability per package
    historyfile=open(histfile,'w')

    # number of uninstallable arch=native/all packages per slice
    counter={i: bicounter() for i in conf.hlengths.keys()}

    if report and report['report']:
        p=arch+':'
        n=len(p)
        # set of names of not installable foreground packages 
        uninstallable_fg_packages={
            ccp(st['package'],p,n)
            for st in report['report']
            if universe.is_in_foreground(st['package'],st['version'])}
        for stanza in report['report']:
            package  = ccp(stanza['package'],p,n)
            version  = stanza['version']
            reasons  = stanza['reasons']
            isnative = stanza['architecture'] != 'all'
            all_mark = '' if isnative else '[all] '

            if not universe.is_in_foreground(package,version):
                # ignore packages that are not in the foreground, e.g. source
                # package with Extra-Source-Only set, or cruft packages.
                continue
    
            # create short and complete explanation, add complete
            # explanation to the corresponding file
            reasons_hash=hash_reasons(reasons,p,n)
            reasons_summary=summary_of_reasons(reasons,p,n)
            reasons_filename = pooldir + '/' + str(reasons_hash)
            if not os.path.isfile(reasons_filename):
                create_reasons_file(package,version,scenario['type'],
                                    reasons,reasons_summary,
                                    reasons_filename,universe,
                                    arch,bugtable,uninstallable_fg_packages)

            # write to html summary for that day
            html_today.write(package,isnative,version,
                               reasons_hash,reasons_summary)

            # write to the corresponding historic html page
            # and count archall/native uninstallable packages per slice
            if package in history:
                firstday=int(history[package])
                duration=day-firstday
                for i in sorted(conf.hlengths.keys(),reverse=True):
                    if duration >= conf.hlengths[i]:
                        html_history[i].write(package,isnative,version,
                                        reasons_hash,reasons_summary,
                                        since=date_of_days(firstday))
                        counter[i].incr(isnative)
                        break

            # write into the summary file in the cache
            print(package,version,isnative,reasons_hash,reasons_summary,
                  file=sumfile, sep='#')

            # rewrite the history file: for each file that is now not
            # installable, write the date found in the old history_cachefile
            # if it exists, otherwise write the current day.
            print(package,history.get(package,daystamp),
                  sep='#',
                  file=historyfile)

    del html_today
    for f in html_history.values(): del f
    sumfile.close ()
    historyfile.close ()
    summary.set_history_broken(arch,counter)

