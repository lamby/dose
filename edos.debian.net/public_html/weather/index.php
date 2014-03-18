<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>Debian Quality Assurance -- Debian weather</title>
  <link rev="made" href="mailto:zack@debian.org" />
  <link rel="shortcut icon" href="/favicon.ico" />
  <link rel="stylesheet" href="weather.css" type="text/css" />
</head>
<?
include("../qa-bodystart.php");
include("weather-config.php");
include("weather-lib.php");
?>

<h1>Debian Weather</h1>

<p>The "weather" of a given Debian-based distribution is an indication of how 
safe it is on a given day to attempt some package installation/upgrade. A "bad 
day" is a day in which a sensible percentage of that distribution repository is 
not installable due to unsatisfiable inter-package dependencies. A "good day", 
on the contrary, is when most (possibly all) of the packages available in that 
distribution repository are installable. For more information see the
<a href="#thresholds">thresholds</a> below.</p>

<h2>Available weathers</h2>

<p>Weathers are computed architecture per architecture, on some Debian based 
distributions. Click on one of the links below to check today's weather for 
your distribution and architecture. Have a nice day!</p>
<?
$weathers = avail_weathers($weather_results)
?>

<h3>Official Debian suites</h3>
<?
$debian_weathers = array();
foreach (array("stable", "testing", "unstable") as $name) {
	$debian_weathers[$name] = $weathers[$name];
	unset($weathers[$name]);
}
print_weather_table($debian_weathers);
?>

<h3>Other Debian-based distributions</h3>
<?
print_weather_table($weathers);
?>

<a name="thresholds" />
<h2>Weather thresholds</h2>

<p>Whether it is a good day or not is decided upon the percentage of non 
installable (binary) packages over the total number of available (binary) 
packages. Currently, package counts take into account only the <tt>main</tt> 
section of any given Debian distro/arch.
The thresholds between the various available wheather statuses are given 
below:</p>

<table>
<?
for ($i = 0; $i < count($weather_thresh); $i++) {
	echo "<tr><td><strong>$weather_descrs[$i]</strong></td><td>&lt;= $weather_thresh[$i]%</td></tr>\n";
}
?>
</table>

<h2>More information</h2>

<p>For more information on the concept of "uninstallability" which is used by 
Debian Weather you can have a look at the
<a href="http://www.mancoosi.org/edos/formalization/">EDOS 
formalization</a> of inter-package relationships. An analysis of common reasons 
which rendere Debian packages uninstallable is available in the report about <a 
href="http://www.mancoosi.org/edos/results/#sec:results:debian"><tt>edos-debcheck</tt> 
experimental results</a>.</p>

<p><tt>edos-debcheck</tt> is available as <a 
href="http://packages.debian.org/stable/edos-debcheck">an official Debian 
package</a>, you can try it by yourself on the package set of your choice.</p>

<? include("weather-trailer.php") ?>
