# -*- coding: utf-8 -*- 
"""TrackingAPI.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xm5WCj0JX3h0BYpH4hHS9sPdmcU9uLJK
"""

# !pip install tracking-url

# !pip install ups

# !pip install usps-api

# !pip install flask

# !pip install flask-ngrok

# !pip install fedex

# !pip install -e git://github.com/akolpakov/ClassicUPS.git#egg=classicups

# !pip install classicups -- do not run this command to install ups module, instead run the above one

import tracking_url
from usps import USPSApi
from fedex.services.track_service import FedexTrackRequest 
from fedex.config import FedexConfig
from fedex.tools.conversion import sobject_to_dict
from fedex.tools.conversion import sobject_to_json
from flask import Flask
# from flask_ngrok import run_with_ngrok
from flask import request, jsonify
from ClassicUPS import UPSConnection
# import time
import xml.etree.ElementTree as ET

app=Flask(__name__)

# run_with_ngrok(app)

@app.route('/')
def first():
    return 'App is live!'

@app.route('/api/<id>')
def executor(id):
    
    try:
        
        with open('records.txt','a') as file:
            file.write('API called with id {id}\n'.format(id=id))
        
    except Exception as e:
        
        with open('records.txt','a') as file:
            file.write(e)
            file.write('\n')

    guess=tracking_url.guess_carrier(id)

    if guess:

        package_url=guess.url

        guess=guess.carrier

        print(guess, package_url)

        if guess=='fedex':

            return fedexShipment(id, package_url)

        elif guess=='ups':
            
#             return 'Classic UPS module required!'

            return upsShipment(id, package_url)

        elif guess=='usps':

            return uspsShipment(id, package_url)

    else:

        error_msg={'data':'No data found'}

        return error_occured()

def upsShipment(tracking_id, package_url):

  try:

    ups=UPSConnection('8D9C85F69560E832',
                      'trackpaxers',
                      'Swiggle42!',)
    
    track=ups.tracking_info(tracking_id)

    data=track.result.xml_response.decode()
    
    data=ET.fromstring(data)
    
    #updating from here
    
    pack=data[1].findall('Package')
    
    if len(pack)>0:
        
        if pack[0][2].text:
            
            data=pack[0][2].text
            
            data=data[:4] + '-' + data[4:6] + '-' + data[6:]
            
            if pack[0][1].text.lower()=='y':
                
                data='Delivered on ' + data
                
            else:
                
                data='Scheduled delivery on ' + data
        
        
    else:
        
        data='Delivery pending.'
    
    
 #updates till here
    

    data={'status':True, 'company':'ups', 'url':package_url, 'data':data}

    return data

  except:

    return error_occured()



def uspsShipment(tracking_id, package_url):

    try:

        user='594TRACK3149'

        conn=USPSApi(user)

        track=conn.track(tracking_id)
        
        #updating from here for TrackSummary
        
        null=None
        
        res=track.result
        
        result=res['TrackResponse']['TrackInfo']['TrackSummary']
        
        result=result['Event'] + ' (Updated on '+ result['EventDate'] + ')' 
        
        

        
        
        
        
        
        
        
        
#         trackingStatus = usps.track(tracking_id).result
#         trackingResponse = trackingStatus.get('TrackResponse')
#         trackingInfo = trackingResponse.get('TrackInfo')
#         trackingError = trackingInfo.get('Error')
#         trackingId = trackingInfo.get('@ID')
        
#         data=''

#         if trackingError is None:
#             trackingSummary = trackingInfo.get('TrackSummary')
#             trackingDetail = trackingInfo.get('TrackDetail')
#             data='Tracking Number {0}'.format(trackingId)
#             data+='Tracking Summary {0}'.format(trackingSummary)
#             data+='Tracking Detail:'
#             data+=trackingDetail
            
#         return data

#         data={'company':'usps','url':package_url, 'data':track.result}   original returned data (working live)


#updates till here

        data={'status':True, 'company':'usps','url':package_url, 'data':result}

        return data

    except:

        return error_occured()



def fedexShipment(tracking_id, package_url):
    
#     global package_url

    try:

        CONFIG_OBJ = FedexConfig(key='hCXl7hCb73961EWa',

        password='dpBrCgq3LvbtHup5EUS2WwM0q',

        account_number='510087100',

        meter_number='119228198',

        use_test_server='https://wsbeta.fedex.com:443/web-services')

        track = FedexTrackRequest(CONFIG_OBJ)

        track.SelectionDetails.PackageIdentifier.Type = 'TRACKING_NUMBER_OR_DOORTAG'

        track.SelectionDetails.PackageIdentifier.Value = tracking_id

        track.send_request()

        response_dict = sobject_to_dict(track.response)

        response_json = sobject_to_json(track.response)
        
#         respdata = response_json.replace('\\','')
        
#         respdata=respdata.title()
        
#         respdata=eval(respdata)
        
#         req=respdata['Completedtrackdetails'][0]['Trackdetails'][0]['Events'][0]['Eventdescription']

        data={'status':True, 'company':'fedex', 'url':package_url, 'data':response_json}

        return data

    except:

        return error_occured()

def error_occured():

    error={'status':False, 'Data':'Some error occured!'}

    return error

if __name__ == "__main__":
    app.run()

# if __name__ == '__main__':
#     # Bind to PORT if defined, otherwise default to 5000.
#     port = int(os.environ.get('PORT', 5004))
#     app.run(host='0.0.0.0', port=port)









""" NOT BEING USED CODE 



# ups

tracker = track
result = ""

#1 List all carriers
urlStr = ""
requestData = ""
#result = tracker.trackingmore(requestData, urlStr, "carriers")

#2 detect a carriers by tracking number
#urlStr = ""
#requestData = "{\"tracking_number\":\"1Z2A272F6740509862\"}"
#result = tracker.trackingmore(requestData, urlStr, "carriers/detect")

#3 create a tracking number(??????????????????)
#urlStr = ""
# requestData = "{\"tracking_number\": \"1Z2A272F6740509862\",\"carrier_code\":\"ups\",\"title\":\"4PX page\",\"customer_name\":\"trackingmore user\",\"customer_email\":\"service@trackingmore.com\",\"order_id\":\"#123\",\"order_create_time\":\"2018/09/08 16:51\",\"destination_code\":\"US\",\"tracking_ship_date\":\"20180908\",\"tracking_postal_code\":\"12201\",\"lang\":\"en\",\"logistics_channel\":\"API TEST\"}"
# result = tracker.trackingmore(requestData, urlStr, "post")

#4 List all trackings
#urlStr = "?page=1&limit=100&created_at_min=&created_at_max=&update_time_min=&update_time_max=&order_created_time_min=&order_created_time_max=&numbers=1Z2A272F6740509862&orders=&lang=en"
#requestData = ""
#result = tracker.trackingmore(requestData, urlStr, "get")

#5 Get tracking results of a single tracking.
urlStr = "/ups/1Z2A272F6740509862/en"
requestData = ""
result = tracker.trackingmore(requestData, urlStr, "codeNumberGet")

#6 create muti tracking number
#urlStr = ""
#requestData = "[{\"tracking_number\": \"1Z2A272F6740509862\",\"carrier_code\":\"ups\",\"title\":\"4PX page\",\"customer_name\":\"trackingmore user\",\"customer_email\":\"service@trackingmore.com\",\"order_id\":\"#123\",\"order_create_time\":\"2018/09/08 16:51\",\"destination_code\":\"US\",\"tracking_ship_date\":\"20180908\",\"tracking_postal_code\":\"12201\",\"lang\":\"en\",\"logistics_channel\":\"API TEST\"},{\"tracking_number\": \"LZ448865302CN\",\"carrier_code\":\"china-ems\",\"title\":\"4PX page\",\"customer_name\":\"trackingmore user\",\"customer_email\":\"service@trackingmore.com\",\"order_id\":\"#123\",\"order_create_time\":\"2018/09/08 16:51\",\"destination_code\":\"US\",\"tracking_ship_date\":\"20180908\",\"tracking_postal_code\":\"12201\",\"lang\":\"en\",\"logistics_channel\":\"API TEST\"}]"
#result = tracker.trackingmore(requestData, urlStr, "batch")

#7 Update Tracking item
#urlStr = "/ups/1Z2A272F6740509862"
#requestData = "{\"title\": \"4PX page\",\"customer_name\":\"trackingmore user\",\"customer_email\":\"service@trackingmore.com\",\"order_id\":\"#123\",\"logistics_channel\":\"API TEST\",\"customer_phone\":\"+86 13142052920\",\"destination_code\":\"US\",\"status\":\"7\"}"
#result = tracker.trackingmore(requestData, urlStr, "codeNumberPut")

#8 Delete a tracking item
#urlStr = "/ups/1Z2A272F6740509862"
#requestData = ""
#result = tracker.trackingmore(requestData, urlStr, "codeNumberDelete")

#9 Get realtime tracking results of a single tracking
#urlStr = ""
#requestData = "{\"tracking_number\": \"1Z2A272F6740509862\",\"carrier_code\":\"ups\",\"destination_code\":\"US\",\"tracking_ship_date\": \"20180908\",\"tracking_postal_code\":\"12201\",\"specialNumberDestination\":\"UK\",\"order\":\"#123\",\"order_create_time\":\"2018/09/08 16:51\",\"lang\":\"en\"}"
#result = tracker.trackingmore(requestData, urlStr, "realtime")

#10 Modify courier code
#urlStr = ""
#requestData = "{\"tracking_number\": \"1Z2A272F6740509862\",\"carrier_code\":\"ups\",\"update_carrier_code\":\"china-ems\"}"
#result = tracker.trackingmore(requestData, urlStr, "update")

#11 Get user info
#urlStr = ""
#requestData = ""
#result = tracker.trackingmore(requestData, urlStr, "getuserinfo")

#12 Get status number
#urlStr = ""
#requestData = ""
#result = tracker.trackingmore(requestData, urlStr, "getstatusnumber")

#13 Set number not update
#urlStr = ""
#requestData = "[{\"tracking_number\":\"1Z2A272F6740509862\",\"carrier_code\":\"ups\"},{\"tracking_number\":\"LZ448865302CN\",\"carrier_code\":\"ups\"}]"
#result = tracker.trackingmore(requestData, urlStr, "notupdate")

#14 Get remote iterm results
#urlStr = ""
#requestData = "[{\"country\":\"CN\",\"postcode\":\"400422\"},{\"country\":\"CN\",\"postcode\":\"412000\"}]"
#result = tracker.trackingmore(requestData, urlStr, "remote")

#15 Get cost time iterm results
#urlStr = ""
#requestData = "[{\"carrier_code\":\"ups\",\"destination\":\"US\",\"original\":\"CN\"},{\"carrier_code\":\"china-ems\",\"destination\":\"US\",\"original\":\"CN\"}]"
#result = tracker.trackingmore(requestData, urlStr, "costtime")

#16 Delete multiple tracking item
#urlStr = ""
#requestData = "[{\"tracking_number\":\"1Z2A272F6740509862\",\"carrier_code\":\"ups\"},{\"tracking_number\":\"LZ448865302CN\",\"carrier_code\":\"china-ems\"}]"
#result = tracker.trackingmore(requestData, urlStr, "delete")

#17 Update multiple Tracking item
#urlStr = ""
#requestData = "[{\"tracking_number\":\"1Z2A272F6740509862\",\"carrier_code\":\"ups\",\"title\": \"4PX page\",\"customer_name\":\"trackingmore user\",\"customer_email\":\"service@trackingmore.com\",\"order_id\":\"#123\",\"logistics_channel\":\"API TEST\",\"destination_code\":\"US\",\"status\":\"7\"},{\"tracking_number\":\"LZ448865302CN\",\"carrier_code\":\"china-ems\",\"title\": \"4PX page\",\"customer_name\":\"trackingmore user\",\"customer_email\":\"service@trackingmore.com\",\"order_id\":\"#123\",\"logistics_channel\":\"API TEST\",\"destination_code\":\"US\",\"status\":\"7\"}]"
#result = tracker.trackingmore(requestData, urlStr, "



print(result)

# track=ups.tracking_info('1Z84V3360333114179')

# resp=track.result.xml_response

# track.delivered.ctime()

# import xml.etree.ElementTree as ET

# tree = ET.fromstring(resp)

# x=resp.decode()

# y=x.split('\n')

# for line in y:
  # print(line)
# len(y)

#



import sys
import json
import urllib.request
import urllib.parse
import http.client

headers={"Content-Type":"application/json",
        "Trackingmore-Api-Key":"d740f2e2-da38-46f6-8607-e28d8d5c086b",
        'X-Requested-With':'XMLHttpRequest'
        }
class track:

    def trackingmore(requestData, urlStr, method):

        if method == "get":

            url = 'http://api.trackingmore.com/v2/trackings/get'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl, headers=headers)
            result = urllib.request.urlopen(req).read()

        elif method == "post":

            url = 'http://api.trackingmore.com/v2/trackings/post'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="POST")
            result = urllib.request.urlopen(req).read()

        elif method == "batch":

            url = 'http://api.trackingmore.com/v2/trackings/batch'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="POST")
            result = urllib.request.urlopen(req).read()

        elif method == "codeNumberGet":

            url = 'http://api.trackingmore.com/v2/trackings'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="GET")
            result = urllib.request.urlopen(req).read()

        elif method == "codeNumberPut":

            url = 'http://api.trackingmore.com/v2/trackings'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="PUT")
            result = urllib.request.urlopen(req).read()

        elif method == "codeNumberDelete":

            url = 'http://api.trackingmore.com/v2/trackings'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="DELETE")
            result = urllib.request.urlopen(req).read()

        elif method == "realtime":

            url = 'http://api.trackingmore.com/v2/trackings/realtime'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="POST")
            result = urllib.request.urlopen(req).read()

        elif method == "carriers":

            url = 'http://api.trackingmore.com/v2/carriers'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="GET")
            result = urllib.request.urlopen(req).read()

        elif method == "carriers/detect":

            url = 'http://api.trackingmore.com/v2/carriers/detect'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="GET")
            result = urllib.request.urlopen(req).read()

        elif method == "update":

            url = 'http://api.trackingmore.com/v2/trackings/update'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="POST")
            result = urllib.request.urlopen(req).read()

        elif method == "getuserinfo":

            url = 'http://api.trackingmore.com/v2/trackings/getuserinfo'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="GET")
            result = urllib.request.urlopen(req).read()

        elif method == "getstatusnumber":

            url = 'http://api.trackingmore.com/v2/trackings/getstatusnumber'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="GET")
            result = urllib.request.urlopen(req).read()

        elif method == "notupdate":

            url = 'http://api.trackingmore.com/v2/trackings/notupdate'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="POST")
            result = urllib.request.urlopen(req).read()

        elif method == "remote":

            url = 'http://api.trackingmore.com/v2/trackings/remote'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="POST")
            result = urllib.request.urlopen(req).read()

        elif method == "costtime":

            url = 'http://api.trackingmore.com/v2/trackings/costtime'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="POST")
            result = urllib.request.urlopen(req).read()

        elif method == "delete":

            url = 'http://api.trackingmore.com/v2/trackings/delete'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="POST")
            result = urllib.request.urlopen(req).read()

        elif method == "updatemore":

            url = 'http://api.trackingmore.com/v2/trackings/updatemore'
            RelUrl = url + urlStr
            req = urllib.request.Request(RelUrl,requestData.encode('utf-8'), headers=headers,method="POST")
            result = urllib.request.urlopen(req).read()

        return result

import fedex

data=upsShipment('1ZXA67480397094626', 'url')
print(data['company'])

string=data['data']

x=string.split('\n')

x=x[1]

import xml.etree.ElementTree as ET

# for i in x:
#   if i=='<':
#     print()
#   print(i,end='')

import re

words=x.split('<')

words=' '.join(words)
words=words.split('>')
words=' '.join(words)
words=words.split('/')

words

for word in words:
  if 'Delivery' in word:
    print(word)

"""
