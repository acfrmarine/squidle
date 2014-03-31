	var jwInfoIconSrc = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAACXBIWXMAAAsTAAALEwEAmpwYAAAA/ElEQVQokY2SwYmEQBBFXzWDIpiECQgjlYoxTBCzBw+zQZiNdxsFEzAJURCW2ou99MjK7r80Xbz6n+4qMTOCvPd34AEoUAED4IFWVcfAiZnRdd0tz/OnmTUigpnxy9nM8/yq6/rLAeR5/gSa4JRlGapKlmVEaoqi+ACQvu/vZjYAiAgASZJQliXTNLHvOwDhGSJS3YBHgIP2fcd7/1aLmIcDNP4MgDRNUVXSNH2rH5w6oDonOefO7vG9csBwTrrSwQ0O8GfHKx2cd0BrZvyVFjGtU9VRRH6GetUgIohIo6qjA1iW5ZNouOu64r1n27a4t5nn+QXHGgX9d/e+ARALfJbH3ASqAAAAAElFTkSuQmCC";
	var jwAppName = "SquidleDownloader";
	var jwIs64Bit = jwDetect64Bit();
	var jwInfoSrc;
	var jwUpdateURL;
	try
	{
		jwInfoSrc = "";		
	}
	catch (err){}	// Not required
	
	function translate(key) 
	{
		if (typeof translations === 'undefined') return key;
  		var result = translations[key];
  		if (result == null) return key;
  		return result;
  	}	
	
	function isMac()
	{
		return navigator.platform.indexOf("Mac") != -1;				
	}
	
	function isWindows()
	{
		return navigator.platform.indexOf("Win") != -1;
	}
	
	function isLinux()
	{
		return navigator.platform.indexOf("Linux") != -1 || navigator.platform.indexOf("X11") != -1;
	}
	
	function getHeadElement()
	{
		var elements = document.getElementsByTagName("head");
		if (elements.length > 0)
			return elements[0];
				
		var headElement = document.createElement('head');
		document.body.appendChild(headElement);
		return headElement;
  	}
	
	if (!window.getComputedStyle) 
	{
    	window.getComputedStyle = function(el, pseudo) 
    	{
        	this.el = el;
        	this.getPropertyValue = function(prop) 
        	{
            	var re = /(\-([a-z]){1})/g;
            	if (prop == 'float') prop = 'styleFloat';
            	if (re.test(prop)) 
            	{
                	prop = prop.replace(re, function () 
                	{
                    	return arguments[2].toUpperCase();
                	});
            	}
            	return el.currentStyle[prop] ? el.currentStyle[prop] : null;
        	}
        	return this;
    	}
	}
	
	function jwSwitch(switchTo)
	{			
		var recommendedLink = document.getElementById("jw_recommended");
		var offlineLink = document.getElementById("jw_allOffline");
		var onlineLink = document.getElementById("jw_allOnline");	
		var infoLink = document.getElementById("jw_infoDiv");		
		var appletDiv = document.getElementById("jw_appletDiv");
				
		if (switchTo == "recommended")
		{
			appletDiv.className = "jw_topPaddedDiv";
			
			showElement("jw_recommendedDiv1");
			showElement("jw_recommendedDiv2");
			showElement("jw_appletDiv");
			hideElement("jw_allOfflineDiv");
			hideElement("jw_allOnlineDiv");
			hideElement("jw_infoDiv");			
			
			recommendedLink.className = "jw_recommendedLink";
			offlineLink.className = "jw_Link";
			onlineLink.className = "jw_Link";										
		}
		else if (switchTo == "online")
		{
			appletDiv.className = "";
		
			hideElement("jw_recommendedDiv1");
			hideElement("jw_recommendedDiv2");
			showElement("jw_appletDiv");			
			hideElement("jw_allOfflineDiv");
			showElement("jw_allOnlineDiv");
			hideElement("jw_infoDiv");
			
			recommendedLink.className = "jw_Link";
			offlineLink.className = "jw_Link";
			onlineLink.className = "jw_recommendedLink";
		}
		else if (switchTo == "offline")
		{
			appletDiv.className = "";
			
			hideElement("jw_recommendedDiv1");
			hideElement("jw_recommendedDiv2");
			showElement("jw_appletDiv");			
			showElement("jw_allOfflineDiv");
			hideElement("jw_allOnlineDiv");
			hideElement("jw_infoDiv");
						
			recommendedLink.className = "jw_Link";
			offlineLink.className = "jw_recommendedLink";
			onlineLink.className = "jw_Link";					
		}	
		else if (switchTo == "info")
		{
			appletDiv.className = "";
			hideElement("jw_recommendedDiv1");
			hideElement("jw_recommendedDiv2");
			hideElement("jw_allOfflineDiv");
			hideElement("jw_allOnlineDiv");
			hideElement("jw_appletDiv");
			showElement("jw_infoDiv");
						
			recommendedLink.className = "jw_Link";
			offlineLink.className = "jw_Link";
			onlineLink.className = "jw_Link";					
		}
	}
	
	function jwConstructFilename(isOnline, os, postfix)
	{
		if (postfix == null)
			postfix = "";
			
		if (os == "mac")
		{
			return jwAppName+"-macos"+(jwIs64Bit ? "64" : "32")+"-"+(isOnline ? "online" : "offline")+".dmg"+postfix;
		}
		if (os == "windows")
		{
			return jwAppName+"-windows"+(jwIs64Bit ? "64" : "32")+"-"+(isOnline ? "online" : "offline")+".exe"+postfix;
		}
		if (os == "linux")
		{
			return jwAppName+"-linux"+(jwIs64Bit ? "64" : "32")+"-"+(isOnline ? "online" : "offline")+".tar"+postfix;
		}
	}
	
	function jwGetDetectedFilename(isOnline, postfix)
	{			
		// <App Name>-<OS><Arch>-<online/offline> (.exe/.dmg)
	
		if (isMac())
			return jwConstructFilename(isOnline, "mac", postfix);
		if (isWindows())
			return jwConstructFilename(isOnline, "windows", postfix);
		if (isLinux())
			return jwConstructFilename(isOnline, "linux", postfix);
		return null;
	}		
	
	function jwOpenLink(href, isRecommended)			
	{
		document.write("<a class='jw_cleanlink' href='"+href+"'>");
	}
	
	function jwCloseLink()
	{
		document.write("</a>");
	}
				
	function jwOpenButton(isRecommended, align, tag)
	{
		if (align == null)
			align = "left";
		document.write("<div align='"+align+"' class='jw_shadowedFont jw_roundBorder ");
		if (isRecommended)
			document.write("jw_buttonSelected jw_blueGradient");
		else
			document.write("jw_button jw_grayGradient");
		document.write("'");
		if (tag != null)
			document.write("id='"+tag+"'");
		document.write(">");	
	}
		
	function jwOpenAppletButton(isRecommended, imageURL, postFix)
	{		
		var	align = "left";
		document.write("<div id='jwAppletDiv' align='"+align+"' class='jw_shadowedFont jw_roundBorder ");
		if (isRecommended)
			document.write("jw_buttonSelected jw_blueGradient");
		else
			document.write("jw_button jw_grayGradient");			
			
		var escapedPostFix = postFix.replace(/'/g,"\\'");					
			
		document.write("' onclick=\"loadApplet(");
		document.write("'"+jwUpdateURL+"'");
		document.write(",");
		document.write("'"+jwAppName+"'");
		document.write(",");
		document.write("'"+isRecommended+"'");
		document.write(",");
		document.write("'"+imageURL+"'");
		document.write(",");
		document.write("'"+escapedPostFix+"','false');\"");		
		document.write(">");	
	}
	
	function jwCloseButton()
	{
		document.write("</div>");
	}
	
	function jwEmbedLogo(imageURL)
	{
		document.write("<div align='center'>");
		document.write("   <img class='jw_resizeImage' src='");		
		document.write(imageURL);
		document.write("'/>"); 
		document.write("</div>");
	}
	
	function jwAddAllOptions(os, type, urlPostfix)
	{
		var isRecommended = false;	
		var isOnline = type=="online";
			document.write("<tr>");
				document.write("<td class='jw_optionLabelCell' nowrap>");
					if (os == "windows") document.write("Windows");
					if (os == "mac") document.write("Mac OS");
					if (os == "linux") document.write("Linux");							
					if (type == "offline") document.write(" "+translate("Offline"));
					if (type == "online") document.write(" "+translate("Online"));							
				document.write("</td>");						
				document.write("<td class='jw_optionContentCell jw_nowrapCell'>");
					jwOpenLink(jwUpdateURL + jwConstructFilename(isOnline, false, os, urlPostfix), isRecommended);
						jwOpenButton(isRecommended, "center", null);	
							document.write("32bit");
						jwCloseButton();
					jwCloseLink();
				document.write("</td>");
				document.write("<td class='jw_optionContentCell jw_nowrapCell'>");
					jwOpenLink(jwUpdateURL + jwConstructFilename(isOnline, true, os, urlPostfix), isRecommended);
						jwOpenButton(isRecommended, "center", null);	
							document.write("64bit");
						jwCloseButton();
					jwCloseLink();
				document.write("</td>");																			
			document.write("</tr>");								
	}
	
	function jwAddSpecificDownloads(orders, type, urlPostfix)
	{
		document.write("<table class='jw_cleanFont jw_collapsedTable'>");
			jwAddAllOptions("windows", type, urlPostfix);
			jwAddAllOptions("linux", type, urlPostfix);
			jwAddAllOptions("mac", type, urlPostfix);					
		document.write("</table>");
	}
	
	var appletIsLoaded = false;
	
	function getRequiredHeight()
	{
		var standaloneDiv = document.getElementById('jwOfflineButton');
		if (standaloneDiv != null && standaloneDiv.clientHeight > 0)
			return standaloneDiv.clientHeight - 4;
		standaloneDiv = document.getElementById('jwOnlineButton');
		if (standaloneDiv != null && standaloneDiv.clientHeight > 0)
			return standaloneDiv.clientHeight - 4;
		return 21;
	}
	
	function getRequiredWidth()
	{
		var standaloneDiv = document.getElementById('jwOfflineButton');
		if (standaloneDiv != null && standaloneDiv.clientWidth > 0)
			return standaloneDiv.clientWidth - 4;
		standaloneDiv = document.getElementById('jwOnlineButton');
		if (standaloneDiv != null && standaloneDiv.clientWidth > 0)
			return standaloneDiv.clientWidth - 4;
		return 254;
	}
	
	function loadApplet(isRecommended, imageURL, postFix, autoRun)
	{
		if (appletIsLoaded)
			return;
		appletIsLoaded = true;
		
		var height = getRequiredHeight();		
		var width = getRequiredWidth();
		
		var appletDivElement = document.getElementById('jwAppletDiv');
		
		// Disable the onclick behaviour
		appletDivElement.onclick = '';
		appletDivElement.style.padding = '2px';
		
		var appletContent = jwEmbedApplet(width, height, imageURL, postFix, autoRun);
		appletDivElement.innerHTML = appletContent;
	}
	
	function jwEmbedApplet(width, height, imageURL, postFix, autoRun)
	{		
		if (jwUpdateURL.charAt(jwUpdateURL.length-1) == '/')
			jwUpdateURL = jwUpdateURL.substring(0, jwUpdateURL.length-1);
	
		var appletDivElement = document.getElementById('jwAppletDiv');
		
		var style = window.getComputedStyle(appletDivElement, null);		
		var bg = style.background;
		var topColor = "";
		var bottomColor = "";
		if (bg != null)
		{
			var gradientIndex = bg.indexOf('gradient');
			
			var open1 = bg.indexOf('rgb', gradientIndex);
			var close1 = bg.indexOf(')', open1);
	
			var open2 = bg.indexOf('rgb', close1);
			var close2 = bg.indexOf(')', open2);
	
			topColor = bg.substring(open1, close1+1);
			bottomColor = bg.substring(open2, close2+1);
		}		
		
		var additionalParameters = "";
		var language = "en";
		var parameterList = "";
		if (postFix != null && postFix.length > 0)
		{		
			var splitPostFix = postFix.split('&');
			for (var i=0; i<splitPostFix.length; i++)
			{	
				var equalsIndex = splitPostFix[i].indexOf('=');					
				if (equalsIndex != -1)
				{
					var name = splitPostFix[i].substring(0,equalsIndex);
					var value = splitPostFix[i].substring(equalsIndex+1);
					
					if (name.indexOf('?') == 0)	name = name.substring(1);
					additionalParameters += "<param name='"+name+"' value='"+value+"' />";
					if (parameterList.length > 0)
						parameterList += ",";
					parameterList += name;
					
					if (name == "language")
						language = value;
				}
				else 
				{
					var name = splitPostFix[i]
					if (name.indexOf('?') == 0)	name = name.substring(1);
					additionalParameters += "<param name='"+name+"' value='' />";
					if (parameterList.length > 0)
						parameterList += ",";
					parameterList += name;
				}
			}						
		}
		
		if (!(typeof addAppParams === 'undefined'))
		{
			for (key in addAppParams)
			{
				additionalParameters += "<param name='"+key+"' value='"+addAppParams[key]+"' />";
				if (parameterList.length > 0)
					parameterList += ",";
				parameterList += key;
			}
		}
		
		if (parameterList.length > 0)
			additionalParameters += "<param name='jwParameterList' value='"+parameterList+"' />";		
		
		var appletContent = "";		
		
		appletContent += "<!--[if !IE]> -->";
      	appletContent += "<object classid='java:jwrapper.appletwrapper.JWAppletWrapper.class' "; 
		appletContent += "        type='application/x-java-applet' ";
		appletContent += "        archive='SquidleDownloaderApplet.jar,SquidleDownloaderApplet_sz.jar' ";
		appletContent += "        height='"+height+"' width='"+width+"' >";
		
		// Add in the archive here.
		appletContent += "  			<param name='archive' value='";
		var jars = 'SquidleDownloaderApplet.jar,SquidleDownloaderApplet_sz.jar'.split(",");
		for (var i=0; i<jars.length; i++)
		{
			if (i > 0)
				appletContent += ",";
			appletContent += jwUpdateURL+"/"+jars[i];
		}
		appletContent += "' />";
		
		appletContent += "  	<param name='persistState' value='false' />";
		appletContent += "  	<param name='update_url' value='"+jwUpdateURL+"' />";
		appletContent += "  	<param name='app_name' value='"+jwAppName+"' />";
		if (imageURL != null)
			appletContent += "  	<param name='splash_image' value='"+imageURL+"' />";
		if (autoRun != null)
			appletContent += "  	<param name='auto_run' value='"+autoRun+"' />";
			
		appletContent += "  	<param name='supported_langs' value='"+language+"' />";			
		appletContent += "  	<param name='gradientTop' value='"+topColor+"' />";
		appletContent += "  	<param name='gradientBottom' value='"+bottomColor+"' />";
		appletContent += "  	<param name='name' value='"+jwAppName+"' />";
		
		if (autoRun != null && autoRun == "true")
			appletContent += "  	<param name='txt_launchnow' value='"+translate("Loading")+" "+jwAppName+"...' />";
		else
			appletContent += "  	<param name='txt_launchnow' value='"+translate("Start")+" "+jwAppName+"' />";
		
		appletContent += additionalParameters;
		
      	appletContent += "<!--<![endif]-->";
      	
        appletContent += "		<object classid='clsid:8AD9C840-044E-11D1-B3E9-00805F499D93' "; 
        appletContent += "				codebase='http://javadl.sun.com/webapps/download/GetFile/1.7.0_21-b11/windows-i586/xpiinstall.exe#Version=1,4,0,0' ";
        appletContent += "        		height='"+height+"' width='"+width+"' >";        
        // Note that we specify the class here only for IE.
        appletContent += "  			<param name='code' value='jwrapper.appletwrapper.JWAppletWrapper.class' />";		
        
        // Add in the archive here.
        // Add in the archive here.
		appletContent += "  			<param name='archive' value='";
		var jars = 'SquidleDownloaderApplet.jar,SquidleDownloaderApplet_sz.jar'.split(",");
		for (var i=0; i<jars.length; i++)
		{
			if (i > 0)
				appletContent += ",";
			appletContent += jwUpdateURL+"/"+jars[i];
		}
		appletContent += "' />";
		
		appletContent += "  			<param name='persistState' value='false' />";
		appletContent += "  			<param name='update_url' value='"+jwUpdateURL+"' />";
		appletContent += "			  	<param name='app_name' value='"+jwAppName+"' />";
		if (imageURL != null)
			appletContent += "  		<param name='splash_image' value='"+imageURL+"' />";
		if (autoRun != null)
			appletContent += "  		<param name='auto_run' value='"+autoRun+"' />";
			
		appletContent += "  			<param name='supported_langs' value='"+language+"' />";			
		appletContent += "  			<param name='gradientTop' value='"+topColor+"' />";
		appletContent += "  			<param name='gradientBottom' value='"+bottomColor+"' />";
		appletContent += "              <param name='name' value='"+jwAppName+"' />";
        
		if (autoRun != null && autoRun == "true")
			appletContent += "  			<param name='txt_launchnow' value='"+translate("Loading")+" "+jwAppName+"...' />";
		else
			appletContent += "  			<param name='txt_launchnow' value='"+translate("Start")+" "+jwAppName+"' />";

		
		appletContent += additionalParameters;
			        
        appletContent += "		</object> ";
        appletContent += "<!--[if !IE]>--> ";
      	appletContent += "</object> ";
      	appletContent += "<!--<![endif]--> ";    	
				
		return appletContent;		
	}
	
	function jwStringHostnameFrom(url)
	{
		var doubleSlash = url.indexOf("://");
		if (doubleSlash != -1)
		{
			var nextSlash = url.indexOf("/", doubleSlash+3);
			return url.substring(0, nextSlash);
		}
		else
		{
			var nextSlash = url.indexOf("/");
			return url.substring(0, nextSlash);
		}
	}
	
	function jwAddOfflineButton(id, postfix, isRecommended)
	{
		document.write("<div id='"+id+"' class='jw_topPaddedDiv'>");
			jwOpenLink(jwUpdateURL+jwGetDetectedFilename(false, postfix), isRecommended);
				jwOpenButton(isRecommended, null, "jwOfflineButton");	
					document.write(translate("Download Full Installer"));
				jwCloseButton();
			jwCloseLink();
		document.write("</div>");
	}
	
	function jwAddOnlineButton(id, postfix, isRecommended)
	{		
		document.write("<div id='"+id+"' class='jw_topPaddedDiv'>");
			jwOpenLink(jwUpdateURL+jwGetDetectedFilename(true, postfix), isRecommended);
				jwOpenButton(isRecommended, null, "jwOnlineButton");
					document.write(translate("Download")+" "+jwAppName);
				jwCloseButton();
			jwCloseLink();
		document.write("</div>");				
	}
	
	function jwAddAppletButton(id, postfix, isRecommended, imageURL)
	{
		document.write("<div id='"+id+"' class='jw_topPaddedDiv'>");
			jwOpenAppletButton(isRecommended, imageURL, postfix);						
				document.write(translate("Launch using Java"));								
			jwCloseButton();
		document.write("</div>");
	}	
	
	function hideElement(divID)
	{
		var element = document.getElementById(divID);
		if (element != null)
			element.style.display='none';
	}
	
	function showElement(divID)
	{
		var element = document.getElementById(divID);
		if (element != null)
			element.style.display='block';
	}
	
	function jwAddInfoDiv(jwAppName)
	{
		if (!jwInfoSrc || jwInfoSrc.length == 0)
			jwInfoSrc = "Powered by<br><br>JWrapper <a href=\"http://jwrapper.com\">Java Installer</a>";
		document.write(jwInfoSrc);
	}
	
	function processPostFix(postFix)
	{
		var hostname = jwStringHostnameFrom(jwUpdateURL);
		if (postFix.length == 0)
			postFix = "?hostname="+encodeURIComponent(hostname);
		else
		{
			postFix = postFix + "&hostname="+encodeURIComponent(hostname);
			if (postFix[0] != '?') postFix = '?'+postFix;
		}
		return postFix;
	}
	
	function jwEmbedDeploymentOptions(orderConfiguration, showInfo, imageURL, postFix)
	{
		var orders = orderConfiguration.split(",");
		var runApplet = false;
		
		postFix = processPostFix(postFix);
					
		// This is the main div that is shown the first time
		document.write("<div style='padding-top: 1px' id='jw_onlyRecommededDiv' class='jw_cleanFont'>");
		
			for (var i=0; i<orders.length; i++)
			{
				var current = orders[i];
				var isRecommended = current.indexOf("*") != -1;
				if (!isRecommended)
					continue;							
				if (current.indexOf("offline") != -1)
					jwAddOfflineButton("", postFix, isRecommended);
				else if (current.indexOf("online") != -1)
					jwAddOnlineButton("", postFix, isRecommended);
				else if (current.indexOf("applet") != -1)
				{				
					jwAddAppletButton("", postFix, isRecommended, imageURL);
					if (current.indexOf("applet_run") != -1)
						runApplet = true;	
				}
				else
					document.write("Warning: unknown configuration entry '"+current+"'");
			}
			
			document.write("<div class='jw_cleanFont' style='padding-top: 10px'>");
				document.write("<span id='jw_allDownloads' onclick='hideElement(\"jw_onlyRecommededDiv\"); showElement(\"jw_mainDiv\"); ' class='jw_Link'>");
				document.write(translate("All Downloads"));
				document.write("</span>");
			document.write("</div>");
		document.write("</div>");
		
		// This is the set of 3 buttons with links shown as alternatives
		document.write("<div style='display:none;' id='jw_mainDiv'>");
			document.write("<div style='display:none;' id='jw_allOnlineDiv'>");				
				jwAddSpecificDownloads(orders, "online", postFix);
			document.write("</div>");
			document.write("<div style='display:none;' id='jw_allOfflineDiv'>");				
				jwAddSpecificDownloads(orders, "offline", postFix);
			document.write("</div>");
			document.write("<div style='display:none;' id='jw_infoDiv' class='jw_mediumFont jw_roundBorder jw_cleanFont'>");	
				jwAddInfoDiv(jwAppName);
			document.write("</div>");
							
			document.write("<div style='padding-top: 1px' class='jw_cleanFont'>");				
				for (var i=0; i<orders.length; i++)
				{
					var current = orders[i];
					var isRecommended = current.indexOf("*") != -1;
					if (current.indexOf("offline") != -1)
						jwAddOfflineButton("jw_recommendedDiv1", postFix, isRecommended);
					else if (current.indexOf("online") != -1)
						jwAddOnlineButton("jw_recommendedDiv2", postFix, isRecommended);
					else if (current.indexOf("applet") != -1)
						jwAddAppletButton("jw_appletDiv", postFix, isRecommended, imageURL);				
					else
						document.write("Warning: unknown configuration entry '"+current+"'");
				}
			document.write("</div>");
			
			// Include the links table in this div since we have the 'Alternative Downloads' link above
			jwEmbedSwitcherLinks(showInfo);
						
		document.write("</div>");
		
		if (runApplet)
			loadApplet(isRecommended, imageURL, postFix, true)		
	}
	
	function jwEmbedWithSettings(configuration, imageURL, showjwAppName, showInfo, postFix)
	{
		// This adds a style node which hides the main div
		// until the lazily loaded styles are fetched, after which the div is shown.
		// This prevents the unstyled content from being shown.
		var css = document.createElement('style');
		css.type = 'text/css';
		var styles = 'div#jw_topLevelMainDiv {display:none;}';
		if (css.styleSheet) css.styleSheet.cssText = styles;
		else css.appendChild(document.createTextNode(styles));

		getHeadElement().appendChild(css);
		
		document.write("<div id='jw_topLevelMainDiv' class='jw_cleanFont jw_mainDiv'>");
			if (imageURL != null)
				jwEmbedLogo(imageURL);
			if (showjwAppName)
			{
				document.write("<div class='jw_appName'>");
				document.write(jwAppName);
				document.write("</div>");
			}
				
			jwEmbedDeploymentOptions(configuration, showInfo, imageURL, postFix);						
		document.write("</div>");
	}
	
	function jwEmbedSwitcherLinks(showInfo)
	{
		document.write("<div align='center' style='padding-top:10px'>");
			document.write("<table class='jw_collapsedTable jw_smallerLink'>");
				document.write("<tr>");
					if (showInfo)
					{
						document.write("<td class='jw_nowrapCell jw_leftEdgeCell'>");
						document.write("</td>");
					}
					document.write("<td class='jw_nowrapCell'>");
						document.write("<span id='jw_recommended' onclick='jwSwitch(\"recommended\");' class='jw_recommendedLink'>");
						document.write(translate("Recommended"));
						document.write("</span>");
					document.write("</td>");
					document.write("<td class='jw_nowrapCell' >");
						document.write("<span class='jw_lightFont''>|</span>");
					document.write("</td>");
					document.write("<td class='jw_nowrapCell'>");
						document.write("<span id='jw_allOnline' onclick='jwSwitch(\"online\");' class='jw_Link'>");
						document.write(translate("All Online"));
						document.write("</span>");
					document.write("</td>");
					document.write("<td class='jw_nowrapCell'>");
						document.write("<span class='jw_lightFont'>|</span>");
					document.write("</td>");
					document.write("<td class='jw_nowrapCell'>");
						document.write("<span id='jw_allOffline' onclick='jwSwitch(\"offline\");' class='jw_Link'>");
						document.write(translate("All Offline"));
						document.write("</span>");
					document.write("</td>");
					if (showInfo)
					{
						document.write("<td class='jw_nowrapCell jw_rightEdgeCell'>");
							document.write("<img id='jw_infoButton' class='jw_Link' src='"+jwInfoIconSrc+"' onclick='jwSwitch(\"info\");'/>");
						document.write("</td>");
					}
				document.write("</tr>");
			document.write("</table>");
		document.write("</div>");
	}
	
	function jwGetJavascriptjwUpdateURL(scriptElement)
	{
		var jwUpdateURL = scriptElement.getAttribute('jwUpdateURL');
		if (jwUpdateURL != null)
			return jwUpdateURL;
		var url = scriptElement.getAttribute('src');
		if (url == null || url.charAt(0) == '/')
		{
			var browserURL = document.location.href;
			if (browserURL.indexOf("://") == -1)
			{
				var protocol = document.location.protocol;
				if (protocol == null || protocol.length == 0)
					protocol = "http";
				browserURL = protocol+"://"+browserURL;
			}
						
			url = jwStringHostnameFrom(browserURL) + url;
		} 
			
		var lastSlash = url.lastIndexOf('/');
		if (lastSlash != -1)
			return url.substring(0, lastSlash+1);
		return url;
	}
	
	function jwGetImageURL(scriptElement, jwUpdateURL)
	{
		var imageURL = scriptElement.getAttribute('imageURL');
		if (imageURL != null)
		{
			if (imageURL.charAt(0) == '/')
			{
				// Relative URL
				var jwUpdateURLHostname = jwStringHostnameFrom(jwUpdateURL);
				return jwUpdateURLHostname+imageURL;
			}
			else
			{
				// Absolte URL is OK - don't add on a host				
			}
		}
		else
		{
			// If there is no custom URL use the JWrapper default
			imageURL = jwUpdateURL+"/JWrapper-"+jwAppName+"-splash.png";
		}
		
		if (jwGetShowImage(scriptElement))
			return imageURL;
		return null;
	}
	
	function jwGetShowjwAppName(scriptElement)
	{
		var showImage = scriptElement.getAttribute('showjwAppName');
		if (showImage != null)
		{
			if (showImage == 'no' || showImage == 'false')
				return false;
			return true;
		}
		return true;
	}
	
	function jwGetShowInfo(scriptElement)
	{
		var showImage = scriptElement.getAttribute('showInfo');
		if (showImage != null)
		{
			if (showImage == 'no' || showImage == 'false')
				return false;
			return true;
		}
		return true;
	}
	
	function jwGetShowImage(scriptElement)
	{
		var showImage = scriptElement.getAttribute('showImage');
		if (showImage != null)
		{
			if (showImage == 'no' || showImage == 'false')
				return false;
			return true;
		}
		return true;
	}
	
	function jwGetCSSLink(scriptElement)
	{
		var url = scriptElement.getAttribute('src');
		var jsIndex = url.lastIndexOf('js');
		url = url.substring(0, jsIndex) + "css";
		return url;
	}
		
	function jwGetJavascriptConfiguration(scriptElement)
	{
		var config = scriptElement.getAttribute('configuration');
		if (config == null)
			return "online*,offline,applet";
		return config;		
	}
	
	function jwLoadCSSDynamically(cssLink)
	{
		var fileref = document.createElement("link");
  		fileref.setAttribute("rel", "stylesheet");
  		fileref.setAttribute("type", "text/css");
  		fileref.setAttribute("href", cssLink);
  		getHeadElement().appendChild(fileref);  		
 	}
 	
 	function jwDetect64Bit()
 	{
 		var agent = navigator.userAgent;
 	
 		if (isMac())
   		{   			
   			var regex = /Mac OS X (\d+)[\.\_](\d+)[\.\_]?(\d*)/g;
   			var myArray = regex.exec(agent);
   			if (myArray.length == 3)
   			{
   				if (myArray[1] > 10) return true;
   				if (myArray[1] == 10 && myArray[2] > 7) return true;
   			}
   			else if (myArray.length == 4)
   			{
   			   	if (myArray[1] > 10) return true;
   				if (myArray[1] == 10 && myArray[2] > 7) return true;
   				if (myArray[1] == 10 && myArray[2] > 7 && myArray[3] >= 3) return true;
   			}
   			return false;
   		}
 	
 		if (agent.indexOf("WOW64") != -1 || 
    		agent.indexOf("Win64") != -1 ||
    		agent.indexOf("x86_64") != -1)
    	{
   			return true;
   		}
   		   		
   		if (navigator.cpuClass != null && navigator.cpuClass.indexOf("64") != -1)
   			return true;
   			
   		return false;
	} 
	function jwGetExistingPostFix(scriptElement)
	{
		var url = scriptElement.getAttribute('src');
		var jsIndex = url.lastIndexOf('.js');
		var postFix = url.substring(jsIndex+3);
		if (postFix.length > 0 && postFix[0] == '?')
			postFix = postFix.substring(1);
			
			
		var existingParameters = document.location.search;
		if (existingParameters.length == 0)
			return postFix;
		else
		{
			if (existingParameters[0] == '?')
				existingParameters = existingParameters.substring(1);
			if (postFix.length > 0)
				return postFix+"&"+existingParameters;
			else
				return existingParameters;
		}
	}
	
	function getOSDependentFilename(isOnline)
	{
		var scriptElementLink = document.getElementById('jwLink');
		var postFix = jwGetExistingPostFix(scriptElementLink);	
		postFix = processPostFix(postFix);
		return jwUpdateURL+jwGetDetectedFilename(false, postFix);
	}
	
	function jwEmbed()
	{
		var scriptElement = document.getElementById('jwEmbed');
		var scriptElementLink = document.getElementById('jwLink');
		if (scriptElement != null)
		{
			jwUpdateURL = jwGetJavascriptjwUpdateURL(scriptElement);
			var configuration = jwGetJavascriptConfiguration(scriptElement);
			if (configuration == null)
				return false;
			var cssLink = jwGetCSSLink(scriptElement);
			var imageURL = jwGetImageURL(scriptElement, jwUpdateURL, jwAppName);
			var showjwAppName = jwGetShowjwAppName(scriptElement);
			var showInfo = jwGetShowInfo(scriptElement);
			var postFix = jwGetExistingPostFix(scriptElement);	
			
			if (typeof jwInfoSrc === 'undefined' || jwInfoSrc.length == 0) showInfo = false;
			
			jwEmbedWithSettings(configuration, imageURL, showjwAppName, showInfo, postFix);
			jwLoadCSSDynamically(cssLink);
		}
		else if (scriptElementLink != null)
		{
			jwUpdateURL = jwGetJavascriptjwUpdateURL(scriptElementLink);
		}
	}
	
	// jwEmbed();
	
	
	