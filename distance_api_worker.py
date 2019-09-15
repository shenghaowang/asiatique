import argparse
import logging
import logging.config
import yaml
from addict import Dict as Addict


class DistAPIWorker:
    def __init__(self, api_key, root_url, city_grid, supermarket):
        """Initialization.
        @param api_key
        @param root_url
        @param city_grid
        @param supermarket

        """
        self.api_key = api_key
        self.root_url = root_url
        self.city_grid = city_grid
        self.supermarket = supermarket

    def _form_url(self):
        


def main(config_file):
    conf = Addict(yaml.safe_load(open(config_file, 'r')))
    if conf.get("logging") is not None:
        logging.config.dictConfig(conf["logging"])
    else:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
    


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