<?php
include("../qa-bodystart.php");
$distributions = array("skolelinux_lenny", "skolelinux_lenny-test");
function myinclude($filename) {
	if (file_exists($filename)) {include($filename);}}
?>

<h1>Uninstallable Packages in
<a href=http://wiki.debian.org/DebianEdu>Debian Edu/Skolelinux</a></h1>

Clicking on the numbers in the table gives a detailed listing.
<p>
In every cell of the following tables, the first value gives the total
number of noninstallable packages, while the value in parantheses
gives the number of noninstallable packages that have their
<i>Architecture</i> set to a value different from <i>all</i>.

<?php
foreach ($distributions as $dist) {
  myinclude("results/$dist/table.php");
  }
?>

<p>

<hr>
[<a href=index.php>Back to the Index of EDOS Debcheck</a>]
<hr>
Made by Ralf Treinen.
Last generated on
<?php echo date("r", filemtime("results/timestamp"))?>.
<br>
Copyright (C) 2006-2010 <a
href="http://www.spi-inc.org/">Software in the Public Interest</a> and others;
See <a href="http://www.debian.org/license">license terms</a>.
</body>
</html>
