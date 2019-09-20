import csv
import argparse
import logging
import logging.config
import yaml
import json
import googlemaps
from addict import Dict as Addict


class DistAPIWorker:
    def __init__(self, gmaps, city_grid, supermarket):
        """Initialization.
        @param gmaps
        @param city_grid
        @param supermarket

        """
        self.gmaps = gmaps
        self.city_grid = city_grid
        self.supermarket = supermarket

    def run(self):
        grid_geocode = (self.city_grid["center_lat"],
                        self.city_grid["center_lng"])
        supermarket_geocode = (self.supermarket["lat"],
                               self.supermarket["lng"])
        response = self.gmaps.distance_matrix(grid_geocode, supermarket_geocode,
                                              mode='driving')
        response["grid_id"] = self.city_grid.get("id")
        response["supermarket_id"] = self.supermarket.get("index")
        return response


def main(config_file):
    conf = Addict(yaml.safe_load(open(config_file, 'r')))
    if conf.get("logging") is not None:
        logging.config.dictConfig(conf["logging"])
    else:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
    supermarkets_file = conf.get("input").get("supermarkets_file")
    supermarkets_file_reader = csv.reader(open(supermarkets_file))
    supermarkets_file_header = next(supermarkets_file_reader)
    supermarkets = []
    for row in supermarkets_file_reader:
        supermarket = dict(zip(supermarkets_file_header, row))
        supermarkets.append(supermarket)

    grid_geocode_file = conf.get("input").get("grid_geocode_file")
    grids_file_reader = csv.reader(open(grid_geocode_file))
    grids_file_header = next(grids_file_reader)
    grids = []
    for row in grids_file_reader:
        grid = dict(zip(grids_file_header, row))
        grids.append(grid)

    api_key = conf.get("API").get("KEY")
    gmaps = googlemaps.Client(key=api_key)
    results = []
    for grid in grids[:2]:
        logging.info("grid: %s", grid)
        for supermarket in supermarkets[:3]:
            logging.info("supermarket: %s", supermarket)
            dist_api_worker = DistAPIWorker(gmaps, grid, supermarket)
            response = dist_api_worker.run()
            results.append(response)

    # Export query responses to file
    if len(results) > 0:
        results_fp = conf.get("output").get("grid_to_supermarket_dist_file")
        with open(results_fp, 'w') as output_file:
            json.dump(results, output_file, indent=4)
        logging.info("Query responses dumped to %s", results_fp)


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
