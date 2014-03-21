# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import yaml,os, hashlib, datetime
from common import *


format_short_dep="missing dependency on {d}"
format_short_con="conflict between {c1} and {c2}"

format_long_dep='<li>No package matches the dependency <i>{d}</i> of package {p} (={v})<br>.'
format_long_con='<li>Conflict between package {c1} (={v1}) and package {c2} (={v2})<br>.'

format_depchain='Dependency chain from {sp} (={sv}) to {tp} (={tv}):'
format_depchains='Multiple dependency chains from {sp} (={sv}) to {tp} (={tv}):'


##########################################################################
# hashing reasons

def freeze_recursive(structure):
    '''
    recursively transform dictionaries into hashable structures
    '''
    
    if isinstance(structure,list):
        return([freeze_recursive(x) for x in structure])
    elif isinstance(structure,dict):
        return( [ (key,freeze_recursive(structure[key])) 
                  for key in sorted(structure.keys ())
                  if not key in {'architecture', 'source', 'essential'} ])
    else:
        return(structure)

def freeze_depchain(depchain):
    '''
    freeze a dependency chain. We only keep package, version, and dependency
    '''

    if depchain is None:
        return(None)
    else:
        return( [ ( x['package'],x['version'],x['depends'] )
                            for x in depchain ])

def hash_reasons(structure):
    '''
    return a hash of a set of reasons, abstracting from architecture
    '''

    return(hashlib.md5(str(freeze_recursive(structure)).encode()).hexdigest())


########################################################################
# summaries of reasons

def summary_of_reason (reason):
    '''
    return a summary of one reason
    '''

    if 'missing' in reason:
        return(format_short_dep.format(
                d=reason['missing']['pkg']['unsat-dependency']))
    elif 'conflict' in reason:
        return(format_short_con.format(
                c1=reason['conflict']['pkg1']['package'],
                c2=reason['conflict']['pkg2']['package']))
    else:
        raise Exception('Unknown reason')

def summary_of_reasons (reasons):
    '''
    return a summary of a list of reasons
    '''
    
    head, *tail = reasons
    summary=summary_of_reason(head)
    for reason in tail:
        summary += '; ' + summary_of_reason(reason)
    return(summary)


#######################################################################
# detailed printing of reasons

def print_reason (package,version,reason,outfile):
    '''
    detailed printing of one reason in html to a file
    '''

    if 'missing' in reason:
        print(format_long_dep.format(
                d=reason['missing']['pkg']['unsat-dependency'],
                p=reason['missing']['pkg']['package'],
                v=reason['missing']['pkg']['version']),
              file=outfile)
        if 'depchains' in reason['missing']:
            print_depchains(package,version,
                            reason['missing']['pkg']['package'],
                            reason['missing']['pkg']['version'],
                            reason['missing']['depchains'],
                            outfile)
    elif 'conflict' in reason:
        print(format_long_con.format(
                c1=reason['conflict']['pkg1']['package'],
                v1=reason['conflict']['pkg1']['version'],
                c2=reason['conflict']['pkg2']['package'],
                v2=reason['conflict']['pkg2']['version']),
              file=outfile)
        if 'depchain1' in reason['conflict']:
            print_depchains(package,version,
                            reason['conflict']['pkg1']['package'],
                            reason['conflict']['pkg1']['version'],
                            reason['conflict']['depchain1'],
                            outfile)
        if 'depchain2' in reason['conflict']:
            print_depchains(package,version,
                            reason['conflict']['pkg2']['package'],
                            reason['conflict']['pkg2']['version'],
                            reason['conflict']['depchain2'],
                            outfile)
    else:
        raise Exception('Unknown reason')

def print_depchain(depchain, outfile):
    '''
    print a single dependency chain to a file
    '''
    
    print('<ol>',file=outfile)
    for member in depchain['depchain']:
        print('<li>Package {p} (={v}) depends on {d}'.format(
                p=member['package'],v=member['version'],d=member['depends']),
              file=outfile)
    print('</ol>',file=outfile)

def print_depchains(source_package,source_version,
                    target_package,target_version,
                    depchains,outfile):
    '''
    print one or several dependency chains between two given packages
    '''

    if not depchains:
        info('no depchains for package {p}, version {v}'.format(
                p=source_package,
                v=source_version))
    elif len(depchains) == 1:
        print(format_depchain.format(
                sp=source_package,sv=source_version,
                tp=target_package,tv=target_version),
              file=outfile)
        print_depchain(depchains[0],outfile)
    else:
        print(format_depchains.format(
                sp=source_package,sv=source_version,
                tp=target_package,tv=target_version),
              file=outfile)
        print('<ol>',file=outfile)
        for depchain in depchains:
            print('<li>',file=outfile)
            print_depchain(depchain,outfile)
        print('</ol>',file=outfile)


def create_reasons_file(package, version, reasons, outfile_name):
    '''
    print to outfile_name the detailed explanation why (package,version) is
    not installable, according to reason.
    '''
    
    outfile=open(outfile_name, 'w')

    print('<b>Version: {v}</b>'.format(v=version), file=outfile)
    print('<ol>',file=outfile)
    for reason in reasons:
        print_reason(package,version,reason,outfile)
    print('</ol>',file=outfile)

    outfile.close ()


summary_header = '''
<h1>Packages not installable on {arch} in scenario {scenario}</h1>
<b>Date: {utctime} UTC</b>
<p>
<table border=1>
<tr>
<th>Package</th>
<th>Version</th>
<th>Short explanation (click for detailed explanation)</th>
'''

#########################################################################
# top level 

def build(timestamp,scenario,arch):
    '''
    summarize a complete output produced by dose-debcheck to outfilename,
    and prettyprint chunks of detailed explanations that do not yet exist in 
    the pool.
    '''

    info('building report for {s} on {a}'.format(s=scenario,a=arch))

    # the directory where we store chunks of explanations
    pooldir = cachedir(timestamp,scenario,'pool')
    if not os.path.isdir(pooldir): os.mkdir(pooldir)

    # the report obtained from dose-debcheck
    reportfile = open(cachedir(timestamp,scenario,arch)+'/debcheck.out')
    report= yaml.load(reportfile)
    reportfile.close()

    # html output: a summary for this architecture
    outdir=htmldir(timestamp,scenario)
    if not os.path.isdir(outdir): os.makedirs(outdir)
    outfile = open(outdir+'/'+arch+'.html', 'w')
    print(html_header,file=outfile)
    print(summary_header.format(
            timestamp=str(timestamp),
            scenario=scenario,
            arch=arch,
            utctime=datetime.datetime.utcfromtimestamp(float(timestamp))),
          file=outfile)

    # a summary of the analysis in the cache directory
    sumfile = open(cachedir(timestamp,scenario,arch)+'/summary', 'w')

    if report['report']:
        for stanza in report['report']:
            package  = stanza['package']
            version  = stanza['version']
            reasons  = stanza['reasons']
            isnative = stanza['architecture'] != 'all'
            all_mark = '' if isnative else '[all]'
            print('<tr><td>',all_mark,package,'</td>', file=outfile,sep='')
            print('<td>',version,'</td>', file=outfile,sep='')
            reasons_hash=hash_reasons(reasons)
            reasons_summary=summary_of_reasons(reasons)
            reasons_filename = pooldir + '/' + str(reasons_hash)
            if not os.path.isfile(reasons_filename):
                create_reasons_file(package,version,reasons,reasons_filename)
            print('<td>',pack_anchor(timestamp,package,reasons_hash),
                  reasons_summary,'</a>',
                  file=outfile, sep='')
            print(package,version,isnative,reasons_hash,reasons_summary,
                  file=sumfile, sep='#')
        print("</table>", file=outfile)

    print(html_footer,file=outfile)
    outfile.close ()
    sumfile.close ()
