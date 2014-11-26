#############################################
##       MAIN HANDLER FILE FOR VIEWS       ##
#############################################
import os
import cgi
import config
import ee
import jinja2
import webapp2
import datetime
import numpy
import json
import httplib2 

from forms import *
import collectionMethods
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)
httplib2.Http(timeout=15)

#############################################
##       SET DIRECTORY FOR PAGES          ##
#############################################
template_dir = os.path.join(os.path.dirname(__file__),'templates')
JINJA_ENVIRONMENT= jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(template_dir))

#############################################
##       HOME PAGE                         ##
#############################################
class MainPage(webapp2.RequestHandler):
    def get(self):   
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.out.write(template.render({}))

#############################################
##       DROUGHT TOOL PAGE                 ##
#############################################
class DroughtTool(webapp2.RequestHandler):
	#############################################
	##      GET                                ##
	#############################################
    def get(self): 
	ppost=0	
        ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)

	#initialize forms
	mapzoom=4
	pointLat = 39.0510 
	pointLong = -98.0250
	state ='Washington'
	variable = 'NDVI'
	domainType = 'full'
	dateStart ='2013-01-01' 
	dateEnd='2013-03-31'
	anomOrValue='anom'
	opacity=str(17*0.05);

        template_values = {
	    'opacity': opacity,
	    'pointLat': pointLat,
	    'pointLong': pointLong,
	    'ppost': ppost,
	    'mapzoom': mapzoom,
	    'variable': variable,
	    'state': state,
	    'domainType': domainType,
	    'anomOrValue': anomOrValue,
	    'dateStart': dateStart,
	    'dateEnd': dateEnd,
	    'anomOrValue': anomOrValue,
	    'formOpacity': formOpacity,
	    'formAnomOrValue': formAnomOrValue,
	    'formVariableGrid': formVariableGrid,
	    'formLocation': formLocation,
	    'formVariableLandsat': formVariableLandsat,
	    'formStates': formStates,
        }
        template = JINJA_ENVIRONMENT.get_template('droughttool.php')
        self.response.out.write(template.render(template_values))

    def post(self):
	ppost=1
        ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)

	#Get data from form
        opacity= self.request.get('opacity')
        dateStart= self.request.get('dateStart')
        dateEnd = self.request.get('dateEnd')
	variable =self.request.get('basicvariable')
	domainType =self.request.get('domainType')
	state=self.request.get('state')
	anomOrValue=self.request.get('anomOrValue')

        pointLatLong = self.request.get('pointLatLong')
        pointLatLongX = pointLatLong.split(",")
        pointLong = float(pointLatLongX[0])
        pointLat = float(pointLatLongX[1])
	#pointLong =float(cgi.escape(self.request.get('pointLong')))
	#pointLat=float(cgi.escape(self.request.get('pointLat')))

	collection,collectionName,collectionLongName,product,variableShortName,notes,statistic= collectionMethods.get_collection(variable);
	title=statistic +' ' +variableShortName;
	if(anomOrValue=='anom'):
		title=title+' Anomaly from Climatology ';
	source=collectionLongName+' from '+dateStart+'-'+dateEnd+''

   	if(domainType=='states'):
                subdomain=state;
                mapzoom=4; #would like to zoom in on that state
        elif(domainType=='full' and product=='modis'):
                subdomain = ee.Feature.Point(pointLong,pointLat);
                point = subdomain;
                mapzoom=2; 
        else:
                subdomain = ee.Feature.Point(pointLong,pointLat);
                point = subdomain;
                mapzoom=4;



	collection = ee.ImageCollection(collectionName).filterDate(dateStart,dateEnd).select([variable],[variable]);

	template_values = {
	}
	#if points selected, get timeseries before calculate statistic
#	if(domainType=='points'):
#		#timeSeriesData,timeSeriesGraphData,template_values = collectionMethods.callTimeseries(collection,variable,domainType,point)
#		timeSeriesData=collectionMethods.get_timeseries(collection,point,variable)
#		timeSeriesGraphData = []	
#		n_rows = numpy.array(timeSeriesData).shape[0];
#		for i in range(2,n_rows):
#		  entry = {'count':timeSeriesData[i][1],'name':timeSeriesData[i][0]};
#		  timeSeriesGraphData.append(entry);
#
#		template_values = {
#		    'timeSeriesData': timeSeriesData,
#		    'timeSeriesGraphData': timeSeriesGraphData,
#		}

 	collection = collectionMethods.get_statistic(collection,variable,statistic,anomOrValue);
	collection =collectionMethods.filter_domain2(collection,domainType,subdomain)

	if(anomOrValue=='anom' or anomOrValue=='clim'):
		collection,climatologyNotes = collectionMethods.get_anomaly(collection,product,variable,collectionName,dateStart,dateEnd,statistic,anomOrValue);
	        template_values={'climatologyNotes': climatologyNotes,};

	#the earth engine call
	mapid =collectionMethods.map_collection(collection,variable,anomOrValue,opacity)

	extra_template_values = {
	    'opacity': opacity,
	    'pointLat': pointLat,
	    'pointLong': pointLong,
	    'product': product,
	    'productLongName': collectionLongName,
	    'notes': notes,
	    'variable': variable,
	    'state': state,
	    'domainType': domainType,
	    'dateStart': dateStart,
	    'dateEnd': dateEnd,
	    'anomOrValue': anomOrValue,
	    'ppost': ppost,
	    'title': title,
	    'source': source,
	    'mapzoom': mapzoom,
	    'mapid': mapid['mapid'],
	    'token': mapid['token'],
	    'formOpacity': formOpacity,
	    'formAnomOrValue': formAnomOrValue,
	    'formVariableGrid': formVariableGrid,
	    'formLocation': formLocation,
	    'formVariableLandsat': formVariableLandsat,
	    'formStates': formStates,
	}
	template_values = dict(template_values,**extra_template_values);

        template = JINJA_ENVIRONMENT.get_template('droughttool.php')
        self.response.out.write(template.render(template_values))

#############################################
##       CONTACT PAGE                      ##
#############################################
class ContactPage(webapp2.RequestHandler):
    def get(self):   
        template = JINJA_ENVIRONMENT.get_template('contact.html')
        self.response.out.write(template.render({}))

#############################################
##       ABOUT DATA PAGE                   ##
#############################################
class DataPage(webapp2.RequestHandler):
    def get(self):   
        template = JINJA_ENVIRONMENT.get_template('aboutdata.html')
        self.response.out.write(template.render({}))

#############################################
##       ABOUT METRIC PAGE                 ##
#############################################
class MetricsPage(webapp2.RequestHandler):
    def get(self):   
        template = JINJA_ENVIRONMENT.get_template('aboutmetrics.html')
        self.response.out.write(template.render({}))

#############################################
##       URL MAPPING                        ##
#############################################
app = webapp2.WSGIApplication(
    [('/', MainPage),
    ('/droughttool', DroughtTool),
    ('/droughttool/', DroughtTool),
    ('/contact',ContactPage),
    ('/aboutdata',DataPage),
    ('/aboutmetrics',MetricsPage)],
    debug=True)
