import argparse
import csv
import json
import logging
import logging.config
import time

import googlemaps
import yaml
from addict import Dict as Addict


class PlacesAPIWorker:
    def __init__(self, gmaps, grid, query, radius):
        """Initialization
        @param gmaps
        @param grid
        @param query
        @param radius

        """
        self.gmaps = gmaps
        self.grid = grid
        self.query = query
        self.radius = int(radius)

    def run(self):
        location = "%s,%s" % (self.grid["center_lat"], self.grid["center_lng"])
        response = self.gmaps.places(self.query, location=location, radius=self.radius)
        if response["status"] == "OK" and len(response["results"]) > 0:
            return response["results"]
        return None


def load_grids(file):
    grids_file_reader = csv.reader(open(file))
    grids_file_header = next(grids_file_reader)
    grids = []
    for row in grids_file_reader:
        grid = dict(zip(grids_file_header, row))
        grids.append(grid)
    return grids


def main(config_file):
    conf = Addict(yaml.safe_load(open(config_file, "r")))
    if conf.get("logging") is not None:
        logging.config.dictConfig(conf["logging"])
    else:
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
    logging.info("Initialize Google Maps service ")
    api_key = conf.get("API").get("KEY")
    gmaps = googlemaps.Client(key=api_key)

    grid_geocode_file = conf.get("input").get("filename")
    place_types = conf.get("input").get("query").split(",")
    radius = conf.get("input").get("radius")
    grids = load_grids(grid_geocode_file)
    logging.info("Geocode of %s grids loaded from %s", len(grids), grid_geocode_file)
    locations = []
    place_ids = []
    counter = 0
    logging.info("Start querying places of interest for each city grid ...")
    start_time = time.time()
    for grid in grids:
        for place_type in place_types:
            logging.debug(
                "Processing grid %s - %s with radius of %s",
                grid["id"],
                place_type,
                radius,
            )
            places_api_worker = PlacesAPIWorker(gmaps, grid, place_type, radius)
            results = places_api_worker.run()
            if results is not None:
                for result in results:
                    if result.get("place_id"):
                        place_id = result.get("place_id")
                        if place_id not in place_ids:
                            place_ids.append(place_id)
                            result["place_type"] = place_type
                            locations.append(result)
        counter += 1
        if counter % 100 == 0:
            logging.info(
                "%s city grid processed ... Elapsed time %s seconds",
                counter,
                round(time.time() - start_time, 4),
            )

    # Export query responses to file
    if len(locations) > 0:
        locations_fp = conf.get("output").get("existing_supermarkets_raw")
        with open(locations_fp, "w") as output_file:
            json.dump(locations, output_file, indent=4)
        logging.info(
            "%s target places of interest identified and dumped to %s",
            len(locations),
            locations_fp,
        )


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
