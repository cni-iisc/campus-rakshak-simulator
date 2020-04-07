#!/usr/bin/env python
# coding: utf-8

# In[54]:


import json
import geopandas as gpd
import math
from shapely.geometry import Point, MultiPolygon

import csv
import numpy as np
import random

import argparse
import os
import sys


ibasepath = "data/base/mumbai/"
citygeojsonfile  = ibasepath+"city.geojson"
demographicsfile = ibasepath+"demographics_2011.csv"
employmentfile   = ibasepath+"employment_2011.csv"
householdfile    = ibasepath+"households_2011.csv"
cityprofilefile  = ibasepath+"cityProfile.json"

obasepath = "data/mumbai/"
individualsjson  = obasepath+"individuals.json"
housesjson       = obasepath+"houses.json"
workplacesjson   = obasepath+"workplaces.json"
schoolsjson      = obasepath+"schools.json"


my_parser = argparse.ArgumentParser(description='Create mini-city for COVID-19 simulation')
my_parser.add_argument( 'n', action='store',
                       type=int,
                       nargs='?',
                       help='target population',
                       default=100000)
args = my_parser.parse_args()
miniPop = args.n
#miniPop = 10000

#fixing for now
slum_schoolsize_factor = 2
slum_householdsize_scalefactor = 2
slum_fraction = 0.42



print("Creating city with a population of approximately ",miniPop,flush=True)
print("")

print("Reading city.geojson to get ward polygons...",end='',flush=True)


geoDF = gpd.read_file(citygeojsonfile)
geoDF['wardNo'] = geoDF['wardNo'].astype(int)
geoDF['wardIndex'] = geoDF['wardNo'] - 1
geoDF = geoDF[['wardIndex','wardNo', 'wardName', 'geometry']]
geoDF['wardBounds'] = geoDF.apply(lambda row: MultiPolygon(row['geometry']).bounds, axis=1)
geoDF['wardCentre'] = geoDF.apply(lambda row: (MultiPolygon(row['geometry']).centroid.x, MultiPolygon(row['geometry']).centroid.y), axis=1)
geoDF["neighbors"] = geoDF.apply(lambda row: ", ".join([str(ward) for ward in geoDF[~geoDF.geometry.disjoint(row['geometry'])]['wardNo'].tolist()]) , axis=1)

print("done.",flush=True)

def sampleRandomLatLong(wardIndex):
    (lat1,lon1,lat2,lon2) = geoDF['wardBounds'][wardIndex]
    while True:
        lat = random.uniform(lat1,lat2)
        lon = random.uniform(lon1,lon2)
        point = Point(lat,lon)
        if MultiPolygon(geoDF['geometry'][wardIndex]).contains(point):
            return (lat,lon)

def distance(lat1, lon1, lat2, lon2):
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1))         * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def getCommunityCenterDistance(lat,lon,wardIndex):
    (latc,lonc) = geoDF['wardCentre'][wardIndex]
    return distance(lat,lon,latc,lonc)


# In[55]:


print("Reading demographics, employment and household data (csv)...",end='',flush=True)


wardname = []
wardpop = []
wardarea = []
wardemployed = []
wardunemployed = []
wardworkforce = []
wardhouseholds = []

with open(demographicsfile, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        if row[0]=='wardIndex':
            continue
        wardname.append(row[2])
        wardarea.append(float(row[3]))
        wardpop.append(int(row[4]))
with open(employmentfile, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        if row[0]=='wardIndex':
            continue
        wardemployed.append(int(row[3]))
        wardunemployed.append(int(row[4]))
        wardworkforce.append(int(row[5]))
with open(householdfile, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        if row[0]=='wardIndex':
            continue
        wardhouseholds.append(int(row[3]))
print("done.",flush=True)


# In[56]:


with open(cityprofilefile, newline='') as file:
    cityprofiledata = json.load(file)

hbins = cityprofiledata['householdSize']['bins']
hweights = cityprofiledata['householdSize']['weights']

def sampleHouseholdSize():
    s = np.random.choice(hbins,1,hweights)[0]
    if '+' in s:
        n = int(s[:-1])
    elif '-' in s:
        (a,b) = s.split('-')
        n = random.randint(int(a),int(b))
    else:
        n = int(s)
    return n


# In[57]:


agebins = cityprofiledata['age']['bins']
ageweights = cityprofiledata['age']['weights']


def sampleAge():
    s = np.random.choice(agebins,1,ageweights)[0]
    if '+' in s:
        n = int(s[:-1])
    else:
        (a,b) = s.split('-')
        n = random.randint(int(a),int(b))
    return n


# In[58]:


totalPop = sum(wardpop)
scale = miniPop/totalPop
nwards = len(wardname)



mwardpop = [int(a * scale) for a in wardpop]
mslumwardpop = [int(a * scale * slum_fraction) for a in wardpop]
mnonslumwardpop = [mwardpop[i] - mslumwardpop[i] for i in range(len(wardpop))]
mwardemployed = [int(a * scale) for a in wardunemployed]
mwardunemployed = [int(a * scale) for a in wardemployed]
mwardworkforce = [int(a * scale) for a in wardworkforce]
mwardhouseholds = [int(a * scale) for a in wardhouseholds]


# In[59]:


print("Creating households for each ward...",end='',flush=True)



houses = []
hid = 0
for wardIndex in range(nwards):
    wnonslumpop = mnonslumwardpop[wardIndex]
    wslumpop = mslumwardpop[wardIndex]
    currnonslumwpop = 0
    currslumwpop = 0
    while(currnonslumwpop < wnonslumpop):
        h = {}
        h["id"]=hid
        h["wardIndex"]=wardIndex
        h["slum"]=0

        s = sampleHouseholdSize()
        h["size"]=s
        currnonslumwpop+=s
        (lat,lon) = sampleRandomLatLong(wardIndex)
        h["lat"] = lat
        h["lon"] = lon
        houses.append(h)
        hid+=1


    while(currslumwpop < wslumpop):
        h = {}
        h["id"]=hid
        h["wardIndex"]=wardIndex
        h["slum"]=1
        s = int(sampleHouseholdSize() * slum_householdsize_scalefactor)
        h["size"]=s
        currslumwpop+=s
        (lat,lon) = sampleRandomLatLong(wardIndex)
        h["lat"] = lat
        h["lon"] = lon
        houses.append(h)
        hid+=1
print("done.",flush=True)


# In[60]:


print("Creating individuals to populate the households...",end='',flush=True)

pid = 0
individuals = []
schoolers = [[] for _ in range(nwards)]
workers = [[] for _ in range(nwards)]
slum_schoolers = [[] for _ in range(nwards)]
nonslum_schoolers = [[] for _ in range(nwards)]

#this should be changed to the actual thing
homeworkmatrix = [[(1/nwards)]*nwards]*nwards

for h in houses:
    s = h["size"]
    for i in range(s):
        p = {"id":pid}

        p["household"]=h["id"]
        wardIndex = h["wardIndex"]
        p["wardIndex"]=wardIndex
        p["wardNo"] = wardIndex+1
        p["slum"] = h["slum"]

        p["lat"] = h["lat"]
        p["lon"] = h["lon"]

        p["CommunityCentreDistance"] = getCommunityCenterDistance(h["lat"],h["lon"],wardIndex)

        age = sampleAge()
        p["age"] = age

        #initialising most stuff to None
        p["employed"]=None
        p["workplace"]=None
        p["workplaceType"]=None
        p["school"]=None

        if age<=15:
            #decide about his/her school
            p["employed"]=0
            p["workplaceType"]=2 #this is school

            #assuming they all go to school
            #schoolers[wardIndex].append(pid)
            if p["slum"]==1:
                slum_schoolers[wardIndex].append(pid)
            else:
                nonslum_schoolers[wardIndex].append(pid)

        elif age>=15 and age<65:
            #decide about employment
            eprob = wardemployed[wardIndex]/wardpop[wardIndex]
            eprobadjusted = eprob/sum([ageweights[a] for a in range(3,13)])
            if(random.uniform(0,1)<eprobadjusted):
                #person is employed
                p["employed"]=1

                p["workplace"]="TODO"
                workplaceward = int(np.random.choice(list(range(nwards)),1,homeworkmatrix[wardIndex])[0])
                p["workplaceward"]=workplaceward
                p["workplaceType"]=1
                workers[workplaceward].append(pid)
            else:
                p["employed"]=0
                p["workplaceType"]=0
        else:
            #decide about seniors
            test = 0
            p["employed"]=0
        individuals.append(p)
        pid+=1

print("done.",flush=True)


# In[61]:


# Just taking the code from assignWorkplaces.py
# Don't know what exactly the distribution is

def workplaces_size_distribution(a=3.26, c=0.97, m_max=2870):
    count=1
    a=3.26
    c=0.97
    m_max=2870
    p_nplus = np.arange(float(m_max))
    for m in range(m_max):
        p_nplus[m] =  ((( (1+m_max/a)/(1+m/a))**c) -1) / (((1+m_max/a)**c) -1)

    p_nminus = 1.0 - p_nplus
    p_n = np.arange(float(m_max))
    prev=0.0
    for m in range(1, m_max):
        p_n[m] = p_nminus[m] - prev
        prev = p_nminus[m]

    return p_n/sum(p_n)

def sampleWorkplaceSize():
    wsdist = workplaces_size_distribution()
    m_max = len(wsdist)
    return int(np.random.choice(np.arange(m_max),1,p=wsdist)[0])


# In[62]:


print("Assigning workplaces to people...",end='',flush=True)

#assigning workplaces to people who want work
workplaces = []
wid = 0
for wardIndex in range(nwards):
    wworkers = len(workers[wardIndex])
    while len(workers[wardIndex])>0:
        w = {"id":wid}
        (lat,lon) = sampleRandomLatLong(wardIndex)
        w["lat"] = lat
        w["lon"] = lon

        w["wardIndex"]=wardIndex
        s = sampleWorkplaceSize()
        i = 0
        while(i < s and len(workers[wardIndex])>0):
            pid = workers[wardIndex].pop(random.randrange(len(workers[wardIndex])))
            individuals[pid]["workplace"]=wid
            del individuals[pid]["workplaceward"]
            i+=1
        workplaces.append(w)
        wid+=1

print('done.',flush=True)


# In[63]:


schoolsizebins = ["0-100", "100-200", "200-300", "300-400", "400-500", "500-600", "600-700", "700-800", "800-900"]
schoolsizebinweights = [0.0185, 0.1204, 0.2315, 0.2315, 0.1574, 0.0889, 0.063, 0.0481, 0.0408]

def sampleSchoolSize():
    s = int(np.random.choice(list(range(len(schoolsizebinweights))),1,schoolsizebinweights)[0])
    return (100*s + random.randint(0,99))



print("Assigning schools to people...",end='',flush=True)

#assigning school to people who want go to school
schools = []
sid = 0
for wardIndex in range(nwards):
    wslum_schoolers = len(slum_schoolers[wardIndex])
    while len(slum_schoolers[wardIndex])>0:
        s = {"ID":sid} #capitalised in the previous code so keeping it so
        s["wardIndex"]=wardIndex
        (lat,lon) = sampleRandomLatLong(wardIndex)
        s["lat"] = lat
        s["lon"] = lon
        s["slum"]=1

        size = int(sampleSchoolSize()*slum_schoolsize_factor)

        i = 0
        while(i < size and len(slum_schoolers[wardIndex])>0):
            pid = slum_schoolers[wardIndex].pop(random.randrange(len(slum_schoolers[wardIndex])))
            individuals[pid]["school"]=sid
            i+=1
        schools.append(s)
        sid+=1
for wardIndex in range(nwards):
    wnonslum_schoolers = len(nonslum_schoolers[wardIndex])
    while len(nonslum_schoolers[wardIndex])>0:
        s = {"ID":sid} #capitalised in the previous code so keeping it so
        s["wardIndex"]=wardIndex
        (lat,lon) = sampleRandomLatLong(wardIndex)
        s["lat"] = lat
        s["lon"] = lon
        s["slum"]=0

        size = sampleSchoolSize()
        i = 0
        while(i < size and len(nonslum_schoolers[wardIndex])>0):
            pid = nonslum_schoolers[wardIndex].pop(random.randrange(len(nonslum_schoolers[wardIndex])))
            individuals[pid]["school"]=sid
            i+=1
        schools.append(s)
        sid+=1


print("done.",flush=True)

print("")
print("Created (mini)city")
print("Population:",len(individuals))
print("Households:",len(houses))
print("Schools:",len(schools))
print("Workplaces:",len(workplaces))
print("")


# In[64]:


print("Dumping to json files...",end='',flush=True)

f = open(individualsjson, "w")
f.write(json.dumps(individuals))
f.close
print("(individuals.json, ",end='',flush=True)

f = open(housesjson, "w")
f.write(json.dumps(houses))
f.close
print("houses.json, ",end='',flush=True)

f = open(workplacesjson, "w")
f.write(json.dumps(workplaces))
f.close
print("workplaces.json, ",end='',flush=True)

f = open(schoolsjson, "w")
f.write(json.dumps(schools))
f.close
print("schools.json) ... done.",flush=True)

print("NOTE: Not generating commonArea.json, fractionPopulation.json, wardCenterDistance.json as they are fixed.")


# In[ ]:
