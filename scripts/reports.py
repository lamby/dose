# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import yaml,os, hashlib, datetime
from common import *



format_short_dep="unsatisfied dependency on {d}"
format_short_con="conflict between {c1} and {c2}"

format_long_dep='<li>No package matches the dependency <i>{d}</i> of package {p} (={v})'
format_long_con='<li>Conflict between package {c1} (={v1}) and package {c2} (={v2})'

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

def print_reason(root_package,root_version,
                 reason,outfile,universe,bugtable):
    '''
    detailed printing of one reason in html to a file
    '''

    root_source=universe.source(root_package)

    if 'missing' in reason:
        last_package=reason['missing']['pkg']['package']
        last_version=reason['missing']['pkg']['version']
        last_source=universe.source(last_package)

        print('<table><tr><td align=center>',file=outfile)
        print(root_package,' (',root_version,') ',file=outfile)
        bugtable.print_direct(root_package,root_source,root_package,outfile)
        print('<tr><td>',file=outfile)
        if 'depchains' in reason['missing']:
            print_depchains(root_package,root_version,
                            reason['missing']['pkg']['package'],
                            reason['missing']['pkg']['version'],
                            reason['missing']['depchains'],
                            outfile,universe,bugtable)
        print('<tr><td align=center><table><tr><td>',file=outfile)
        print(last_package, '(',last_version,') ',file=outfile)
        bugtable.print_direct(last_package,last_source,root_package,outfile)
        print('<tr><td>&nbsp;&nbsp;&nbsp;&darr;',
              reason['missing']['pkg']['unsat-dependency'],
              file=outfile)
        print('<tr><td><font color=red>MISSING</font></td></tr></table>',
              '</table>',file=outfile)
    elif 'conflict' in reason:
        lastpkg1=reason['conflict']['pkg1']['package']
        lastpkg2=reason['conflict']['pkg2']['package']
        lastsrc1=universe.source(lastpkg1)
        lastsrc2=universe.source(lastpkg2)
        print(format_long_con.format(
                c1=lastpkg1,
                v1=reason['conflict']['pkg1']['version'],
                c2=lastpkg2,
                v2=reason['conflict']['pkg2']['version']),
              file=outfile)
        bugtable.print_direct(lastpkg1,lastsrc1,root_package,outfile)
        bugtable.print_direct(lastpkg2,lastsrc2,root_package,outfile)
        print('<br>',file=outfile)
        if 'depchain1' in reason['conflict']:
            print_depchains(root_package,root_version,
                            lastpkg1,
                            reason['conflict']['pkg1']['version'],
                            reason['conflict']['depchain1'],
                            outfile,universe,bugtable)
        if 'depchain2' in reason['conflict']:
            print_depchains(root_package,root_version,
                            lastpkg2,
                            reason['conflict']['pkg2']['version'],
                            reason['conflict']['depchain2'],
                            outfile,universe,bugtable)
    else:
        raise Exception('Unknown reason')

def print_depchain(depchain,outfile,universe,bugtable):
    '''
    print a single dependency chain to a file
    '''
    
    print('<table border=0>',file=outfile)
    root_package=depchain['depchain'][0]['package']
    firstiteration=True
    for member in depchain['depchain']:
        package=member['package']
        if not firstiteration:
            print('<tr><td>',package,' (',member['version'],')',file=outfile)
            bugtable.print_direct(package,universe.source(package),root_package,
                                  outfile)
            print('</td></tr>',file=outfile)
        print('<tr><td>&nbsp;&nbsp;&nbsp;&darr; ',member['depends'],
              '</td></tr>',file=outfile)
        firstiteration=False
    print('</table>',file=outfile)

def print_depchains(source_package,source_version,
                    target_package,target_version,
                    depchains,outfile,universe,bugtable):
    '''
    print one or several dependency chains between two given packages
    '''

    if not depchains:
        info('no depchains for package {p}, version {v}'.format(
                p=source_package,
                v=source_version))
    elif len(depchains) == 1:
        print_depchain(depchains[0],outfile,universe,bugtable)
    else:
        print('<table>',file=outfile)
        for depchain in depchains:
            print('<td>',file=outfile)
            print_depchain(depchain,outfile,universe,bugtable)
            print('</td>',file=outfile)
        print('</table>',file=outfile)


def create_reasons_file(package,version,reasons,outfile_name,
                        universe,bugtable):
    '''
    print to outfile_name the detailed explanation why (package,version) is
    not installable, according to reason.
    '''
    
    outfile=open(outfile_name, 'w')

    print('<b>Version: {v}</b>'.format(v=version), file=outfile)
    print('<ol>',file=outfile)
    for reason in reasons:
        print_reason(package,version,reason,outfile,universe,bugtable)
    print('</ol>',file=outfile)

    outfile.close ()


summary_history_header = '''
<h1>Packages not installable on {arch} in scenario {scenario}
for {d} days</h1>
<b>Date: {utctime} UTC</b>
<p>

Packages that have been continuously found to be not installable
(not necessarily in the same version, and not necessarily with the
same explanation all the time).<p>
<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
<p>
<table border=1>
<tr>
<th>Package</th>
<th>Since</th>
<th>Version today</th>
<th>Short explanation as of today (click for details)</th>
<th>Tracking</th>
'''


########################################################################

class Summary_HTML:
    """
    A file object containg an html table of packages that are not
    installable in a certain scenario, architecture, on a certain
    date.
    """

    summary_header = '''
<h1>Packages not installable on {architecture} in scenario {scenario}</h1>
<b>Date: {utctime} UTC</b>
<p>

<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
<p>
<table border=1>
<tr>
<th>Package</th>
<th>Version</th>
<th>Short explanation (click for detailed explanation)</th>
<th>Tracking</th>
'''
    
    def __init__(self,timestamp,scenario,architecture,bugtable):
        """
        open the html file and print the header
        """
        outdir=htmldir(timestamp,scenario)
        if not os.path.isdir(outdir): os.makedirs(outdir)
        self.bugtable=bugtable
        self.timestamp=timestamp
        self.filedesc = open(outdir+'/'+architecture+'.html', 'w')
        print(html_header,file=self.filedesc)
        print(self.summary_header.format(
            timestamp=str(timestamp),
            scenario=scenario,
            architecture=architecture,
            utctime=datetime.datetime.utcfromtimestamp(float(timestamp))),
        file=self.filedesc)

    def __del__(self):
        """
        print the html footer stuff and close the html file
        """
        print('</table>',html_footer,file=self.filedesc,sep='\n')
        self.filedesc.close()

    def write(self,package,isnative,version,reasons_hash,reasons_summary):
        """
        write one line of a summary table
        """
        all_mark = '' if isnative else '[all] '  
        print('<tr><td>',package,'</td>',
              '<td>',all_mark,version,'</td>',
              '<td>',pack_anchor(self.timestamp,package,reasons_hash),
              reasons_summary,'</a></td><td>',
              file=self.filedesc, sep='')
        self.bugtable.print_indirect(package,self.filedesc)
        print('</td></tr>',file=self.filedesc)

#########################################################################
# top level 
def build(timestamp,day,universe,scenario,arch,bugtable):
    '''
    summarize a complete output produced by dose-debcheck to outfilename,
    and prettyprint chunks of detailed explanations that do not yet exist in 
    the pool.
    '''

    daystamp=str(day)

    info('building report for {s} on {a}'.format(s=scenario,a=arch))

    # assure existence of output directories:
    histcachedir=history_cachedir(scenario)
    if not os.path.isdir(histcachedir): os.makedirs(histcachedir)
    pooldir = cachedir(timestamp,scenario,'pool')
    if not os.path.isdir(pooldir): os.makedirs(pooldir)
    histhtmldir=history_htmldir(scenario,arch)
    if not os.path.isdir(histhtmldir): os.makedirs(histhtmldir)


    # fetch the report obtained from dose-debcheck
    reportfile = open(cachedir(timestamp,scenario,arch)+'/debcheck.out')
    report = yaml.load(reportfile)
    reportfile.close()

    # fetch the history of packages
    histfile=history_cachefile(scenario,arch)
    history={}
    if os.path.isfile(histfile):
        h=open(histfile)
        for entry in h:
            package,date=entry.split('#')
            history[package] = date.rstrip()
        h.close()

    summary_file=Summary_HTML(timestamp,scenario,arch,bugtable)

    # historic html files for different time slices
    hfiles={i:open(history_htmlfile(scenario,arch,d),'w')
            for i,d in hlengths.items()}
    for i in hfiles.keys():
        print(html_header,file=hfiles[i])
        print(summary_history_header.format(
                timestamp=str(timestamp),
                scenario=scenario,
                arch=arch,
                d=hlengths[i],
                utctime=datetime.datetime.utcfromtimestamp(float(timestamp))),
              file=hfiles[i])

    # a summary of the analysis in the cache directory
    sumfile = open(cachedir(timestamp,scenario,arch)+'/summary', 'w')

    # file recording the first day of observed non-installability per package
    historyfile=open(histfile,'w')

    # number of uninstallable arch=all packages per slice
    count_archall={i:0 for i in hlengths.keys()}
    # number of uninstallable native packages per slice
    count_natives={i:0 for i in hlengths.keys()}

    if report and report['report']:
        for stanza in report['report']:
            package  = stanza['package']
            version  = stanza['version']
            reasons  = stanza['reasons']
            isnative = stanza['architecture'] != 'all'
            all_mark = '' if isnative else '[all] '
    
            # create short and complete explanation, add complete
            # explanation to the corresponding file
            reasons_hash=hash_reasons(reasons)
            reasons_summary=summary_of_reasons(reasons)
            reasons_filename = pooldir + '/' + str(reasons_hash)
            if not os.path.isfile(reasons_filename):
                create_reasons_file(package,version,reasons,reasons_filename,
                                    universe,bugtable)

            # write to html summary for that day
            summary_file.write(package,isnative,version,
                               reasons_hash,reasons_summary)

            # write to the corresponding historic html page
            # and count archall/native uninstallable packages per slice
            if package in history:
                firstday=int(history[package])
                duration=day-firstday
                for i in sorted(hlengths.keys(),reverse=True):
                    if duration >= hlengths[i]:
                        if isnative:
                            count_natives[i] += 1
                        else:
                            count_archall[i] += 1
                        print('<tr><td>',package,'</td>',file=hfiles[i],sep='')
                        print('<td>',date_of_days(firstday),'</td>',
                              file=hfiles[i],sep="")
                        print('<td>',all_mark,version,'</td>',
                              file=hfiles[i],sep='')
                        print('<td>',pack_anchor_from_hist(
                                timestamp,package,reasons_hash),
                              reasons_summary,'</a></td><td>',
                              file=hfiles[i], sep='')
                        bugtable.print_indirect(package,hfiles[i])
                        print('</td></tr>',file=hfiles[i])
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

        for f in hfiles.values():  print("</table>", file=f)

    del summary_file
    sumfile.close ()
    historyfile.close ()
    for f in hfiles.values():
        print(html_footer,file=f)
        f.close()
    vertical=open(history_verticalfile(scenario,arch),'w')
    for i in hlengths.keys():
        print('{i}={cn}/{ca}'.format(
                i=i,cn=count_natives[i],ca=count_archall[i]),file=vertical)
    vertical.close()

