#!/usr/bin/python
"""
Finds the bounds of a given address using Google Geocoding API. 

Outputs the bounds as a GeoJSON polygon.
"""

import sys
import getopt

import urllib
import json 

from collections import OrderedDict

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
  
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h:a:b", ["help", "address=", "bounds="])
            if len(opts) > 0:
                for o, a in opts: 
                    if o in ("-a", "--address"):
                        print geojson_from_address(a)
                    elif o in ("-b", "--bounds"):
                        print geojson_from_bounds(a)
                    elif o in ("-h", "--help"):
                        usage(argv)
            else: 
                usage(argv)
            
        except getopt.error, msg:
             raise Usage(msg)
        # more code, unchanged
    except Usage, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "for help use --help"
        return 2
        
    return 0

def geojson_from_address(address): 
    """ 
    Generates a GeoJSON polygon object of the bounds for the given address 
    """
    endpoint = 'http://maps.googleapis.com/maps/api/geocode/json'
    sensor = 'true'
    try:
        query_string = urllib.urlencode(OrderedDict(address=address, sensor=sensor))
        url = "%s?%s" % (endpoint, query_string)
        res = urllib.urlopen(url)
        data = res.read()
        d = json.loads(data)
        if 'results' in d:
            for r in d['results']:
                name = None
                if 'formatted_address' in r:
                    name = r['formatted_address']
                if 'geometry' in r:
                    if 'bounds' in r['geometry']:
                        bounds = r['geometry']['bounds']
                        ne = bounds['northeast']
                        sw = bounds['southwest']
                        b = "%f %f %f %f" % (sw['lng'], ne['lat'], ne['lng'], sw['lat'])
                        
                        # construct the GeoJSON object 
                        geojson = {}
                        geojson['type'] = "Polygon"
                        coordinates = []
                        coordinates.append([sw['lng'], ne['lat']])
                        coordinates.append([ne['lng'], ne['lat']])
                        coordinates.append([ne['lng'], sw['lat']])
                        coordinates.append([sw['lng'], sw['lat']])
                        coordinates.append([sw['lng'], ne['lat']])
                        geojson['coordinates'] = [coordinates]
                        
                        return json.dumps(geojson, indent=4, separators=(',', ': '))
    except IOError:
        print sys.stderr, 'Could not open URL.'

def geojson_from_bounds(bounds):
    """
    Generates a GeoJSON object of the bounds for the given bounds
    
    The bounds should be comma-separated: -75.045,38.32,-75.04,38.325
    
    """
    bnds = [float(b) for b in bounds.split(',')]
    if len(bnds) == 4:
        # construct the GeoJSON object 
        geojson = {}
        geojson['type'] = "Polygon"
        coordinates = []
        coordinates.append([bnds[0], bnds[3]])
        coordinates.append([bnds[2], bnds[3]])
        coordinates.append([bnds[2], bnds[1]])
        coordinates.append([bnds[0], bnds[1]])
        coordinates.append([bnds[0], bnds[3]])
        geojson['coordinates'] = [coordinates]
    
        return json.dumps(geojson, indent=4, separators=(',', ': '))

    return json.dumps({})

def usage(argv):
    """ Prints usage message """
    print "%s --address [address]" % argv[0]

if __name__ == "__main__":
  sys.exit(main())