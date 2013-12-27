#!/usr/bin/python
"""
Finds the bounds of a given address using Google Geocoding API. 

Outputs the bounds using the following pattern:

    [upper-left x] [upper-left y] [lower-right x] [lower-right y]

where x = longitude and y = latitude

This is for example the format GDAL uses for specifying a bounding box. 
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
            opts, args = getopt.getopt(argv[1:], "h:a", ["help", "address="])
            if len(opts) > 0:
                for o, a in opts: 
                    if o in ("-a", "--address"):
                        bounds(a)
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
        
def bounds(address): 
    """ 
    Retrieves the bounds for the given address 
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
                        print "Name: %s; Bounds: %s" % (name, b)
    except IOError:
        print sys.stderr, 'Could not open URL.'


def usage(argv):
    """ Prints usage message """
    print "%s --address [address]" % argv[0]

if __name__ == "__main__":
  sys.exit(main())