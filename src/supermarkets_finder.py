import requests
import argparse
import logging
import logging.config
import yaml
import json
import pandas as pd
from addict import Dict as Addict


def main(config_file):
    conf = Addict(yaml.safe_load(open(config_file, 'r')))
    if conf.get("logging") is not None:
        logging.config.dictConfig(conf["logging"])
    else:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
    API_KEY = conf.get("API").get("KEY")
    base_url = conf.get("API").get("URL")
    # place_types = ["supermarkets", "convenience_store", "department_store", "store", "grocery"]
    place_types = ["supermarkets", "grocery"]
    locations = []
    for place in place_types:
        logging.info("Searching for %s in Penang", place)
        query = "query=" + place + "+in+Penang"
        url = base_url + query + "&key=" + API_KEY
        logging.info("url of API query: %s", url)
        response = requests.get(url)
        results = json.loads(response.text).get("results")
        logging.info("%s results are found.", len(results))
        for result in results:
            location = {}
            location["name"] = result.get("name")
            location["addr"] = result.get("formatted_address")
            geocode = result.get("geometry").get("location")
            location["lat"] = geocode.get("lat")
            location["lng"] = geocode.get("lng")
            location["type"] = place
            locations.append(location)

    places_df = pd.DataFrame(locations)
    places_df = places_df.drop_duplicates(subset=["lat", "lng"])
    places_df = places_df.reset_index()
    output_fp = conf.get("output").get("filename")
    places_df.to_csv(output_fp, index=False)
    logging.info("%s supermarkets are located in the city", places_df.shape[0])
    logging.info("Information of existing supermarkets written to %s",
                 output_fp)


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
