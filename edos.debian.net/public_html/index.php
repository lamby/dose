<?
header('Content-Type: text/html; charset="utf-8"');
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>Debian Quality Assurance -- EDOS tools</title>
  <link rev="made" href="mailto:treinen@debian.org">
  <link rel="shortcut icon" href="/favicon.ico">
</head>

<? include("qa-bodystart.php") ?>
<h1>EDOS Tools</h1>

The <a href=www.edos-project.org>EDOS</a> project was a research
project funded by the European Commission that united several
<a href=http://www.edos-project.org/bin/view/Main/Partners>academic
and industrial project partners</a> concerned with the improvement of
the develepment and distribution of Open Source Software. In this
project,
<a href=http://www.edos-project.org/bin/view/Main/Wp2>Workpackage
2</a> was in particular concerned with the formal analysis of package
relationships.  Several
<a href=http://www.edos-project.org/bin/view/Main/Tools>tools</a> came
out of that project, many of which are today maintained by the
successor project <a href=http://www.mancoosi.org>Mancoosi</a>. See
<a href=http://upsilon.cc/~zack/research/publications/debconf8-mancoosi.pdf>our paper at DebConf8</a> for further details.
<p>
This page describes several checks that are performed using the 
EDOS tools.

<h2>Overview of package analysis in various suites and blends</h2>
<ul>
<li><a href=edos-debcheck/>Non-installable packages</a>
<li><a href="weather/">
  Debian Weather: <q>what's the weather like in Debian distros?</q><br />
  <img style="border-style: none" src="weather/pics/weather-clear_sml.png"><img style="border-style: none" src="weather/pics/weather-few-clouds_sml.png"><img style="border-style: none" src="weather/pics/weather-overcast_sml.png"><img style="border-style: none" src="weather/pics/weather-showers-scattered_sml.png"><img style="border-style: none" src="weather/pics/weather-storm_sml.png"></a>
</li>
</ul>


<h2>Tracking filed bug reports</h2>
<ul>
  <li><a href=file-overwrites/>File overwrite errors during package
  installation</a>
  <li><a href=outdated.php>Packages that are outdated in sid</a>
  <li><a href=uninstallable.php>Packages that are found uninstallable due to
      unsatisfiable package relationships</a>
  <li><a href=warnings.php>Warnings on package names, numbers, and relations</a>
</ul>


<hr>
Made by Fabio Mancinelli, Ralf Treinen, and Stefano Zacchiroli.
Last modified
<?php echo date("r", getlastmod())?>.
<br>
Copyright (C) 2006-2010<a
href="http://www.spi-inc.org/">Software in the Public Interest</a> and others;
See <a href="http://www.debian.org/license">license terms</a>.
</body>
</html>
