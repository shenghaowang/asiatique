import argparse
import logging
import logging.config
import yaml
import json
import pandas as pd
from addict import Dict as Addict


def catch_supermarkets(grid_id, dist_df, max_driving_time):
    caught_dist_df = dist_df.loc[(dist_df["grid_id"] == grid_id) & \
                                 (dist_df["driving_time"] <= max_driving_time)]
    return caught_dist_df.shape[0]


def compute_density(grid_id, grid_population, supermarket_counts):
    if int(grid_id) not in supermarket_counts:
        return float(grid_population) / 1
    return float(grid_population) / int(supermarket_counts[grid_id])


def main(config_file):
    conf = Addict(yaml.safe_load(open(config_file, 'r')))
    if conf.get("logging") is not None:
        logging.config.dictConfig(conf["logging"])
    else:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
    raw_file = conf.get("output").get("grid_to_supermarket_dist_raw")
    dist_data = []
    with open(raw_file, encoding='utf-8') as f:
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
    logging.info("%s distance query results written to %s",
                 len(dist_data), output_file)

    supermarket_counts = {}
    max_driving_time = int(conf.get("max_driving_time"))
    for grid_id in dist_df["grid_id"].unique():
        supermarket_counts[grid_id] = catch_supermarkets(grid_id, dist_df, max_driving_time)
    
    population_file = conf.get("input").get("grid_population_file")
    logging.info("Loading simulated population of city grids from %s", population_file)
    population_df = pd.read_csv(population_file)
    population_df["density"] = population_df.apply(lambda pop: \
        compute_density(pop["id"], pop["population"], supermarket_counts), axis=1)
    density_df = population_df[["id", "density"]]

    supermarket_density_file = conf.get("output").get("supermarket_density_file")
    density_df.to_csv(supermarket_density_file, index=False)
    logging.info("Density of supermarkets written to %s", supermarket_density_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True,
                        help="directory of the config file")
    args = parser.parse_args()
    try:
        main(args.config)
    except:
        logging.exception("Unhandled error during processing")
        raise