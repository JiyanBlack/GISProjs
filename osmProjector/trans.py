#!/usr/bin/env python
"""
OSM Projection Converter
Planning and Transport Research Centre (PATREC)

This script is used to convert OSM database files from one projection to 
another. Note it does use Python 2 as there seems to be some issues with 
geographic libraries on macOS with Python 3 still.
"""


__author__ = "Tristan Reed"
__version__ = "0.1.0"

# python trans.py perth-map.osm 4283 gda50.osm 28350

""" Import required libraries. """
import pyproj, sys, textwrap, tqdm
import xml.etree.cElementTree as ElementTree


def main():

    """ Check that we have supplied four arguments. """
    if (len(sys.argv) == 5):

        """ Open up the input file using ElementTree. """
        et_data = ElementTree.parse(sys.argv[1])

        """ Create the Input and Output EPSG PyProj objects. """
        source_proj = pyproj.Proj(init = 'epsg:' + sys.argv[2])
        dest_proj = pyproj.Proj(init = 'epsg:' + sys.argv[4])

        """ Iterate through each element. """
        for element in tqdm.tqdm(et_data.getroot()):

            """ See if it is the Bounds. """
            if (element.tag == "bounds"):

                """ Get the four values from the XML. """
                min_lon = float(element.attrib['minlon'])
                min_lat = float(element.attrib['minlat'])
                max_lon = float(element.attrib['maxlon'])
                max_lat = float(element.attrib['maxlat'])

                """ Project the minimum values. """
                min_x, min_y = pyproj.transform(source_proj, dest_proj, min_lon, 
                    min_lat)

                """ Project the maximum values. """
                max_x, max_y = pyproj.transform(source_proj, dest_proj, max_lon, 
                    max_lat)

                """ Update the XML file. """
                element.set('minlon', min_x)
                element.set('minlat', min_y)
                element.set('maxlon', max_x)
                element.set('maxlat', max_y)
            
            """ See if it is a Node. """
            if (element.tag == "node"):

                """ Get the two values from the XML. """
                lon = float(element.attrib['lon'])
                lat = float(element.attrib['lat'])

                """ Project the  values. """
                node_x, node_y = pyproj.transform(source_proj, dest_proj, lon, 
                    lat)

                """ Update the XML file. """
                element.set('lon', node_x)
                element.set('lat', node_y)
        
        """ Write the output to file. """
        et_data.write(sys.argv[3])

    else:

        """ Print the help information for the user. """
        print(textwrap.dedent("""
        OSM Projection Converter: Usage Instructions
        --------------------------------------------
        osmconverter.py <in_file> <in_epsg> <out_file> <out_epsg>
        --------------------------------------------
        'in_file': path to the input network;
        'in_epsg': EPSG of the input network;
        'out_file': path to write the output network to;
        'out_epsg': EPSG of the output network.
        --------------------------------------------
        e.g.: osmconverter.py osm_network.osm 4326 osm_out.osm 28350
        """))


if __name__ == "__main__":

    """ This is executed when run from the command line. """
    main()