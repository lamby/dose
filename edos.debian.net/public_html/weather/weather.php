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
$distro = $_REQUEST["distro"];
$arch = $_REQUEST["arch"];

function is_token($str) {
	return preg_match('/^[a-zA-Z0-9-_]+$/', $str);
}
?>

<h1><a href="/weather">Debian weather</a></h1>

<?
if (!is_token($distro) or !is_token($arch))
	die("Invalid distribution/architecture. Go away.\n");
?>

<h2>distribution <em><? echo $distro; ?></em>, architecture: <em><? echo "$arch"; ?></em></h2>

<?
$xmlfile = weather_file($distro, $arch);
if (!file_exists($xmlfile))
	die("Can't find weather XML file on disk. Sorry.\n");
$weather = get_weather($xmlfile);
echo "<div class=\"weather\" style=\"text-align: center;\">\n";
echo "<a href=\"/edos-debcheck/results/$distro/latest/$arch/list.php\">";
print_weather_icon($weather, "big");
echo "</a>";
echo "<br />\n";
printf("broken: %.2f%% <br />(%d uninstallable / %d total packages)<br />\n",
	$weather['weather'], $weather['broken'], $weather['total']);
echo "<a class=\"formatlogo\" href=\"/edos-debcheck/results/$distro/latest/$arch/weather.xml\">XML</a>, ";
echo "<a href=\"/edos-debcheck/results/$distro/latest/$arch/list.php\">more details...</a>";
echo "</div>\n";

include("weather-trailer.php")
?>
