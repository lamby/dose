<?
header('Content-Type: text/html; charset="utf-8"');
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>Debian Quality Assurance -- Bugs filed for uninstallable
    packages</title>
  <link rev="made" href="mailto:treinen@debian.org">
  <link rel="shortcut icon" href="/favicon.ico">
</head>

<?include("qa-bodystart.php")?>

<h1>Bugs filed for uninstallable packages</h1>

The <a href=edos-debcheck/>edos-debcheck daily runs</a> report many
packages that are uninstallable due to unsatisfiable relationships
with other packages. Many of these problems are transient (due to
delays in autobuilders, for instance), or currently unavoidable (in
particular package having <kbd>Architecture=all</kbd> but that depend
on architecture-specific packages that are not available on all
architectures). For this reason, bug reports against not-installable
packages should be filed only after careful investigation.
<p>

Currently I file bugs with severity=grave (since it makes the package unusable for most users) in the following cases:
<ul>
<li>Package uninstallable on all architectures
<li>for unstable only: and problem exists since at least one month
<li>and: problem is not ``known'' to be being worked on, or resolution pending. 
</ul>
This has been announced and discussed in <a href=http://lists.debian.org/debian-devel/2010/08/msg00063.html>this thread</a>.
Detected bugs are marked there with user
<kbd>treinen@debian.org</kbd> and usertag <kbd>edos-uninstallable</kbd>.
<ul>
<li><a href=http://bugs.debian.org/cgi-bin/pkgreport.cgi?tag=edos-uninstallable;users=treinen@debian.org;dist=unstable>Bugs in unstable</a>
<li><a href=http://bugs.debian.org/cgi-bin/pkgreport.cgi?tag=edos-uninstallable;users=treinen@debian.org;dist=testing>Bugs in testing</a>
<li><a href=http://bugs.debian.org/cgi-bin/pkgreport.cgi?tag=edos-uninstallable;users=treinen@debian.org;dist=stable>Bugs in stable</a>
<li><a href=http://bugs.debian.org/cgi-bin/pkgreport.cgi?tag=edos-uninstallable;users=treinen@debian.org>All bugs</a>
</ul>

<hr>
Made by Ralf Treinen.
Last modfied on
<?php echo date("r", getlastmod())?>.
<br>
Copyright (C) 2010 <a
href="http://www.spi-inc.org/">Software in the Public Interest</a> and others;
See <a href="http://www.debian.org/license">license terms</a>.
</body>
</html>
