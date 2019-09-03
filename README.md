Project Asiatique: Locations to open new supermarkets in Malaysia
======

Requirements
-----

- python >= 3.5


Installation
-----

```bash
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```


Processing OSM building shapefile
----

- select data of target region, e.g. Penang
- calculate geometric center of selected buildings in geocode
- calculate floor area of selected buildings

```bash
source env/bin/activate
python3 read_shp_file.py
```


Searching for potential supermarket competitors
----

- see `config.sample.yml`
- require key of Google Places API

```bash
source env/bin/activate
python3 places_finder.py -c config.sample.yml
```

Deriving grid population
----

- see `Penang.ipynb`

```bash
source env/bin/activate
jupyter notebook
```
