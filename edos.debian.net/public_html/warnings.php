<?
header('Content-Type: text/html; charset="utf-8"');
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>Debian Quality Assurance -- EDOS debcheck</title>
  <link rev="made" href="mailto:treinen@debian.org">
  <link rel="shortcut icon" href="/favicon.ico">
</head>

<?include("qa-bodystart.php")?>

<h1>Warnings on packages found by EDOS debcheck</h1>


Detected bugs are marked there with user
<kbd>treinen@debian.org</kbd> and usertag <kbd>edos-relation-warning</kbd>.
<ul>
<li><a href=http://bugs.debian.org/cgi-bin/pkgreport.cgi?tag=edos-relation-warning;users=treinen@debian.org>List of all bugs</a>
</ul>

<hr>
Made by Ralf Treinen.
Last modfied on
<?php echo date("r", getlastmod())?>.
<br>
Copyright (C) 2006 <a
href="http://www.spi-inc.org/">Software in the Public Interest</a> and others;
See <a href="http://www.debian.org/license">license terms</a>.
</body>
</html>
