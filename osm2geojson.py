#!/usr/bin/python
"""
Generates a GeoJSON Feature Collection for buildings in a given OSM 
data file
"""

import sys
import getopt

import json 

from xml.dom import minidom

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
  
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h:o:b", ["help", "osm=", "building-ids="])
            
            xml = None
            bid = []
            
            if len(opts) > 0:
                for o, a in opts: 
                    if o in ("-o", "--osm"):
                        xml = a
                    elif o in ("-b", "--building-ids"):
                        bid = a
                    elif o in ("-h", "--help"):
                        usage(argv)
                        return 0
            else: 
                usage(argv)
            
            if xml != None and bid != None:
                # turn argument into list if needed
                if isinstance(bid, basestring):
                    bid = bid.split(',')

                # parse XML 
                xmldoc = minidom.parse(xml)
                
                # create and print GeoJSON 
                print geojson_for_building(xmldoc, bid)
            
        except getopt.error, msg:
             raise Usage(msg)
        
    except Usage, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "for help use --help"
        return 2
        
    return 0

def geojson_for_building(xmldoc, bids): 
    """ 
    Generates a GeoJSON Feature Collection from the specified OSM 
    building IDs
    """

    nodes = {}

    ns = xmldoc.getElementsByTagName('node')
    for n in ns:
        nid = n.attributes['id'].value
        lat = n.attributes['lat'].value
        lon = n.attributes['lon'].value
        
        nodes[nid] = { 'lat': lat, 'lng': lon }

    collection = { 'type': 'FeatureCollection' }
    features = []
    
    ways = xmldoc.getElementsByTagName('way')
    
    for way in ways:
        feature = { 'type': 'Feature' }
        properties = {}
        geometry = { 'type' : 'Polygon' }
        coordinates = []
        wid = way.attributes['id'].value
        # use the feature if it is specified in a list of building IDs, 
        # or if there are no building IDs specified 
        if wid in bids or len(bids) == 0:
            for child in way.childNodes:
                if child.localName == 'nd':
                    ref = child.attributes['ref'].value
                    try:
                        n = nodes[ref]
                        coordinates.append([float(n['lng']), float(n['lat'])]) 
                    except KeyError:
                        pass
                elif child.localName == 'tag':
                    k = child.attributes['k'].value
                    v = child.attributes['v'].value
                    properties[k] = v
        
            geometry['coordinates'] = [coordinates]
            feature['geometry'] = geometry
            feature['properties'] = properties
            features.append(feature)
        
    collection['features'] = features

    # construct the GeoJSON object 
    # geojson = {}
    # geojson['type'] = "Polygon"
    # coordinates = []
    # coordinates.append([sw['lng'], ne['lat']])
    # coordinates.append([ne['lng'], ne['lat']])
    # coordinates.append([ne['lng'], sw['lat']])
    # coordinates.append([sw['lng'], sw['lat']])
    # coordinates.append([sw['lng'], ne['lat']])
    # geojson['coordinates'] = [coordinates]
    
    return json.dumps(collection, indent=4, separators=(',', ': '))


def usage(argv):
    """ Prints usage message """
    print "%s --osm [osm data] --building-ids [,-separated building ids]" % argv[0]

if __name__ == "__main__":
  sys.exit(main())