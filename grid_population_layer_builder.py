import argparse
import pandas as pd
import pyproj
import time
import yaml
import logging
import logging.config
import shapefile as shp
import geopandas as gpd
from addict import Dict as Addict
from osm_preprocessor import read_shapefile


def convert_utm_coords(coords, inProj, outProj):
    lng, lat = pyproj.transform(inProj, outProj, coords[0], coords[1])
    return pd.Series([lng, lat])


def assign_grid(coords, grid_dict):
    for grid_id, boundaries in grid_dict.items():
        if coords[0] > boundaries["left_lng"] and \
           coords[0] < boundaries["right_lng"] and \
           coords[1] > boundaries["bottom_lat"] and \
           coords[1] < boundaries["top_lat"]:
            return str(grid_id)
    return None


def check_bungalow(building_type, area):
    return pd.Series([0, area]) \
            if building_type == 'bungalow' else pd.Series([area, 0])


def main(config_file):
    conf = Addict(yaml.safe_load(open(config_file, 'r')))
    if conf.get("logging") is not None:
        logging.config.dictConfig(conf["logging"])
    else:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")

    start_time = time.time()
    logging.info("Part I Load city grid layer")
    grid_fp = conf.get("input").get("grid_file")
    grid_df = pd.read_csv(grid_fp)
    grid_df["id"] = grid_df["id"].apply(lambda grid_id: str(grid_id))
    grid_df = grid_df.set_index("id")
    grid_df = grid_df.dropna()

    logging.info("Converting UTM coordinate system to geocode ...")
    inProj = pyproj.Proj(init='epsg:3857')
    outProj = pyproj.Proj(init='epsg:4326')
    grid_df[["left_lng", "top_lat"]] = grid_df.apply(lambda row: convert_utm_coords(row[["left", "top"]], inProj, outProj), axis=1)
    grid_df[["right_lng", "bottom_lat"]] = grid_df.apply(lambda row: convert_utm_coords(row[["right", "bottom"]], inProj, outProj), axis=1)
    grid_df["center_lng"] = (grid_df["left_lng"] + grid_df["right_lng"]) / 2
    grid_df["center_lat"] = (grid_df["top_lat"] + grid_df["bottom_lat"]) / 2
    logging.info("Write grid center geocode to file")
    grid_geocode_df = grid_df[["center_lng", "center_lat"]]
    grid_geocode_file = conf.get("output").get("grid_geocode_file")
    grid_geocode_df.to_csv(grid_geocode_file, index=True)
    logging.info("Elapsed time %s seconds ...",
                 round(time.time() - start_time, 4))

    logging.info("Part II Assign residential buildings to grids")
    grid_dict = grid_df.to_dict("index")
    buildings_fp = conf.get("input").get("residential_buildings_file")
    buildings_df = pd.read_csv(buildings_fp)
    logging.info("Range of longitude: %s - %s",
                 buildings_df["center_lng"].min(),
                 buildings_df["center_lng"].max())
    logging.info("Range of latitude: %s - %s",
                 buildings_df["center_lat"].min(),
                 buildings_df["center_lat"].max())
    buildings_df["grid"] = buildings_df.apply(lambda row: assign_grid(row[["center_lng", "center_lat"]], grid_dict), axis=1)
    buildings_df = buildings_df.set_index("id")
    logging.info("Elapsed time: %s seconds ...",
                 round(time.time() - start_time, 4))

    logging.info("Part III Compute gridwise total floor area")
    logging.info("Residential building types: %s",
                 buildings_df["type"].unique())
    buildings_df[["area", "area_bungalow"]] = buildings_df.apply(lambda row: check_bungalow(row["type"], row["area"]), axis=1)
    area_df = buildings_df.groupby(['grid'])['area', 'area_bungalow'].agg('sum')
    area_df = pd.merge(area_df, grid_df, left_index=True, right_index=True)
    area_df = area_df.drop(["left", "right", "top", "bottom",
                            "left_lng", "top_lat", "right_lng", "bottom_lat",
                            "center_lng", "center_lat"], axis=1)
    area_df = area_df.reset_index()
    logging.info("Shape of area_df: %s", area_df.shape)
    logging.info(area_df.head())
    logging.info("Elapsed time: %s seconds ...",
                 round(time.time() - start_time, 4))

    logging.info("Part IV Distribute city population into grids")
    district_df = area_df.groupby(["district"])['area', 'area_bungalow'].agg('sum')
    district_df["total_population"] = conf.get("district_population")
    district_df["bungalow_population"] = district_df["total_population"] / 100 * 5
    district_df["apartment_population"] = district_df["total_population"] - district_df["bungalow_population"]
    district_df = district_df.reset_index()
    logging.info(district_df)
    population_df = pd.merge(area_df, district_df[["district", "area", "apartment_population"]], on='district')
    population_df = population_df.rename(columns={
            "index": "grid_id",
            "area_x": "area",
            "area_bungalow_x": "area_bungalow",
            "area_y": "area_apartment_district",
            "apartment_population": "apartment_population_district"
    })
    population_df["population"] = population_df["apartment_population_district"] / population_df["area_apartment_district"] * population_df["area"] + \
                                        population_df["area_bungalow"] / 100 * 5
    population_df["grid_id"] = population_df["grid_id"].apply(lambda grid_id: int(grid_id))
    logging.info("Shape of population_df: %s", population_df.shape)
    logging.info(population_df.head())

    logging.info("Part V Incorporate grid population with shape file")
    grid_shape = conf.get("input").get("grid_shape_file")
    sf = shp.Reader(grid_shape)
    shp_df = read_shapefile(sf)
    logging.info("Shape of shp_df: %s", shp_df.shape)
    logging.info(shp_df.head())
    population_shp_df = pd.merge(shp_df, population_df[["grid_id", "population"]],
                                 left_on='id', right_on='grid_id', how='outer')
    population_shp_df["population"].fillna(0, inplace=True)
    population_shp_df = population_shp_df.drop(["grid_id", "coords"], axis=1)
    logging.info("Export grid population to text file")
    grid_population_file = conf.get("output").get("grid_population_file")
    population_shp_df.to_csv(grid_population_file, index=False)
    grid_shape_file = conf.get("input").get("grid_shape_file")
    gdf = gpd.read_file(grid_shape)
    gdf = gdf.to_crs({'init': 'epsg:3857'})
    gdf["population"] = population_shp_df["population"]
    grid_population_shape_file = conf.get("output").get("grid_population_shape_file")
    gdf.to_file(grid_population_shape_file)
    logging.info("Population info added to the shape file of city grid layer")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True,
                        help="directory of the config file")
    args = parser.parse_args()
    try:
        main(args.config)
    except Exception:
        logging.exception("Unhandled error during processing")
        raise
