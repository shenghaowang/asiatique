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
    raw_file = conf.get("output").get("existing_supermarkets_raw")
    supermarkets = []
    with open(raw_file, encoding='utf-8') as f:
        for supermarket_raw in json.loads(f.read()):
            supermarket_obj = {}
            supermarket_obj["name"] = supermarket_raw.get("name")
            supermarket_obj["addr"] = supermarket_raw.get("formatted_address")
            geocode = supermarket_raw.get("geometry").get("location")
            supermarket_obj["lat"] = geocode.get("lat")
            supermarket_obj["lng"] = geocode.get("lng")
            supermarket_obj["type"] = supermarket_raw.get("place_type")
            supermarkets.append(supermarket_obj)
    
    supermarkets_df = pd.DataFrame(supermarkets)
    logging.info("%s supermarkets are located in the city", supermarkets_df.shape[0])
    supermarkets_df = supermarkets_df.drop_duplicates(subset=["lat", "lng"])
    logging.info("There are %s supermarkets left after duplicates removed", supermarkets_df.shape[0])
    grocery_df = supermarkets_df.loc[supermarkets_df["type"] == "grocery"]
    logging.info("%s of the results are grocery", grocery_df.shape[0])
    supermarkets_df = supermarkets_df.reset_index()
    supermarkets_df = supermarkets_df.loc[supermarkets_df["type"] == "supermarket"] 
    output_fp = conf.get("output").get("existing_supermarkets_data")
    supermarkets_df.to_csv(output_fp, index=False)
    logging.info("Information of existing supermarkets written to %s", output_fp)


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