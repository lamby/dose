# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os, datetime
import common

########################################################################

html_header='''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>Debian QA: dose-debcheck</title>
  <link rev="made" href="mailto:debian-qa@lists.debian.org">
  <link rel="shortcut icon" href="/favicon.ico">
  <link type="text/css" rel="stylesheet" href="/debian.css">
  <link type="text/css" rel="stylesheet" href="debian.css">
  <style>
    td, th {
      padding: 6px;
      border: 1pt solid black;
    }
  </style>
</head>
  
<body>
<div id="header">
  <div id="upperheader">
    <div id="logo">
      <a href="http://www.debian.org/" title="Debian Home"><img src="/Pics/openlogo-50.png" alt="Debian" width="50" height="61"></a>
    </div>
    <p class="section"><a href="/">QA</a></p>
  </div>
  <div id="navbar">
    <p class="hidecss"><a href="#inner">Skip Quicknav</a></p>
    <ul>
      <li><a href="http://www.debian.org/intro/about">About Debian</a></li>
      <li><a href="http://www.debian.org/distrib/">Getting Debian</a></li>
      <li><a href="http://www.debian.org/support">Support</a></li>
      <li><a href="http://www.debian.org/devel/">Developers'&nbsp;Corner</a></li>
    </ul>
  </div>
  <p id="breadcrumbs">Debian Quality Assurance</p>
</div>

<div id="content">
'''

html_footer='''</div>

<div id="footer">
  <hr class="hidecss">
  <p>Back to the <a href="http://www.debian.org/">Debian Project homepage</a>.</p>
  <hr>
  <div id="fineprint">
    <p>
      To report a problem with the QA web site,
      e-mail <a href="mailto:debian-qa@lists.debian.org">debian-qa@lists.debian.org</a>. For
      other contact information, see the
      Debian <a href="http://www.debian.org/contact">contact page</a>.
    </p>
    <p>
      Made by Ralf Treinen; code is
      <a href="https://alioth.debian.org/plugins/scmgit/cgi-bin/gitweb.cgi?p=qa/dose.git;a=summary">
      available</a>.<br>
      Copyright &copy; 2014
      <a href="http://www.spi-inc.org/">SPI</a>;
      see <a href="http://www.debian.org/license" rel="copyright">license terms</a>.<br>
      Debian is a registered <a href="http://www.debian.org/trademark">trademark</a> of
      Software in the Public Interest, Inc.
    </p>
  </div>
</div>
</body>
</html>
'''

class html_file:
    """
    Objects for HTML files in the debian QA style
    """

    def __init__(self,output_path,output_name):
        '''
        open a file for writing with given path and file name,
        print HTML header.
        '''

        if not os.path.isdir(output_path):
            os.makedirs(output_path)
        self.filedesc = open(output_path+'/'+output_name, 'w')
        print(html_header,file=self.filedesc)
        self.in_table=False

    def __del__(self):
        '''
        print the HTML footer and close the file.
        '''

        print(html_footer,file=self.filedesc)
        self.filedesc.close()
        
########################################################################

class html_table(html_file):
    """
    An HTML file with one or several tables that a user can fill in
    line by line.
    """

    path_to_packages=None # relative path of the dir containing package pages

    def __init__(self,output_path,output_name,
                 page_header,table_header,
                 display_since=False,bugtable=None):

        '''
        Open the file and print the page header. 

        Display_since: control presence of a "since" column

        Bugtable: used to obtain information on relevant bugs. Don't print
          a Tracking column when set to None.
        '''

        html_file.__init__(self,output_path,output_name)

        self.table_header=table_header
        self.display_since=display_since
        self.bugtable=bugtable

        print(page_header,file=self.filedesc)
        self.in_table=False
        
    def __del__(self):
        """
        Print the html footer stuff and close the html file
        """
        if self.in_table:
            print('</table>',file=self.filedesc)
        html_file.__del__(self)

    def write(self,package,isnative,version,reasons_hash,reasons_summary,
              since=None):
        """
        Write one line of a summary table
        """

        all_mark = '' if isnative else '[all] '  
        print('<tr><td>',package,'</td>',file=self.filedesc,sep='',end='')
        if self.display_since:
            print('<td>',since,'</td>',file=self.filedesc,end='')
        print('<td>',all_mark,version,'</td>',
              '<td><a href=',self.path_to_packages,package,'.html#',
              reasons_hash,'>',reasons_summary,'</a></td><td>',
              file=self.filedesc, sep='')
        if self.bugtable:
            self.bugtable.print_indirect(package,self.filedesc)
        print('</td></tr>',file=self.filedesc)

    def section(self,text):
        '''
        write a <h2> header into the HTML file and open a table.
        '''

        if self.in_table:
            print('</table>',file=self.filedesc)
        print('<h2>',text,'</h2>',file=self.filedesc,sep='')
        self.start_table()

    def start_table(self):
        '''
        open a table.
        '''
        print(self.table_header,file=self.filedesc)
        self.in_table=True

    def set_path_to_packages(self,path):
        self.path_to_packages = path

###########################################################################

class html_table_multi(html_table):

    '''
    As html_table, but allows for printing multiple-line entries for
    the same package.
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
        if self.display_since:
            print(multitd,since,'</td>',file=self.filedesc,end='')
        continuation_line=False
        for hash in reasons:
            if continuation_line:
                print('<tr>',file=self.filedesc)
            record=reasons[hash]
            if record['isnative']:
                all_mark = '' 
            else:
                all_mark='[all]'
            print('<td>',all_mark,record['version'],'</td>',
                  file=self.filedesc,sep='')
            print('<td>',file=self.filedesc,end='')
            for arch in record['archs']:
                print(arch, file=self.filedesc, end=' ')
            print('</td>',file=self.filedesc,end='')
            print('<td><a href=',self.path_to_packages,package,'.html#',
                  hash,'>',record['short'],'</a></td>',
                  file=self.filedesc,sep='')
            if not continuation_line:
                print(multitd,file=self.filedesc,end='')
                if self.bugtable:
                    self.bugtable.print_indirect(package,self.filedesc)
                print('</td>',file=self.filedesc)
            print('</tr>',file=self.filedesc)
            continuation_line=True

###########################################################################

class summary(html_table):

    path_to_packages = 'packages/'

    def __init__(self,timestamp,scenario,architecture,bugtable):

        summary_header = '''
<h1>Packages not installable on {architecture} in scenario {scenario}</h1>
<b>Date: {utctime} UTC</b>
<p>

<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
<p>
'''

        table_header = '''
<table border=1>
<tr>
<th>Package</th>
<th>Version</th>
<th>Short explanation (click for detailed explanation)</th>
<th>Tracking</th>
</tr>
'''

        output_path=common.htmldir(timestamp,scenario)
        output_name=architecture+'.html'

        header=summary_header.format(
            scenario=scenario,
            architecture=architecture,
            utctime=datetime.datetime.utcfromtimestamp(float(timestamp)))

        html_table.__init__(self,output_path,output_name,
                            header,table_header,bugtable=bugtable)
        self.start_table()

###########################################################################

class summary_multi(html_table_multi):

    path_to_packages = 'packages/'
    
    def __init__(self,timestamp,scenario,architecture,bugtable):

        summary_header = '''
<h1>Packages not installable on {architecture} architecture
in scenario {scenario}</h1>
<b>Date: {utctime} UTC</b>
<p>
<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
o<p>
'''

        table_header = '''
<table border=1>
<tr>
<th>Package</th>
<th>Version</th>
<th>Architectures</th>
<th>Short explanation (click for detailed explanation)</th>
<th>Tracking</th>
</tr>
'''

        output_path=common.htmldir(timestamp,scenario)
        output_name=architecture+'.html'
        header=summary_header.format(
            scenario=scenario,
            architecture=architecture,
            utctime=datetime.datetime.utcfromtimestamp(float(timestamp)))
        html_table_multi.__init__(self,output_path,output_name,
                              header,table_header,bugtable=bugtable)
        self.start_table()

############################################################################

class history(html_table):

    def __init__(self,timestamp,scenario,architecture,bugtable,since_days):

        summary_header = '''
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
        
        table_header = '''
<table border=1>
<tr>
<th>Package</th>
<th>Since</th>
<th>Version today</th>
<th>Short explanation as of today (click for details)</th>
<th>Tracking</th>
</tr>
'''

        self.path_to_packages = '../../'+str(timestamp)+'/packages/'

        output_path=common.history_htmldir(scenario,architecture)
        output_name = str(since_days)+'.html'
        header=summary_header.format(
            timestamp=str(timestamp),
            scenario=scenario,
            architecture=architecture,
            days=since_days,
            utctime=datetime.datetime.utcfromtimestamp(float(timestamp)))
        html_table.__init__(self,output_path,output_name,
                            header,table_header,
                            display_since=True,bugtable=bugtable)
        self.start_table()


############################################################################

class history_multi(html_table_multi):

    def __init__(self,timestamp,scenario,architecture,bugtable,since_days):

        summary_header = '''
<h1>Packages not installable on {architecture} architecture 
in scenario {scenario} for {days} days</h1>
<b>Date: {utctime} UTC</b>
<p>

Packages that have been continuously found to be not installable
(not necessarily in the same version, and not necessarily with the
same explanation all the time).<p>
<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
<p>
'''

        table_header = '''
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

        self.path_to_packages = '../../'+str(timestamp)+'/packages/'

        output_path=common.history_htmldir(scenario,architecture)
        output_name = str(since_days)+'.html'
        header=summary_header.format(
            timestamp=str(timestamp),
            scenario=scenario,
            architecture=architecture,
            days=since_days,
            utctime=datetime.datetime.utcfromtimestamp(float(timestamp)))
        html_table.__init__(self,output_path,output_name,
                            header,table_header,
                            display_since=True,bugtable=bugtable)
        self.start_table()


###########################################################################

class diff(html_table):

    path_to_packages = 'packages/'

    def __init__(self,timestamp_now,timestamp_prev,scenario,architecture):

        summary_header='''
<h1>Difference for {architecture} in scenario {scenario}</h1>
<b>From {tprev} UTC<br>To {tnow} UTC</b>
<p>
<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
'''

        table_header='''
<table border=1>
<tr>
<th>Package</th>
<th>Version</th>
<th>Short Explanation (click for details)</th>
'''

        output_path=common.htmldir(timestamp_now,scenario)
        output_name=architecture+'-diff.html'

        header=summary_header.format(
            scenario=scenario,
            architecture=architecture,
            tprev=datetime.datetime.utcfromtimestamp(float(timestamp_prev)),
            tnow=datetime.datetime.utcfromtimestamp(float(timestamp_now)))

        html_table.__init__(self,output_path,output_name,
                            header,table_header)

###########################################################################

class diff_multi(html_table_multi):

    path_to_packages = 'packages/'

    def __init__(self,timestamp_now,timestamp_prev,scenario,where):

        summary_header='''
<h1>Difference for {where} architecture in scenario {scenario}</h1>
<b>From {tprev} UTC<br>To {tnow} UTC</b>
<p>
<kbd>[all]</kbd> indicates a package with <kbd>Architecture=all</kbd>.
'''

        table_header='''
<table border=1>
<tr>
<th>Package</th>
<th>Version</th>
<th>Architectures</th>
<th>Short Explanation (click for details)</th>
'''

        output_path=common.htmldir(timestamp_now,scenario)
        output_name=where+'-diff.html'

        header=summary_header.format(
            scenario=scenario,
            where=where,
            tprev=datetime.datetime.utcfromtimestamp(float(timestamp_prev)),
            tnow=datetime.datetime.utcfromtimestamp(float(timestamp_now)))

        html_table_multi.__init__(self,output_path,output_name,
                                  header,table_header)

