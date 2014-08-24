# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.


summary_header_no_history = '''
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
<table border=1>
<tr>
<th>Package</th>
<th>Since</th>
<th>Version today</th>
<th>Short explanation as of today (click for details)</th>
<th>Tracking</th>
'''

########################################################################

class summary:
    """
    A file object containg an html table of packages that are not
    installable in a certain scenario, architecture. Can be used 
    for a particular date, or for historical summaries.
    """

    def __init__(self,timestamp,scenario,architecture,bugtable,
                 since_days=None):
        """
        Open the html file and print the header.

        If since_days is a non-null value d than a table with historical
        start date is created, for packages non-installable for at least
        d many days
        """

        outdir=htmldir(timestamp,scenario)
        if not os.path.isdir(outdir): os.makedirs(outdir)
        histhtmldir=history_htmldir(scenario,architecture)
        if not os.path.isdir(histhtmldir): os.makedirs(histhtmldir)

        self.bugtable=bugtable
        self.timestamp=timestamp
        self.since_days=since_days
        if since_days:
            summary_header = summary_header_with_history
            self.filedesc = open(histhtmldir+'/'+str(since_days)+'.html', 'w')
        else:
            summary_header = summary_header_no_history
            self.filedesc = open(outdir+'/'+architecture+'.html', 'w')
        print(html_header,file=self.filedesc)
        print(summary_header.format(
            timestamp=str(timestamp),
            scenario=scenario,
            architecture=architecture,
            days=since_days,
            utctime=datetime.datetime.utcfromtimestamp(float(timestamp))),
        file=self.filedesc)

    def __del__(self):
        """
        Print the html footer stuff and close the html file
        """
        
        print('</table>',html_footer,file=self.filedesc,sep='\n')
        self.filedesc.close()

    def write(self,package,isnative,version,reasons_hash,reasons_summary,
              since=None):
        """
        Write one line of a summary table
        """

        all_mark = '' if isnative else '[all] '  
        print('<tr><td>',package,'</td>',file=self.filedesc,end='')
        if self.since_days:
            print('<td>',since,'</td>',file=self.filedesc,end='')
        print('<td>',all_mark,version,'</td>',
              '<td>',pack_anchor(self.timestamp,package,reasons_hash),
              reasons_summary,'</a></td><td>',
              file=self.filedesc, sep='')
        self.bugtable.print_indirect(package,self.filedesc)
        print('</td></tr>',file=self.filedesc)
