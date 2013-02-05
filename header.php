<?if($outputmode==0){?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head profile="http://www.w3.org/2005/10/profile">
<link rel="icon" type="image/ico" href="favicon.ico" />
<meta http-equiv="content-type" content="text/html; charset=UTF-8"/><meta name="description" content="description"/>
<meta name="apple-itunes-app" content="app-id=327702034"/>
<meta name="keywords" content="keywords"/> 
<?if ($title){?>
<title><?=$title?> - Visual Exoplanet Catalogue</title>
<?}else{?>
<title>Visual Exoplanet Catalogue</title>
<?}?>
<link rel="stylesheet" type="text/css" href="./css/style.css" media="screen" />
<link rel="stylesheet" type="text/css" href="./css/tables.css" media="screen" />
<!-- Google Analytics start -->
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-6857673-3");
pageTracker._trackPageview();
} catch(err) {}</script>
<!-- Google Analytics end -->
<?=$header?>
</head>
<body>
<div class="outer-container">

<div class="inner-container">

<div class="header">
<div class="title">
<div class="name"><a href="./index.php">The New Visual Exoplanet Catalogue</a></div>
<div class="tag">a visualisation  toolkit for extrasolar planetary systems</div>
</div> <!-- title -->
</div> <!-- header -->
<div class="navigation">
<h2>Catalogue</h2>
<ul>
<li><a href="./planets.php">All exoplanets</a></li>
<li><a href="./systems.php">All exoplanetary systems</a></li>
<li><a href="./binarysystems.php">Binary/Tripple/Quadrupel star systems with planets</a></li>
<li><a href="./transitingplanets.php">Transiting exoplanets</a></li>
<li><a href="./imagedplanets.php">Imaged exoplanets</a></li>
<li><a href="./multiplanetarysystems.php">Multiplanetary systems</a></li>
</ul>

<!--
<h2>Kepler Catalogue</h2>
<ul>
<li><a href="/kepler/">Public Data Q0</a></li>
</ul>

-->
<h2>Plots</h2>
<ul>
<li><a href="./correlations.php">Correlations plots</a></li>
<li><a href="./histogram.php">Histograms</a></li>
<li><a href="https://github.com/hannorein/oec_plots">Python scripts<br />for offline use</a></li>
</ul>

<h2>About</h2>
<ul>
<li><a href="http://exoplanetapp.com" style="font-weight: bold; color:red;">iPhone Application</a></li>
<li><a href="./index.php">About</a></li>
</ul>

</div> <!-- navigation -->
<div class="content">
<?}?>

<?

function alttr(&$counter, $inc=false){
	if ($inc) { 
		if ($counter) { 
			$counter = false; 
		} else { 
			$counter = true; 
		}
	}
	if ($counter){
		return "";
	}else{
		return "alt";
	}

}
function exitwitherror($error="We're looking into this..."){
	echo "<div style='color: #ff0000; font-size: 1.5em;'><b>An error occured.<b><br /><br />".$error."</div>";
	include ".inc/footer.php";
	die();
}
function show_svg($url, $width=400, $height=400, $format="svg", $id=""){
	?>
<object data="<?=$url?>" type="image/svg+xml" width="<?=$width?>" height="<?=$height?>">
       Your browser (you are probably using Internet Explorer) cannot display SVG. 
</object>
	<?
}

?>
