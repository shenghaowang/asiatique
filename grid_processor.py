import pandas as pd
import pyproj


def convert_utm_coords(coords, inProj, outProj):
    lng, lat = pyproj.transform(inProj, outProj, coords[0], coords[1])
    return pd.Series([lng, lat])


def assign_grid(coords, grid_dict):
    for id, boundaries in grid_dict.items():
        if coords[0] > boundaries["left_lng"] and \
           coords[0] < boundaries["right_lng"] and \
           coords[1] > boundaries["bottom_lat"] and \
           coords[1] < boundaries["top_lat"]:
            return boundaries["id"]
    return None


def main():
    buildings_fp = "/home/swang/Desktop/shenghao-repos/asiatique/data/penang_residential_buildings.csv"
    grid_fp = "/home/swang/Desktop/shenghao-repos/asiatique/data/penang_grid_EPSG3857_WGS84.csv"
    grid_df = pd.read_csv(grid_fp)
    grid_df = grid_df.set_index("id")
    grid_dict = grid_df.to_dict('index')

    inProj = pyproj.Proj(init='epsg:3857')
    outProj = pyproj.Proj(init='epsg:4326')
    grid_df[["left_lng", "top_lat"]] = grid_df.apply(lambda row: convert_utm_coords(row[["left", "top"]], inProj, outProj), axis=1)
    grid_df[["right_lng", "bottom_lat"]] = grid_df.apply(lambda row: convert_utm_coords(row[["right", "bottom"]], inProj, outProj), axis=1)
    print(grid_df.head())

    ## Assign residential buildings to grid
    grid_dict = grid_df.to_dict('index')
    print(grid_dict)
    buildings_df = pd.read_csv(buildings_fp)
    buildings_df["grid"] = buildings_df[["center_lng", "center_lat"]].apply(lambda coords: assign_grid(coords, grid_dict))
    print(buildings_df.head())


if __name__ == "__main__":
    main()
