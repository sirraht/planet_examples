# coding: utf-8

# A simple program for executing "quick searches" exercising the
# Planet Python Client for API V1.

# Requires geojson spatial filter and at least one "item_type".
# GeoJSON should look like this:        
"""
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
"""
# Prereq:
# Set up the PL_API_KEY as an environment variable in bash .profile
# export PL_API_KEY='SOME_KEY'

import datetime
import json
import argparse
from planet import api as planetapi
from sys import stdout
"""
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

"""


def get_file(file):
    with open(file, 'r') as geo_json_data:
        data = json.load(geo_json_data)
    
    # Remove whitespace and newline characters    
   
    # clean_dict(data)
    
    return data
   

def create_date_filter(dlt, dgt):
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
    date_query_lt = planetapi.filters.date_range('acquired', lte=dlt)
   
    date_query_gt = planetapi.filters.date_range('acquired', gte=dgt)
    
    return date_query_lt, date_query_gt


def create_filter(geojson, arguments):
    # Build Planet geo query json

    geo_query = planetapi.filters.geom_filter(geojson)
    
    # Build range filter for specifying % cloud cover
    cloud_filter = planetapi.filters.range_filter('cloud_cover', lt=arguments.cloudcover)

    # Build permission filter
    #permission_filter = planetapi.filters.permission_filter('assets.analytic:download')
    permission_filter = planetapi.filters.permission_filter(arguments.permissions)

    # Build range filter for specifying % usable pixels
    # usable_filt = planetapi.filters.range_filter('usable_data', lt=arguments.usable)

    date_query_lt, date_query_gt = create_date_filter(arguments.datelessthan,
                                                      arguments.dategreaterthan)

    # Combine query filters with geoquery as 'And' filter
    pl_filter = planetapi.filters.and_filter(
        date_query_gt, date_query_lt, cloud_filter, geo_query, permission_filter)
   
    return pl_filter


def do_search(pl_filter, arguments):

    # Get client

    client = planetapi.ClientV1()
    # Build request; this will cause an exception if there are any API related errors
    request = planetapi.filters.build_search_request(pl_filter, arguments.satellite)

    results = client.quick_search(request)

    if args.doprint is True:
        print("Results from:", ", ".join(arguments.satellite))

    out_buffer = []
    # items_iter returns an iterator over API response pages
    for item in results.items_iter(limit=None):
        # each item is a GeoJSON feature
        if arguments.doprint is True:
            stdout.write('%s\n' % item['id'])
            out_buffer.append(item)

        else:
            out_buffer.append(item)
 
    with open('./result.json', 'w') as request_out:
        json.dump(out_buffer, request_out, sort_keys=True, indent=4, ensure_ascii=False)


def main(arguments):
    
    geo_json_data = get_file(arguments.geojson)

    pl_filter = create_filter(geo_json_data, arguments)
    
    do_search(pl_filter, arguments)


if __name__ == "__main__":
        
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")    
    
    parser = argparse.ArgumentParser(description='planet downloader')
    parser.add_argument('geojson',
                        help='Path to GeoJSON file')
    parser.add_argument('-s', '--satellite',
                        help='Item types indicating satellite platforms to search, '
                             'e.g. -s "SkySatScene" "PSScene4Band".',
                        type=str,
                        nargs='*',
                        default=["PSScene4Band"])
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('--noprint',
                        help='Suppress printing results',
                        action='store_true')
    group1.add_argument('--doprint',
                        help='Print item IDs to stdout',
                        action='store_true')
    parser.add_argument('--cloudcover',
                        help='Max percentage cloud cover, float between 0 and 1',
                        default=1.0,
                        type=float)
    parser.add_argument('--datelessthan',
                        help='Less than or equal to date',
                        default=today,
                        type=str)
    parser.add_argument('--dategreaterthan',
                        help='Greater than or equal to date',
                        default="2000-01-01",
                        type=str)
    parser.add_argument('--permissions',
                        help='Download permission level "assets:download", '
                             '"assets.visual:download", '
                             'or "assets.analytic:download"',
                        default="assets:download",
                        type=str)

    parser.set_defaults()
    args = parser.parse_args()
    
    main(args)
