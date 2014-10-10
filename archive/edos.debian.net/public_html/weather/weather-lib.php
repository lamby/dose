<?

function avail_weathers($basedir) {
	$avail = array();
	$distros = glob("$basedir/*", GLOB_ONLYDIR);
	foreach ($distros as $distro) {
		if (preg_match('/test$/i', $distro))
			continue;
		$distro_base = basename($distro);
		$avail[$distro_base] = array();
		$archs = glob("$distro/latest/*", GLOB_ONLYDIR);
		foreach ($archs as $arch) {
			$arch_base = basename($arch);
			if ($arch_base == "some" || $arch_base == "every")
				continue;
			$avail[$distro_base][$arch_base] = true;
		}
	}
	return $avail;
}

function weather_file($distro, $arch) {
	global $weather_results;
	$xmlfile = "$weather_results/$distro/latest/$arch/weather.xml";
	return $xmlfile;
}

# parse a given XML file and return the Debian weather as a percentage.
# XML file format is the same used by the weather applets.
function get_weather($xmlfile) {
	$xml = simplexml_load_file($xmlfile);
	$total = $xml->xpath('/weather/packages/total');
	$broken = $xml->xpath('/weather/packages/broken');
	$index = $xml->xpath('/weather/index');
	$res = array();
	$res['total'] = floatval($total[0]);
	$res['broken'] = floatval($broken[0]);
	$res['weather'] = floatval($broken[0])/floatval($total[0])*100;
	$res['index'] = intval($index[0]);
	return $res;
}

function print_weather_icon($weather, $size) {
	global $weather_descrs, $weather_files;
	global $distro, $arch;

	$i = $weather['index'];
	if ($i < 1 or $i > count($weather_files)) {
		die("Invalid weather index '$i', blame weather.xml. Bye.");
	}
	$i--;	# indexes from weather.xml are 1-based
	$descr = ucfirst($weather_descrs[$i]);
	echo "<img class='weather-logo' src=\"pics/$weather_files[$i]_$size.png\" />";
	return;
}

function print_weather_table($weathers) {
	echo "<table>";
	foreach ($weathers as $distro => $archs) {
		echo "<tr>";
		echo "<th style='text-align: left'>$distro</th>";
		echo "<td>";
		echo "<table style='display: inline'><tr>";
		foreach (array_keys($archs) as $arch) {
			echo "<td style='text-align: center'>";
			echo "<a href=\"weather.php?distro=$distro&arch=$arch\">";
			$xmlfile = weather_file($distro, $arch);
			if (file_exists($xmlfile)) {
				$weather = get_weather($xmlfile);
				print_weather_icon($weather, "sml");
				echo "<br />\n";
			}
			echo "<small>$arch</small></a> ";
			echo "</td>";
		}
		echo "</tr></table></td></tr>\n";
	}
	echo "</table>";
}

?>

