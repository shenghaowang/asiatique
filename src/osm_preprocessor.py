import pandas as pd
import numpy as np
import shapefile as shp
from area import area
from pathlib import Path


def read_shapefile(sf):
    """
    Read a shapefile into a Pandas dataframe with a 'coords'
    column holding the geometry information. This uses the pyshp
    package
    """
    fields = [x[0] for x in sf.fields][1:]
    print("fields: ", fields)
    records = [list(i) for i in sf.records()]
    shps = [s.points for s in sf.shapes()]

    df = pd.DataFrame(columns=fields, data=records)
    df = df.assign(coords=shps)

    return df


def get_center(coords):
    num_points = len(coords) - 1
    sum_lng = 0
    sum_lat = 0
    for i in range(num_points):
        point = coords[i]
        sum_lng += point[0]
        sum_lat += point[1]
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
    obj = {}
    obj['type'] = 'Polygon'
    obj['coordinates'] = [coords]

    return area(obj)


def is_penang(geocode):
    """Check whether a building is within Penang based on its geocode
    """
    lat, lng = geocode[1], geocode[0]
    if lat > 5.1175 and lat < 5.5929 and lng > 100.1691 and lng < 100.5569:
        return True
    else:
        return False


def main():
    #shp_path = '/home/swang/Desktop/shenghao-repos/asiatique/MYS_adm/MYS_adm0.shp'
    print(Path.cwd().parent)
    # shp_path = '/Users/shenghao/Desktop/shenghao-repos/asiatique/malaysia-singapore-brunei-latest-free.shp/gis_osm_buildings_a_free_1.shp'
    shp_path = 'raw/gis_osm_buildings_a_free_1.shp'
    sf = shp.Reader(shp_path)
    print("type of sf: ", type(sf))
    #print("shape of sf: ", sf.shapes())
    shp_df = read_shapefile(sf)
    residential_types = ["condominium", "apartment", "apartments",
                         "dormitory", "EiS_Residences", "residential",
                         "bungalow", "detached", "mix_used"]
    residential_df = shp_df.loc[shp_df["type"].isin(residential_types)]
    residential_df = residential_df.set_index("osm_id")
    residential_df["center"] = residential_df["coords"].apply(lambda coords: get_center(coords))
    # Boundary of Penang State, obtained from OpenStreetMap
    # lat: 5.1175 - 5.5929; lng: 100.1691 - 100.5569
    residential_df["is_penang"] = residential_df["center"].apply(lambda geocode: is_penang(geocode))
    penang_df = residential_df.loc[residential_df["is_penang"] == True]
    penang_df["area"] = penang_df["coords"].apply(lambda coords: calc_floor_area(coords))
    penang_df["center_lng"] = penang_df["center"].apply(lambda geocode: geocode[0])
    penang_df["center_lat"] = penang_df["center"].apply(lambda geocode: geocode[1])
    penang_df["area"] = penang_df["coords"].apply(lambda coords: calc_floor_area(coords))
    penang_df["id"] = np.arange(len(penang_df))
    penang_df = penang_df.reset_index()
    penang_df = penang_df.drop(["osm_id", "code", "fclass",
                                "is_penang", "center", "coords"], axis=1)
    penang_df = penang_df.set_index('id')
    print(penang_df.head())
    # penang_df.to_csv("data/penang_residential_buildings.csv", index=True)


if __name__ == "__main__":
    main()
