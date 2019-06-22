import fiona


def read_shape(shp_fp):
    with fiona.open(shp_fp) as src:


def main():
    shp_f = '/home/swang/Desktop/shenghao-repos/asiatique/MYS_adm/MYS_adm0.shp'
    read_shape(shp_f)


if __name__ == "__main__":
    main()
