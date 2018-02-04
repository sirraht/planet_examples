import argparse
from planet import api
from planet.api import downloader
import json


def get_client():
    client = api.ClientV1() 
    return client


def get_downloader(client):
    pl_downloader = downloader.create(client)
    return pl_downloader


def get_input_file(inputfile):
    with open(inputfile, 'r') as jsondata:
        data = json.load(jsondata)
    return data


'''
def getitems(data):
    items = [] 
    for item in data:
        # each item is a JSON feature
        items.append(item['id'])
    return items
'''


def downloaditems(client, available_collects, dest):

    for item in available_collects:
        print(item['id'])
        assets = client.get_assets(item).get()
        activation = client.activate(assets['analytic'])
        # wait for activation
        assets = client.get_assets(item).get()
        callback = api.write_to_file(dest)
        body = client.download(assets['analytic'], callback=callback)
        body.await()


def main(args):
    client = get_client() 
    inputdata = get_input_file(args.jsonFile)
    downloaditems(client, inputdata, args.directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Python for downloading '
                                                 'image assets associated with sensors '
                                                 'identified with planetSearch.py')
    parser.add_argument('jsonFile',
                        help="Path to json file containing search results from "
                             "planetSearch.py")
    #parser.add_argument('assettypes', help="List of asset-types to download.  See https://api.planet.com/data/v1/asset-types/", type=str, nargs='*')
    parser.add_argument('-d', '--directory',
                        help="Destination directory, must exist",
                        type=str, default=".")


 
    args = parser.parse_args() 
    main(args)
