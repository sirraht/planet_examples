
# coding: utf-8

# A simple script exercising the Planet Python Client for API V1

# Prereq:
# Set up the PL_API_KEY as an environment variable in bash .profile
# export PL_API_KEY='SOME_KEY'

from planet import api as planetapi
from sys import stdout

# GeoJSON search geometry. Note "type" value needs capitalization
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

# Build Planet geo query json
    
geoquery = planetapi.filters.geom_filter(aoi)


# Build Planet date range query json

datequerygt = planetapi.filters.date_range('acquired', gt='2017-12-01')
datequerylt = planetapi.filters.date_range('acquired', lt='2017-12-31')


# Build range filter for specifying % cloud cover

cloud_filt = planetapi.filters.range_filter('cloud_cover', lt=0.2)


# Combine date query with geoquery as an 'And' filter

filt = planetapi.filters.and_filter(datequerygt, datequerylt, cloud_filt, geoquery)


# Get client

client = planetapi.ClientV1()


# we are requesting PlanetScope 4 Band imagery

item_types = ['PSScene4Band']

request = planetapi.filters.build_search_request(filt, item_types)
# this will cause an exception if there are any API related errors

results = client.quick_search(request)

# items_iter returns an iterator over API response pages
for item in results.items_iter(limit=None):
  # each item is a GeoJSON feature
  stdout.write('%s\n' % item['id'])

