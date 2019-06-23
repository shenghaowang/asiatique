import pandas as pd
import shapefile as shp


def read_shapefile(sf):
    """
    Read a shapefile into a Pandas dataframe with a 'coords'
    column holding the geometry information. This uses the pyshp
    package
    """
    fields = [x[0] for x in sf.fields][1:]
    print(fields)
    print("type of fields: ", type(fields))
    print("length of fields: ", len(fields))
    records = sf.records()
    print(records)
    print(records[0][5])
    print("type of records: ", type(records[0]))
    #print(records[0].shape)
    shps = [s.points for s in sf.shapes()]
    #print(shps)

    df = pd.DataFrame(columns=fields, data=records[0])
    df = df.assign(coords=shps)

    return df


def main():
    #shp_path = '/home/swang/Desktop/shenghao-repos/asiatique/MYS_adm/MYS_adm0.shp'
    shp_path = '/Users/shenghao/Desktop/shenghao-repos/asiatique/MYS_adm/MYS_adm0.shp'
    sf = shp.Reader(shp_path)
    print(sf)
    print("type of sf: ", type(sf))
    print("shape of sf: ", sf.shapes())
    shp_df = read_shapefile(sf)
    print(shp_df)


if __name__ == "__main__":
    main()
