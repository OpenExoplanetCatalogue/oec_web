function log10(val) {
	  return Math.log(val) / Math.LN10;
}
function MAX(val1,val2) {
	  return Math.max(val1,val2);
}
function MIN(val1,val2) {
	  return Math.min(val1,val2);
}


function getFormatForTag(tag){
	var error_plus 		= parseFloat(tag.attr("errorplus"));
	var error_minus 	= parseFloat(tag.attr("errorminus"));
	var upperlimit 		= parseFloat(tag.attr("upperlimit"));
	var lowerlimit 		= parseFloat(tag.attr("lowerlimit"));
	var value 		= parseFloat(tag.text());
	
	var hideErrors = false;
	var dataString;
	var exp0String;
	var exp1String;
	var exp2String;
	var errorMinusString;
	var errorPlusString;
	var errorString;

	var isExp = true;
	var exponent;
	var dexponent;
	if (!isNaN(value)){
		exponent = Math.floor(log10(value));
		dexponent = Math.pow(10, exponent);
	}else if (!isNaN(upperlimit)){
		exponent = Math.floor(log10(upperlimit));
		dexponent = Math.pow(10, exponent);
	}else if (!isNaN(lowerlimit)){
		exponent = Math.floor(log10(lowerlimit));
		dexponent = Math.pow(10, exponent);
	}else{
		return "<span class=\"NA\">N/A</span>";
	}

	if ((exponent>-4 && exponent<5) || (!isNaN(value) && value<=0.) ){
		isExp = false;
	}else{
		var diexponent = 1./dexponent;
		value		*=diexponent;
		error_minus	*=diexponent;
		error_plus	*=diexponent;
		upperlimit	*=diexponent;
		lowerlimit	*=diexponent;
	}

	var significantdigits = 2;
	if (!isNaN(value)){
		significantdigits = -Math.floor(log10(Math.abs(value/2.)));
		if (!isNaN(error_plus) && !isNaN(error_minus)){
			var error_significantdigits = MAX(-Math.floor(log10(error_plus/2.)),-Math.floor(log10(error_minus/2.)));
			significantdigits = MAX(error_significantdigits,significantdigits);
		}else{
			significantdigits +=2;
		}
	}else{
		//upper/lower limits
		significantdigits = 4;
	}
	significantdigits = MIN(significantdigits,4.);
	significantdigits = MAX(significantdigits,0.);

	var hasErrors = false;
	if ((!isNaN(error_plus) || !isNaN(error_minus)) && !hideErrors) hasErrors = true;


	if (!isNaN(value)){
		dataString = value.toFixed(significantdigits);
	}else{
		if (!isNaN(lowerlimit)){
			dataString = "&gt; "+lowerlimit.toFixed(significantdigits);
		}else if (!isNaN(upperlimit)){
			dataString = "&lt; "+upperlimit.toFixed(significantdigits);
		}
	}

	if (isExp){
		exp2String = exponent.toFixed(0);
		if (hasErrors){
			exp1String = " )&#183;10"
		}else{
			exp1String = " &#183;10"
		}
	}else{
		exp1String = "";
		exp2String = "";
	}

	if (hasErrors){
		if (!isNaN(error_minus)){
			errorMinusString = "&#8722;"+error_minus.toFixed(significantdigits);
		}else{
			errorMinusString = "";
		}
		if (!isNaN(error_plus)){
			errorPlusString = "&#43;"+error_plus.toFixed(significantdigits);
		}else{
			errorPlusString = "";
		}
		if (!isNaN(error_minus)&&!isNaN(error_minus)){
			if (errorMinusString.substring(7)==errorPlusString.substring(5)){
				errorString = "&#177;"+ errorMinusString.substring(7);
				errorMinusString = "";
				errorPlusString = "";
			}else{
				errorString = "";
			}
		}else{
			errorString = "";
		}

	}else{
		errorString		= "";
		errorMinusString	= "";
		errorPlusString		= "";
	}

	if (isExp && hasErrors){
		exp0String = "( ";
	}else{
		exp0String = "";
	}
	var returnString = "";
	returnString += exp0String;
	returnString += dataString;
	returnString += errorString;
	if (errorPlusString.length || errorMinusString.length){
		returnString += "<span class=\"errorbars\">";
		returnString += "<span class=\"errorplus\">"+errorPlusString+"</span>";
		returnString += "<span class=\"errorminus\">"+errorMinusString+"</span>";
		returnString += "</span>";
	}
	if (exp2String.length || exp1String.length){
		returnString += exp1String+"<sup>"+exp2String+"</sup>";
	}

	return returnString;
}
