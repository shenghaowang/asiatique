import pandas as pd
import numpy as np
import shapefile as shp


def read_shapefile(sf):
    """
    Read a shapefile into a Pandas dataframe with a 'coords'
    column holding the geometry information. This uses the pyshp
    package
    """
    fields = [x[0] for x in sf.fields][1:]
    print(fields)
    print("type of fields: ", type(fields))
    print("length of fields: ", len(fields))
    # records = sf.records()
    records = [list(i) for i in sf.records()]
    #print(records)
    #print(records[0][5])
    print("type of records: ", type(records[0]))
    #print(records[0].shape)
    shps = [s.points for s in sf.shapes()]
    #print(shps)

    df = pd.DataFrame(columns=fields, data=records)
    df = df.assign(coords=shps)

    return df


def get_center(coords):
    num_points = len(coords)
    sum_lng = 0
    sum_lat = 0
    for coord in coords:
        sum_lng += coord[0]
        sum_lat += coord[0]
    return (sum_lng / num_points, sum_lat / num_points)


def get_cartesian(geocode):
    """Convert geocode into Cartesian coordinates
    """

    lat, lng = np.deg2rad(geocode[1]), np.deg2rad(geocode[0])
    R = 6378137 # Radius of earth in meter
    x = R * np.cos(lat) * np.cos(lng)
    y = R * np.cos(lat) * np.sin(lng)
    # z = R * np.sin(lat)
    return (x, y)


def calc_floor_area(coords):
    """Estimate area of a polygon according to the Cartesian coordinates of
    its boundary points.

    Ref: http://mathworld.wolfram.com/PolygonArea.html
    """
    # https://stackoverflow.com/questions/4681737/how-to-calculate-the-area-of-a-polygon-on-the-earths-surface-using-python

    num_points = len(coords)
    coords = list(map(get_cartesian, coords))
    A = 0
    for i in range(num_points):
        if i < num_points - 1:
            point1 = coords[i]
            point2 = coords[i+1]
        else:
            point1 = coords[num_points - 1]
            point2 = coords[0]

        # Take note the points of polygon are arranged ub clockwise order
        A += point1[0] * point2[1] - point2[0] * point1[1]

    return -(A / 2)


def main():
    #shp_path = '/home/swang/Desktop/shenghao-repos/asiatique/MYS_adm/MYS_adm0.shp'
    shp_path = '/home/swang/Desktop/shenghao-repos/asiatique/malaysia-singapore-brunei-latest-free.shp/gis_osm_buildings_a_free_1.shp'
    sf = shp.Reader(shp_path)
    #print(sf)
    print("type of sf: ", type(sf))
    #print("shape of sf: ", sf.shapes())
    shp_df = read_shapefile(sf)
    #print(shp_df.head())
    residential_df = shp_df.loc[shp_df["type"] == "residential"]
    residential_df = residential_df.set_index("osm_id")
    residential_df["center"] = residential_df["coords"].apply(lambda coords: get_center(coords))
    residential_df["area"] = residential_df["coords"].apply(lambda coords: calc_floor_area(coords))
    residential_df = residential_df.drop(["coords"], axis=1)
    print(residential_df.head())
    residential_df.to_csv("data/residential_buildings.csv")


if __name__ == "__main__":
    main()
