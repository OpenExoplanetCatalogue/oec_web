
var M_PI 	= 3.1415926535897; // C constant
var scale 	= 0;
var width 	= 400;
var height 	= 300;
var planets;
var speed 	= 0.5;
var minperiod 	= 100000000;
var zoom 	= 0;
var t 		= 0;

function get2DPositionofPlanet(planet,time){
	//if (!self.root) return GLKVector2Make(0, 0); // orphan planets
	

	var longitude 		= parseFloat($("longitude",planet).text())/180.*M_PI;
	if (isNaN(longitude)) longitude = 0.0;
	var ascendingnode 	= parseFloat($("ascendingnode",planet).text())/180.*M_PI;
	if (isNaN(ascendingnode)) ascendingnode = 0.0;
	var semimajoraxis 	= parseFloat($("semimajoraxis",planet).text());
	if (isNaN(semimajoraxis)) semimajoraxis = 0.0;
	var periastron 		= parseFloat($("periastron",planet).text())/180.*M_PI;
	if (isNaN(periastron)) periastron = 0.0;
	var period 		= parseFloat($("period",planet).text());
	if (isNaN(period)) period = 0.0;
	var eccentricity 	= parseFloat($("eccentricity",planet).text());
	if (isNaN(eccentricity)) eccentricity = 0.0;
	
	var M = longitude - periastron; 		// Mean anomaly
	if (period){
		M += 2.*M_PI*time/period;
	}else{
		M += 2.*M_PI*time/365.; 		// assume default period: 1 year
	}
	var E = M+eccentricity*Math.sin(M);		// Eccentric anomaly
	var deltaE = 0;
	var counter = 15;
	do{
		deltaE = (E - eccentricity*Math.sin(E)- M)/(1.-eccentricity*Math.cos(E));
		E -= deltaE;
		counter--;
	}while (Math.abs(deltaE)>1e-4 && counter);
	
	var _a = 1;
	if (semimajoraxis>0) _a = semimajoraxis;
	
	var xp =_a*(Math.cos(E)-eccentricity);
	var yp =_a*Math.sqrt(1.-eccentricity*eccentricity) * Math.sin(E);
	
	var sinNodengle = Math.sin(ascendingnode);
	var cosNodengle = Math.cos(ascendingnode);
	 var sinArgPeri = Math.sin(periastron-ascendingnode);
	var cosArgPeri = Math.cos(periastron-ascendingnode);
	
	var point = {
		"x": xp*(cosArgPeri*cosNodengle-sinArgPeri*sinNodengle) + yp*(-sinArgPeri*cosNodengle-cosArgPeri*sinNodengle),
		"y": xp*(cosArgPeri*sinNodengle+sinArgPeri*cosNodengle) + yp*(-sinArgPeri*sinNodengle+cosArgPeri*cosNodengle),
	};
	point.x = point.x * scale * Math.pow(10,zoom)+ width/2.;
	point.y = point.y * scale * Math.pow(10,zoom) + height/2.;
	return point;
}

function getPathForPlanet(planet){
	var period = parseFloat($("period",planet).text());
	var N = 64.;
	var point = get2DPositionofPlanet(planet,0);
	var path = "M "+ point.x+ " " + point.y;
	for (var i=1.; i<N;i++){
		var point = get2DPositionofPlanet(planet,period*i/N);
		path = path + " L "+ point.x+ " " + point.y;
	}
	return path + " Z";
}

function redrawOrbits(){
	var viz = d3.select("#viz").select("svg");
	viz.selectAll("path").remove();
	for (var i=0;i<planets.length;i++){
		viz.insert("path",":first-child")
			.attr("d",getPathForPlanet(planets[i]))
			.attr("stroke-width",1)
			.attr("stroke","lightgray")
			.attr("fill","none");
	}
}

function setupOrbitPlot(xml){
	planets = $(xml).find("planet");
	d3.select("#sliderbox").style("width",width+"px");
	new Dragdealer('speed-slider',{
		slide: false,
		x: speed,
		animationCallback: function(x, y){
			speed = x;
		}
	});
	new Dragdealer('zoom-slider',{
		slide: false,
		x: zoom,
		animationCallback: function(x, y){
			zoom = x;
			redrawOrbits();
		}
	});
	var viz = d3.select("#viz")
		.append("svg")
		.attr("width", width)
		.attr("height", height);
	for (var i=0;i<planets.length;i++){
		var planet = planets[i];
		var a = parseFloat($("semimajoraxis",planet).text());
		var eccentricity = parseFloat($("eccentricity",planet).text());
		if (isNaN(eccentricity)) eccentricity = 0.0;
		var period = parseFloat($("period",planet).text());
		var starmass = parseFloat($($(planet.parentNode).children("mass")[0]).text());
		if ((isNaN(period) || period<=0.) && a>0.){
			if (starmass>0.){
				period = 2.*M_PI*Math.sqrt(a*a*a*3378.2183/starmass);
			}else{
				period = 2.*M_PI*Math.sqrt(a*a*a*3378.2183); // Assume solar mass;
			}
			d3.select(planet).append("period").text(period);
		}
		if ((isNaN(a) || a<=0.) && period>0.){
			if (starmass>0.){
				a = Math.pow(period*period/4./M_PI/M_PI*0.00029601403*starmass, 1./3.); 
			}else{
				a = Math.pow(period*period/4./M_PI/M_PI*0.00029601403, 1./3.); // Assume solar mass
			}
			d3.select(planet).append("semimajoraxis").text(a);
		}

		var ae = a*(1.+eccentricity);
		if (ae>scale){
			scale = ae;
		}
		if (period<minperiod){
			minperiod = period;
		}
	}
	scale = (height/2.)/scale * 0.95;
	redrawOrbits();
	viz.append("image")
		.attr("width","22")
		.attr("height","22")
		.attr("xlink:href","./img/star.png")
		.attr("x", width/2.-11)
		.attr("y", height/2.-11);


	setInterval(function() {
		t = t + minperiod/100.*Math.pow(10.,4.*(speed-0.5));
		updatePlot();
	}, 17);
}




function updatePlot(){ 
	var dots = d3.select("#viz").select("svg").selectAll("g")
			.data(planets);
	var newdots = dots.enter().append("g");
	
	newdots.append("circle")
		.attr("r",function(planet){
			var m = parseFloat($("mass",planet).text());
			return width/80.*Math.pow(m,1./3.);
		});

	newdots.append("text")
		.attr("x",function(planet){
			var m = parseFloat($("mass",planet).text());
			return width/80.*Math.pow(m,1./3.);
		})
		.attr("y",function(planet){
			var m = parseFloat($("mass",planet).text());
			return -width/80.*Math.pow(m,1./3.);
		})
		.text(function(planet){
			return $("name",planet).first().text();
			});
	
	dots
		.attr("transform",function(planet){
			var point =get2DPositionofPlanet(planet,t);
			return "translate("+point.x+","+point.y+")";
			});
		
	dots.select("circle")
		.attr("transform",function(planet){
			var a = parseFloat($("semimajoraxis",planet).text());
			var e = parseFloat($("eccentricity",planet).text());
			var peri = parseFloat($("paeriastron",planet).text()); //degrees
			var ascendingnode 	= parseFloat($("ascendingnode",planet).text())/180.*M_PI;
			return "rotate("+(peri-ascendingnode)+","+width/2.+","+height/2.+")";
			});

	dots.exit().remove();
};
