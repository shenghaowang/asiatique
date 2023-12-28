import argparse
import json
import logging
import logging.config

import geopandas as gpd
import pandas as pd
import shapefile as shp
import yaml
from addict import Dict as Addict

from osm_preprocessor import read_shapefile


def catch_supermarkets(grid_id, dist_df, max_driving_time):
    caught_dist_df = dist_df.loc[
        (dist_df["grid_id"] == grid_id) & (dist_df["driving_time"] <= max_driving_time)
    ]
    return caught_dist_df.shape[0]


def compute_density(grid_id, grid_population, supermarket_counts):
    if int(grid_id) not in supermarket_counts:
        return float(grid_population) / 1
    return float(grid_population) / int(supermarket_counts[grid_id])


def main(config_file):
    conf = Addict(yaml.safe_load(open(config_file, "r")))
    if conf.get("logging") is not None:
        logging.config.dictConfig(conf["logging"])
    else:
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
    raw_file = conf.get("output").get("grid_to_supermarket_dist_raw")
    dist_data = []
    with open(raw_file, encoding="utf-8") as f:
        for dist_raw in json.loads(f.read()):
            dist_obj = {}
            dist_obj["grid_id"] = dist_raw["grid_id"]
            dist_obj["supermarket_id"] = dist_raw["supermarket_id"]
            dist_obj["status"] = dist_raw["status"]
            if dist_raw.get("rows"):
                row = dist_raw.get("rows")[0]
                if row.get("elements"):
                    element = row.get("elements")[0]
                    if element.get("distance"):
                        dist_obj["distance"] = element.get("distance").get("value")
                    else:
                        dist_obj["distance"] = None

                    if element.get("duration"):
                        dist_obj["driving_time"] = element.get("duration").get("value")
                    else:
                        dist_obj["driving_time"] = None
            else:
                dist_obj["distance"] = None
                dist_obj["driving_time"] = None
            dist_data.append(dist_obj)
    dist_df = pd.DataFrame(dist_data)
    output_file = conf.get("output").get("grid_to_supermarket_dist_data")
    dist_df.to_csv(output_file, index=False)
    logging.info("%s distance query results written to %s", len(dist_data), output_file)

    supermarket_counts = {}
    max_driving_time = int(conf.get("max_driving_time"))
    for grid_id in dist_df["grid_id"].unique():
        supermarket_counts[grid_id] = catch_supermarkets(
            grid_id, dist_df, max_driving_time
        )

    population_file = conf.get("input").get("grid_population_file")
    logging.info("Loading simulated population of city grids from %s", population_file)
    population_df = pd.read_csv(population_file)
    population_df["density"] = population_df.apply(
        lambda pop: compute_density(pop["id"], pop["population"], supermarket_counts),
        axis=1,
    )
    density_df = population_df[["id", "density"]]

    grid_shape = conf.get("input").get("grid_shape_file")
    sf = shp.Reader(grid_shape)
    shp_df = read_shapefile(sf)
    logging.info("Shape of shp_df: %s", shp_df.shape)
    logging.info(shp_df.head())
    density_shp_df = pd.merge(
        shp_df, density_df, left_on="id", right_on="id", how="outer"
    )
    density_shp_df = density_shp_df.drop("coords", axis=1)
    logging.info("Export supermarket density to text file")
    supermarket_density_file = conf.get("output").get("supermarket_density_file")
    density_shp_df.to_csv(supermarket_density_file, index=False)
    logging.info(density_shp_df.head())
    gdf = gpd.read_file(grid_shape)
    gdf = gdf.to_crs({"init": "epsg:3857"})
    gdf["density"] = density_shp_df["density"]
    supermarket_density_shape_file = conf.get("output").get(
        "supermarket_density_shape_file"
    )
    gdf.to_file(supermarket_density_shape_file)
    logging.info("Supermarket density added to the shape file of city grid layer")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", required=True, help="directory of the config file"
    )
    args = parser.parse_args()
    try:
        main(args.config)
    except Exception:
        logging.exception("Unhandled error during processing")
        raise
