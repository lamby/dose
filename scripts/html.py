# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os, datetime
import common

########################################################################

class summary:
    """
    A file object containg an html table of packages that are not
    installable in a certain scenario, architecture. Can be used 
    for a particular date, or for historical summaries.
    """

    summary_header_no_history = '''
<h1>Packages not installable on {architecture} in scenario {scenario}</h1>
<b>Date: {utctime} UTC</b>
<p>

<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
<p>
'''

    summary_header_with_history = '''
<h1>Packages not installable on {architecture} in scenario {scenario}
for {days} days</h1>
<b>Date: {utctime} UTC</b>
<p>

Packages that have been continuously found to be not installable
(not necessarily in the same version, and not necessarily with the
same explanation all the time).<p>
<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
<p>
'''

    table_header_no_history = '''
<table border=1>
<tr>
<th>Package</th>
<th>Version</th>
<th>Short explanation (click for detailed explanation)</th>
<th>Tracking</th>
</tr>
'''

    table_header_with_history = '''
<table border=1>
<tr>
<th>Package</th>
<th>Since</th>
<th>Version today</th>
<th>Short explanation as of today (click for details)</th>
<th>Tracking</th>
</tr>
'''

    def __init__(self,timestamp,scenario,architecture,bugtable,
                 since_days=None):
        """
        Open the html file and print the header.

        If since_days is a non-null value d than a table with historical
        start date is created, for packages non-installable for at least
        d many days
        """

        outdir=common.htmldir(timestamp,scenario)
        if not os.path.isdir(outdir): os.makedirs(outdir)
        histhtmldir=common.history_htmldir(scenario,architecture)
        if not os.path.isdir(histhtmldir): os.makedirs(histhtmldir)

        self.bugtable=bugtable
        self.timestamp=timestamp
        self.since_days=since_days
        self.in_table=False
        if since_days:
            summary_header = self.summary_header_with_history
            self.table_header = self.table_header_with_history
            self.filedesc = open(histhtmldir+'/'+str(since_days)+'.html', 'w')
        else:
            summary_header = self.summary_header_no_history
            self.table_header = self.table_header_no_history
            self.filedesc = open(outdir+'/'+architecture+'.html', 'w')
        print(common.html_header,file=self.filedesc)
        print(summary_header.format(
            timestamp=str(timestamp),
            scenario=scenario,
            architecture=architecture,
            days=since_days,
            utctime=datetime.datetime.utcfromtimestamp(float(timestamp))),
        file=self.filedesc)
        print(self.table_header,file=self.filedesc)
        self.in_table=True

    def __del__(self):
        """
        Print the html footer stuff and close the html file
        """
        
        if self.in_table:
            print('</table>',common.html_footer,file=self.filedesc,sep='\n')
        self.filedesc.close()

    def write(self,package,isnative,version,reasons_hash,reasons_summary,
              since=None):
        """
        Write one line of a summary table
        """

        all_mark = '' if isnative else '[all] '  
        print('<tr><td>',package,'</td>',file=self.filedesc,sep='',end='')
        if self.since_days:
            print('<td>',since,'</td>',file=self.filedesc,end='')
        print('<td>',all_mark,version,'</td>',
              '<td>',common.pack_anchor(self.timestamp,package,reasons_hash),
              reasons_summary,'</a></td><td>',
              file=self.filedesc, sep='')
        self.bugtable.print_indirect(package,self.filedesc)
        print('</td></tr>',file=self.filedesc)

    def section(self,text):
        '''
        write a <h2> header into the HTMl file. Close and Re-open a table
        when necessary.
        '''

        if self.in_table:
            print('</table>',file=self.filedesc)
        print('<h2>',text,'</h2>',file=self.filedesc,sep='')
        if self.in_table:
            print(self.table_header,file=self.filedesc)

###########################################################################

class summary_multi(summary):

    summary_header_no_history='''
<h1>Packages not installable on {architecture} architecture
in scenario {scenario}</h1>
<b>Date: {utctime} UTC</b>
<p>
<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
<p>
'''

    summary__header_with_history = '''
<h1>Packages not installable on {architecture} architecture
in scenario {scenario}
for {days} days</h1>
<b>Date: {utctime} UTC</b>
<p>

Packages that have been continuously found to be not installable
(not necessarily in the same version,
 not necessarily on the same architectures,
 and not necessarily with the same explanation all the time).<p>
'''

    table_header_no_history = '''
<table border=1>
<tr>
<th>Package</th>
<th>Version</th>
<th>Architectures</th>
<th>Short explanation (click for detailed explanation)</th>
<th>Tracking</th>
</tr>
'''

    table_header_with_history = '''
<table border=1>
<tr>
<th>Package</th>
<th>Since</th>
<th>Version today</th>
<th>Architectures</th>
<th>Short explanation as of today (click for details)</th>
<th>Tracking</th>
</tr>
'''

    def write(self,package,reasons,since=None):
        """
        Write one line of a summary table
        """

        number_of_hashes=len(reasons)
        if number_of_hashes > 1:
            multitd='<td rowspan="'+str(number_of_hashes)+'">'
        else:
            multitd='<td>'
        print('<tr>',multitd,package,'</td>',file=self.filedesc,sep='')
        if self.since_days:
            print(multitd,since,'</td>',file=self.filedesc,end='')
        continuation_line=False
        for hash in reasons:
            if continuation_line:
                print('<tr>',file=self.filedesc)
            record=reasons[hash]
            if record['isnative'] == 'True':
                all_mark = '' 
            else:
                all_mark='[all]'
            print('<td>',all_mark,record['version'],'</td>',
                  file=self.filedesc,sep='')
            print('<td>',file=self.filedesc,end='')
            for arch in record['archs']:
                print(arch, file=self.filedesc, end=' ')
            print('</td>',file=self.filedesc,end='')
            print('<td>',
                  common.pack_anchor_from_hist(self.timestamp,package,hash),
                  record['short'],
                  '</a></td>',
                  file=self.filedesc,sep='')
            if not continuation_line:
                print(multitd,file=self.filedesc,end='')
                self.bugtable.print_indirect(package,self.filedesc)
                print('</td>',file=self.filedesc)
            print('</tr>',file=self.filedesc)
            continuation_line=True



