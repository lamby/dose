# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import conf
from datetime import date

verbose=True

def info(message):
    if verbose: print(message)

def cachedir(timestamp,scenario,arch):
    '''
    absolute path of a cache directory for given timestamp, scenario, arch
    '''
    return('{r}/{t}/{s}/{a}'.format(
            r=conf.locations['cacheroot'],
            t=timestamp,
            s=scenario,
            a=arch))

def history_cachedir(scenario):
    return('{r}/history/{s}'.format(
            r=conf.locations['cacheroot'],
            s=scenario))

def history_cachefile(scenario,architecture):
    return('{r}/history/{s}/{a}'.format(
            r=conf.locations['cacheroot'],
            s=scenario,
            a=architecture))

def htmldir(timestamp,scenario):
    '''
    absolute path of a html directory for given timestamp, scenario
    '''
    return('{r}/{s}/{t}'.format(
            r=conf.locations['htmlroot'],
            t=timestamp,
            s=scenario))

def htmldir_scenario(scenario):
    '''
    absolute path of a html directory for given scenario
    '''
    return('{r}/{s}'.format(
            r=conf.locations['htmlroot'],
            s=scenario))

def pack_anchor(timestamp,package,hash):
    '''
    relative path, from an architecture page, to a package page 
    '''
    return('<a href="packages/{p}.html#{h}">'.format(
            p=package,
            h=hash))

def str_of_list(liste):
    if not liste: return ''
    result, *rest = liste
    for element in rest:
        result += ', ' + element
    return(result)

html_header = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
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
          border-left: 1pt solid black;
          border-right: 1pt solid black;
          border-bottom: 1pt solid black;
          border-top: 1pt solid black;
        }
    </style>
  </head>
  
  <body>
    <div id="header">
      <div id="upperheader">
	<div id="logo">
          <a href="http://www.debian.org/" title="Debian Home"><img src="/Pics/openlogo-50.png"
								    alt="Debian" width="50" height="61"></a>
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

html_footer='''    <div id="footer">
      <hr class="hidecss">
      <p>Back to the <a href="http://www.debian.org/">Debian Project homepage</a>.</p>
      <hr>
      <div id="fineprint">
	<p>To report a problem with the QA web site,
	  e-mail <a href="mailto:debian-qa@lists.debian.org">debian-qa@lists.debian.org</a>. For
	  other contact information, see the
	  Debian <a href="http://www.debian.org/contact">contact
	    page</a>.</p>
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

seconds_per_day = 60 * 60 * 24

def days_since_epoch(time):
    return(time//seconds_per_day)

# ordinal number of 1/1/1970, where 1 = 1/1/0000 
proleptic_of_epoch = 719163

# date corresponding to a number of days since epoch
def date_of_days(days):
    (date.fromordinal(days+proleptic_of_epoch)).isoformat()
