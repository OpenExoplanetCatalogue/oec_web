#!/usr/bin/python
import subprocess

header ="""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
	<meta http-equiv="content-type"
		content="text/html; charset=ISO-8859-1">
	<meta name="viewport" content="user-scalable=no, width=device-width,maximum-scale=1.0">
	<meta name="format-detection" content="telephone=no">
	<style type="text/css">
		body {
			border: 		0px;
			font-family:		Helvetica;
			background-color:	#000;
			color: 			#fff;
		}
		a:link {
			color:			#eee;
		}
		a:visited {
			color:			#ddd;
		}
		.blacktitle {
			font-size:		1.2em;
			font-weight:		bold;
			width:			100%;
			padding:		0.1em;
			padding-bottom:		0.2em;
		}
		.blacktitlesmall {
			font-size:		1.em;
			width:			100%;
			padding:		0.1em;
			padding-bottom:		0.2em;
		}
		.blackmain {
			width:			100%;
			padding:		0.1em;
		}
		.blacksmall, .share{
			font-size:		0.75em;
			color:			#777;
			font-weight:		lighter;
			width:			100%;
			padding:		0.1em;
			margin-bottom:		1.5em;
			
			clear:			both;
		}
		.blacksmall{
			text-align:		right;
			z-index: 1;
			border-bottom:		1px #777 solid;
		}
		.blacksmall a, .blacksmall img{
			display: none;
		}
		.blacksmall a:link {
			color:			#888;
			text-decoration:none;
		}
		.blacksmall img{
			border: 0px;
			text-decoration:none;
			width: 14px;
			height: 14px;
			vertical-align: text-bottom;
			padding-right: 0.3em;
		}
		.blackimage {
			float: 			left;
			height:			71px;
			width:			71px;
			padding-right:		0.5em;
		}
	</style>
	<script type="text/javascript">
		function share(tag){
			var newsitem = this.parentNode.parentNode;
			var url = "share://host/";
			for (var i = 0; i < newsitem.children.length; i++){
				var div = newsitem.children[i];
				if (div.className=="blacktitle" || div.className=="blackmain"){
					var urlpart = encodeURIComponent(div.textContent.trim()+" ");
					url +=urlpart;
				}
			}
			window.open(url);
		}
	</script>
</head>
<body>
		<div class="blacktitle">
		This section lists recent updates to the Open Exoplanet Catalogue. 
		</div>

"""
footer = """
<script type="text/javascript" src="retina.js"></script>
</body>
</html>
"""

def format_item(text,date):
	return """
	<div class="newsitem">
		<div class="blackmain">
		<img src="push.png" alt="Push notification" class="blackimage"/>
		%s
		</div>
		<div class="blacksmall">Updated posted %s. <a href="javascript:void(0)" onclick="share.call(this)"><img src="share_iphone.png">Share.</a></div>
	</div>
	""" % (text, date.strip())

N = 10

with open("./iphone/news/index.php","w") as f:
	print >>f, header
	for i in xrange(N):
	    s = subprocess.check_output(["git", "log", "-n", "1", "--skip=%i"%i, "--no-merges", "--format=%s%b"],cwd="open_exoplanet_catalogue")
	    d = subprocess.check_output(["git", "log", "-n", "1", "--skip=%i"%i, "--no-merges", "--format=%cr"],cwd="open_exoplanet_catalogue")
	    item=format_item(s,d)
	    print >>f, item
	print >>f, footer


ignored = """
<?
if(intval($_REQUEST["version"])<9964&&$_REQUEST["desktop"]!=1){
?>
<div class="newsitem">
<div class="blackmain">
<img src="new.png" alt="New version" class="blackimage"/>
Version 19.0.0 of the Exoplanet App is available as a free update with several new features. 
Please go to the AppStore and update the app.
</div>
<div class="blacksmall">Update made available on 16 February 2015. <a href="javascript:void(0)" onclick="share.call(this)"><img src="share_iphone.png">Share.</a></div>
</div>
<?}else{?>
<div class="newsitem">
<div class="blackmain">
<img src="new.png" alt="New version" class="blackimage"/>
Hurray! You are running the latest version of the Exoplanet App.
This version now includes images of near and far galaxies from the Hubble Space telescope and other observatories. This allows you to explore our extra-galactic neighbourhood in even more detail. Just go to the Milky-Way, zoom out (requires add-on) and enjoy the stunning views! 
</div>
<div class="blacksmall">Update made available on 9 February 2015. <a href="javascript:void(0)" onclick="share.call(this)"><img src="share_iphone.png">Share.</a></div>
</div>
<?}?>
"""
