
# coding: utf-8

# A simple program for exercising the Planet Python Client for API V1.
# Requires geojson spatial filter and at least one "item_type".
# GeoJSON should look like this:        
'''    
    aoi = {
        "type": "Polygon",
        "coordinates": [
            [
                [
                    -119.75921630859374,
                    37.127476151584446
                ],
                [
                    -119.76187705993651,
                    37.08777498712564
                ],
                [
                    -119.72265243530273,
                    37.08695336399672
                ],
                [
                    -119.72136497497559,
                    37.12679182507274
                ],
                [
                    -119.75921630859374,
                    37.127476151584446
                ]
            ]
        ]
    }
'''
# Valid "item_types" include:

# Prereq:
# Set up the PL_API_KEY as an environment variable in bash .profile
# export PL_API_KEY='SOME_KEY'

import datetime
import json
import argparse
from planet import api as planetapi
from sys import stdout
from string import Template

def clean_dict(d):
    
    for key, value in d.items():
        if isinstance(value, list):
            clean_list(value)
        elif isinstance(value, dict):
            clean_dict(value)
        else:
            newvalue = value.strip()
            d[key] = newvalue

def clean_list(l):
    
    for index, item in enumerate(l):
        if isinstance(item, dict):
            clean_dict(item)
        elif isinstance(item, list):
            clean_list(item)
        else:
            if isinstance(item, str):
                l[index] = item.strip()
            else:
                l[index] = item


def getFile(file):
    with open(file, 'r') as geojsondata:
        data = json.load(geojsondata)
    
    # Remove whitespace and newline characters    
   
    clean_dict(data)
    
    return data
   

def createDateFilter(dlt, dgt):
    
    
    # Build Planet date range query json
    try:
        datetime.datetime.strptime(dlt, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYY-MM-DD")    
    try:
        datetime.datetime.strptime(dgt, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYY-MM-DD") 

    # Enforce dlt to be after dgt
    if dlt < dgt:
        raise ValueError("DateGreaterThan must be earlier in time than DateLessThan") 

    # Build filter 
    datequerylt = planetapi.filters.date_range('acquired', lt=dlt)
   
    datequerygt = planetapi.filters.date_range('acquired', gt=dgt)
    
    return datequerylt, datequerygt    


def createFilter(geojsondata, cloudcover, dlt=None, dgt=None):
   
    # Build Planet geo query json

    geoquery = planetapi.filters.geom_filter(geojsondata)
    
    # Build range filter for specifying % cloud cover
    cloud_filt = planetapi.filters.range_filter('cloud_cover', lt=cloudcover)

    datequerylt, datequerygt = createDateFilter(dlt, dgt)

    # Combine date query with geoquery as an 'And' filter

    filt = planetapi.filters.and_filter(
        datequerygt, datequerylt, cloud_filt, geoquery)
   
    return filt 


def doSearch(filt, args):

    # Get client

    client = planetapi.ClientV1()
    # Build request; this will cause an exception if there are any API related errors
    request = planetapi.filters.build_search_request(filt, args.satellite)

    results = client.quick_search(request)

    if args.doprint == True:
        print("Results from:", ", ".join(args.satellite)) 

    outbuffer = []
    # items_iter returns an iterator over API response pages
    for item in results.items_iter(limit=None):
        # each item is a GeoJSON feature
        if args.doprint == True: 
            stdout.write('%s\n' % item['id'])
            outbuffer.append(item)

        else:
            outbuffer.append(item)
 
    with open('./result.json','w') as requestout:
        json.dump(outbuffer, requestout, sort_keys=True, indent=4, ensure_ascii=False)


def main(args):
    
    geojsondata = getFile(args.geojson)

    filt = createFilter(geojsondata, cloudcover=args.cloudcover, dlt=args.datelessthan, dgt=args.dategreaterthan)
    
    doSearch(filt, args)


if __name__ == "__main__":
        
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")    
    
    parser = argparse.ArgumentParser(description='planet downloader')
    parser.add_argument('geojson', help='Path to GeoJSON file')
    group = parser.add_mutually_exclusive_group() 
    group.add_argument('--noprint', help='Suppress printing results', action='store_true') 
    group.add_argument('--doprint', help='Print item IDs to stdout', action='store_true') 
    parser.add_argument('-s', '--satellite', help='Item types indicating satellite platforms to search, e.g. -s "SkySatScene" "PSScene4Band".', type=str, nargs='*', default=["PSScene4Band"])
    parser.add_argument('-c', '--cloudcover', help='Max percentage cloud cover, float between 0 and 1', default=1.0, type=float)
    parser.add_argument('--datelessthan', help='Less than date', default=today, type=str)     
    parser.add_argument('--dategreaterthan', help='Greater than date', default="2000-01-01", type=str)  
    parser.set_defaults()    
    args = parser.parse_args()
    
    main(args)
