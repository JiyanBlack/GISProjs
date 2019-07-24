import shapefile
from pyproj import Proj, transform

def getWKT_PRJ (epsg_code):
    import urllib
    wkt = urllib.urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(epsg_code))
    remove_spaces = wkt.read().replace(" ","")
    output = remove_spaces.replace("\n", "")
    return output

shp_folder = "C:/blog/pyproj/shp/"
shpf = shapefile.Reader(shp_folder + "Ireland_LA.shp")
wgs_shp = shapefile.Writer(shapefile.POLYGON)

fields = shpf.fields
wgs_fields = wgs_shp.fields

for name in fields:
    if type(name) == "tuple":
        continue
    else:
        args = name
        wgs_shp.field(*args)

records = shpf.records()

for row in records:
    args = row
    wgs_shp.record(*args)


input_projection = Proj(init="epsg:29902")
output_projection = Proj(init="epsg:4326")

geom = shpf.shapes()

for feature in geom:
    # if there is only one part
    if len(feature.parts) == 1:
        # create empty list to store all the coordinates
        poly_list = []
        # get each coord that makes up the polygon
        for coords in feature.points:
           x, y = coords[0], coords[1]
           # tranform the coord
           new_x, new_y = transform(input_projection, output_projection, x, y)
           # put the coord into a list structure
           poly_coord = [float(new_x), float(new_y)]
           # append the coords to the polygon list
           poly_list.append(poly_coord)
       # add the geometry to the shapefile.
        wgs_shp.poly(parts=[poly_list])
else:
    # append the total amount of points to the end of the parts list
    feature.parts.append(len(feature.points))
    # enpty list to store all the parts that make up the complete feature
    poly_list = []
    # keep track of the part being added
    parts_counter = 0

    # while the parts_counter is less than the amount of parts
    while parts_counter < len(feature.parts) - 1:
        # keep track of the amount of points added to the feature
        coord_count = feature.parts[parts_counter]
        # number of points in each part
        no_of_points = abs(feature.parts[parts_counter] - feature.parts[parts_counter + 1])
        # create list to hold individual parts - these get added to poly_list[]
        part_list = []
        # cut off point for each part
        end_point = coord_count + no_of_points

        # loop through each part
        while coord_count < end_point:
            for coords in feature.points[coord_count:end_point]:
                x, y = coords[0], coords[1]
                # tranform the coord
                new_x, new_y = transform(input_projection, output_projection, x, y)
                # put the coord into a list structure
                poly_coord = [float(new_x), float(new_y)]
                # append the coords to the part list
                part_list.append(poly_coord)
                coord_count = coord_count + 1
    # append the part to the poly_list
    poly_list.append(part_list)
    parts_counter = parts_counter + 1
# add the geometry to to new file
wgs_shp.poly(parts=poly_list)


wgs_shp.save(shp_folder + "Ireland_LA_wgs.shp")

prj = open(shp_folder + "Ireland_LA_wgs.prj", "w")
epsg = getWKT_PRJ("4326")
prj.write(epsg)
prj.close()