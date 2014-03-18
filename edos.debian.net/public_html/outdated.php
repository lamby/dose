<?
header('Content-Type: text/html; charset="utf-8"');
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>Debian Quality Assurance -- Bugs filed for outdated packages</title>
  <link rev="made" href="mailto:treinen@debian.org">
  <link rel="shortcut icon" href="/favicon.ico">
</head>

<?include("qa-bodystart.php")?>

<h1>Bugs filed for outdated packages</h1>

We call a package <i>p</i> in version <i>n</i> outdated w.r.t. a certain
repository <i>R</i> if:
<ul>
<li> it is not installable in <i>R</i>
<li> no matter how the <emph>other</emph> packages in <i>R</i> evolve,
 this package remains uninstallable. This includes the possibility that
 missing packages are added to the repository, or that packages change
 their dependencies and conflicts while being updated.
</ul>
We attempt to take into account the fact that packages that stem from the
same source package cannot be updated independently: if we find that
two binary packages <i>p1</i> and <i>p2</i> have the same source package
and have similar version numbers (that is, the same version up to epoch
and up to a binNMU), then we assume that also in the future these two packages
will advance in a synchronised way. This is an approxiamtion since we do
not take the possibility into account that packages may chaneg their source
package.
<p>
This means that package <i>p</i> can only be made installable by updating
it in the repository (either by a sourceful or a recompilation upload).
<p>
Currently I file bugs with severity=serious against such packages.
<p>
Detected bugs are marked there with user
<kbd>treinen@debian.org</kbd> and usertag <kbd>edos-outdated</kbd>.
<ul>
<li><a href=http://bugs.debian.org/cgi-bin/pkgreport.cgi?tag=edos-outdated;users=treinen@debian.org;dist=unstable>Bugs in unstable</a>
</ul>

<hr>
Made by Ralf Treinen.
Last modfied on
<?php echo date("r", getlastmod())?>.
<br>
Copyright (C) 2011 <a
href="http://www.spi-inc.org/">Software in the Public Interest</a> and others;
See <a href="http://www.debian.org/license">license terms</a>.
</body>
</html>
