<?php
include("../qa-bodystart.php");
?>

<h1>EDOS-Debcheck: File Overwrite Errors</h1>

This page is about reporting file overwrite errors that occur when one
package tries to install a file that is owned by a different
package. I run at irregular intervals, but typically at least once per
day, a script that proceeds as follows:

<p>
<ol>
<li>Calculate from a recent <kbd>Contents</kbd> file a list of pairs
   of packages that share at least one file.</li>
<li>Restrict the list obtained in (1) to those pairs of packages that
  are co-installable according to edos-debcheck.</li>
<li>Try installation of every pair of packages remaining after step
  (2) in a fresh chroot.</li>
</ol>
<p>
Usually I do these checks for sid on amd64, in times of preparation of
a release I might also check testing. There is a <a href=doc.html>more
detailed documentation on how this works</a>.
<p>
Detected problems are filed as bugs, usually against both offending
packages with severity Serious, with the list of files that are common
to both packages according to the Contents file. Bugs (both bugs that
I have filed as result of my script, and bugs that have been reported
by others and that I have reproduced with my script) carry a usertag
<kbd>edos-file-overwrite</kbd> for the user
<kbd>treinen@debian.org</kbd>.

<ul>
  <li><a href=http://bugs.debian.org/cgi-bin/pkgreport.cgi?tag=edos-file-overwrite;users=treinen@debian.org>All detected bugs</a>
</ul>

Note that <a href=http://wiki.debian.org/piuparts>piuparts</a> does
much more extensive tests of package installation and removal, and
checks for different kinds of problems that may occur. One of the many
tests done by piuparts now uses edos-debcheck to generate test
candidates following the first two steps described above. Some
categories of bugs are found by piuparts this way:
<ul>
<li><a href=http://bugs.debian.org/cgi-bin/pkgreport.cgi?tag=replaces-without-breaks;users=debian-qa@lists.debian.org>Replaces without breaks</a>
</ul>

<p>
<hr>
Made by Ralf Treinen. Last update
<?php echo date("r", filemtime("index.php"))?>.
<br>
Copyright (C) 2008 <a
href="http://www.spi-inc.org/">Software in the Public Interest</a> and others;
See <a href="http://www.debian.org/license">license terms</a>.
</body>
</html>
