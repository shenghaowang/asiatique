import csv
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
    logging.info("%s distance query results written to %s", len(dist_data), output_file)


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