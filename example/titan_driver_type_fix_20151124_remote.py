#!/bin/env python
#encoding=utf-8
import urllib
import httplib
import sys
import pymongo
from pymongo import MongoClient

reload(sys)
sys.setdefaultencoding('utf-8')

m_user='xxx'
m_pwd='xxx'
m_host='127.0.0.1'
m_db='xx'
m_port=27017

# titan http request env
port = 8080
host = '127.0.0.1'
requrl = 'api/car/operate/update.json'

#
client  = MongoClient('mongodb://%s:%s@%s:%d/%s' % (m_user, m_pwd, m_host, m_port, m_db))
db = client[m_db]
coll = db['car_parameter']

query = {"_id": "7806f40e-4bf8-4989-9e5c-b57c75a9500e"}
#query = {}
fieldFilter = {"_id":1, "drive_type":1, "driver_type":1}

posts = coll.find(query, fieldFilter)

total = posts.count()

print 'size=%d' % total

current = 0

# Reuse connection
conn = httplib.HTTPConnection(host, port)

for post in posts:
    #print post, post.get("_id"), post.get("drive_type") 
    current = current + 1
    id = post.get("_id")
    dType = post.get("drive_type")
    newDType = post.get("driver_type")

    if newDType:
        print 'already done, skip'
        continue
    
    print 'begin... total=%d, current=%d, id=%s' % (total, current, id)

    if not id:
        print 'skip id not found'
        continue
    if not dType:
        print 'skip drive_type not found'
        continue
    print id, dType

#    if type(id) == unicode:
#        id = id.encode("utf-8", "ignore")
#    if type(dType) == unicode:
#        dType = dType.encode("utf-8", "ignore")
    
    # Process item of : "driver_type" : "{key_name=驱动方式, value=11, value_name=FR－前置后驱, key=driver_type}"
    if isinstance(dType, dict):
        dType = dType.get("value")    
    
    if not dType:
        print 'skip drive_type not found'
        continue
 
    if dType == "other":
        dType = "5"
 
    type = {"driveType": "%s" % dType}
    #type = {"driveType": "4"}
    get_params = {"appName":"souche", "group":"car_parameter", "id":"%s" % id, "attrs": "%s" % type}
    
    get_params_urlencode = urllib.urlencode(get_params)

    geturl = '%s?%s' % (requrl, get_params_urlencode)
    posturl = 'http://%s:%d/%s' % (host, port, requrl)

    headerdata = {"Host": '%s:%d' % (host, port), "Content-Type":"application/x-www-form-urlencoded"}
    conn.request(method="POST", url = posturl, body=get_params_urlencode, headers = headerdata)

    response = conn.getresponse()

    res= response.read()

    print "done ,id=%s, res=%s" % (id, res)

conn.close()

print 'Done'
