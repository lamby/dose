<?php
include("../qa-bodystart.php");
?>

<h1>EDOS-Debcheck: Uninstallable Packages</h1>

<ul>
<li><a href=unstable.php>Debian unstable (sid)</a>
<li><a href=testing.php>Debian testing </a>
<li><a href=stable.php>Debian stable </a>
<li><a href=skolelinux.php>Skolelinux</a>
<li><a href=grip.php>Emdebian</a>
</ul>

<p>

In this context, we say that a package <i>P</i>
is <em>installable</em> in some distribution <i>D</i> if there 
there is a subset <i>S</i> of <i>D</i> containing <i>P</i>, and such that
for each package in <i>S</i>
<ul>
<li>every dependency relation is satisfied by some package in <i>S</i>
<li>and it is not in conflict with any package in <i>S</i>
</ul> 

The set of uninstallable packages is computed by the <a
href=http://packages.debian.org/unstable/devel/edos-debcheck>edos-debcheck</a>
tool. More information about this can be found at <a
href=http://www.edos-project.org/xwiki/bin/view/Main/Wp2>EDOS WorkPackage 2</a>.

<hr>
Made by Ralf Treinen.
Last generated on
<?php echo date("r", filemtime("results/timestamp"))?>.
<br>
Copyright (C) 2006-2013 <a
href="http://www.spi-inc.org/">Software in the Public Interest</a> and others;
See <a href="http://www.debian.org/license">license terms</a>.
</body>
</html>
