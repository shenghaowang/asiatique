Project Asiatique: Locations to open new supermarkets in Malaysia
======

Project Organization
------------
    ├── README.md          <- The top-level README for developers using this project.
    ├── raw
    │   ├── gis_osm_buildings_a_free_1.dbf
    │   └── gis_osm_buildings_a_free_1.shp      <- The original OSM shape file of buildings in Malaysia, Singapore, and Brunei.
    │
    ├── data
    │   ├── penang_residential_buildings.csv    <- Geocode and floor area of the residential buildings in Penang.
    │   ├── grid_center_geocode.csv             <- Centric geocode of the 1km x 1km grids, generated using QGIS.
    │   ├── penang_grid_EPSG3857_WGS84_v3.csv   <- Boundaries and parent district of the grids, exported from QGIS.
    │   ├── penang_grid_EPSG3857_WGS84_v3.shp   <- Shape file of the grids, exported from QGIS.
    │   ├── penang_grid_population.csv          <- Text file of the grids with simulated grid population.
    │   └── penang_grid_population.shp          <- Shape file of the grids with simulated grid population.
    │
    ├── notebooks
    │   ├── 1.0-simulate-population-distribution.ipynb  <- Simulate gridwise population distribution across Penang.
    │   ├── 2.0-develop-supermarkets-layer.ipynb        <- Build shape file of existing supermarket players.
    │   └── 3.0-calculate-customer-density.ipynb        <- Calculate customer density for grids and build shape file.
    │ 
    ├── config
    │   ├── grid_population_layer_builder.yml   <- Config parameters for building population distribution shape file.
    │   ├── places_api_config.yml               <- Config parameters for extracting locations of existing supermarket and grocery stores.
    │   └── dist_api_config.yml                 <- Config parameters for calculating driving time between the locations of customers and supermarkets.
    │
    └── src
        ├── osm_preprocessor.py                 <- Script for reading information from OSM shape file.
        └── grid_population_layer_builder.py    <- Script for generating population distribution shape file.

Requirements
------------

- python >= 3.5


Installation
------------

```bash
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```


Processing OSM building shapefile
------------

- select data of target region, e.g. Penang
- calculate geometric center of selected buildings in geocode
- calculate floor area of selected buildings

```bash
source env/bin/activate
python3 src/osm_preprocessor.py
```

Simulating population distribution across city
------------

- see `config/grid_population_layer_builder.yml`

```bash
source env/bin/activate
python3 src/grid_population_layer_builder.py -c config/grid_population_layer_builder.yml
```

Searching for potential supermarket competitors
------------

- see `config/places_api_config.yml`
- require key of Google Places API

```bash
source env/bin/activate
python3 src/supermarkets_finder.py -c config/places_api_config.sample.yml
```