import pandas as pd
from geopandas.tools import sjoin
import geopandas as gpd

from ..files import get_cached_path
from .data_io import (
    load_gis_data,
    load_xls_data,
    load_shapefile_data,
    load_victorian_suburbs_metadata,
    load_aurin_data,
)


def group_repeat_names_vic(x):
    if x["loc_pid"] == "VIC2961":
        return "BELLFIELD - GRAMPIANS"
    elif x["loc_pid"] == "VIC2967":
        return "BELLFIELD - BANYULE"
    elif x["loc_pid"] == "VIC2976":
        return "HAPPY VALLEY - SWAN HILL"
    elif x["loc_pid"] == "VIC2984":
        return "HILLSIDE - MELTON"
    elif x["loc_pid"] == "VIC2990":
        return "REEDY CREEK - MITCHELL"
    elif x["loc_pid"] == "VIC2969":
        return "SPRINGFIELD - MACEDON RANGES"
    elif x["loc_pid"] == "VIC2963":
        return "STONY CREEK - HEPBURN"
    else:
        return x["suburb_name_combined"]


def parse_duplicates_from_victorian_councils(suburbs, councils):

    vic_locations = load_victorian_suburbs_metadata()
    duplicated_suburbs = vic_locations[
        vic_locations.duplicated(subset=["locality_name"])
    ]["locality_name"].unique()
    dup_suburbs_gdf = suburbs[
        suburbs["vic_loca_2"].apply(lambda x: x in duplicated_suburbs[:-1])
    ]

    dup_suburbs_join = sjoin(
        dup_suburbs_gdf.to_crs("EPSG:4326"), councils.to_crs("EPSG:4326"), how="left"
    )
    dup_suburbs_join["suburb_name_combined"] = dup_suburbs_join.apply(
        lambda x: f'{x["vic_loca_2"]} - {x["vic_lga__3"]}', axis=1
    )
    # note, this was identifired
    dup_suburbs_join["fixed_multinames"] = dup_suburbs_join.apply(
        group_repeat_names_vic, axis=1
    )
    dup_suburbs_join_dis = dup_suburbs_join.drop_duplicates(subset=["fixed_multinames"])
    double_name_converter = {
        code: name
        for code, name in zip(
            dup_suburbs_join_dis.loc_pid.values,
            dup_suburbs_join_dis.fixed_multinames.values,
        )
    }

    def change_multinames(x, cdict=double_name_converter):
        if x["loc_pid"] in cdict:
            return cdict[x["loc_pid"]]
        else:
            return x["vic_loca_2"]

    suburbs["fixed_names"] = suburbs.apply(change_multinames, axis=1)
    suburbs.rename(columns={"fixed_names": "Site_suburb"}, inplace=True)
    suburbs.loc[
        suburbs.Site_suburb == "ASCOT - HEPBURN", "Site_suburb"
    ] = "ASCOT - BALLARAT"
    return suburbs


def wrangle_victorian_gis_data(parse_duplicates=True):
    suburbs = load_gis_data("victoria_suburbs")
    councils = load_gis_data("victoria_councils")
    if parse_duplicates == True:
        suburbs = parse_duplicates_from_victorian_councils(suburbs, councils)
    return suburbs, councils


def convert_spreadsheet_colnames(df):
    name_change = {}
    drop_cols = []
    for col in df.columns:
        if "Statistical Area Level 1  (SA1) 7-Digit" in col:
            name_change[col] = "sa1_7d_code"
        elif "Suburb (SSC) Name" in col:
            name_change[col] = "suburb_name"
        elif "Economic Resources - Score" in col:
            name_change[col] = "ier_score"
        elif "Education and Occupation - Score" in col:
            name_change[col] = "ieo_score"
        elif "Resident Population" in col:
            name_change[col] = "population"
        elif "Relative Socio-economic Disadvantage - Score" in col:
            name_change[col] = "irsd_score"
        elif "Relative Socio-economic Advantage and Disadvantage - Score" in col:
            name_change[col] = "irsad_score"
        elif "Census Collection District" in col:
            name_change[col] = "cd_code"
        else:
            drop_cols.append(col)
    # print(drop_cols, name_change)
    return df.rename(columns=name_change).drop(columns=drop_cols)


def wrangle_abs_spreadsheet_datasets(dataset):
    df = load_xls_data(dataset, sheet_name="Table 1", header=[4, 5])
    df.columns = [" - ".join(i) for i in df.columns]
    df = convert_spreadsheet_colnames(df)
    return df


def get_victorian_abs_spreadsheets():
    df_2011 = wrangle_abs_spreadsheet_datasets("seifa_2011_sa1")
    df_2016 = wrangle_abs_spreadsheet_datasets("seifa_2016_sa1")
    return df_2011, df_2016


def get_sa1_gis_dataset(dataset, sa1_code, state_code, state_number):
    gdf = load_shapefile_data(dataset)
    gdf = gdf[["geometry", sa1_code, state_code]]
    gdf[state_code] = pd.to_numeric(
        gdf[state_code], downcast="integer", errors="coerce"
    )

    gdf = gdf[gdf[state_code] == state_number]
    gdf[sa1_code] = pd.to_numeric(gdf[sa1_code], downcast="integer", errors="coerce")
    return gdf


def combine_victorian_abs_spreadsheets(df_2011=None, df_2016=None):
    if (type(df_2011) == type(None)) | (type(df_2016) == type(None)):
        df_2011, df_2016 = get_victorian_abs_spreadsheets()
    gdf_2016 = get_sa1_gis_dataset("sa1_gis_2016", "SA1_7DIG16", "STE_CODE16", 2)
    gdf_2011 = get_sa1_gis_dataset("sa1_gis_2011", "SA1_7DIG11", "STE_CODE11", 2)
    df_l = []
    for year, df_rename in zip([2016, 2011], [df_2016, df_2011]):
        print(f"processing year {year}")
        df_rename["sa1_7d_code"] = pd.to_numeric(
            df_rename["sa1_7d_code"], downcast="integer", errors="coerce"
        )
        df_rename.dropna(subset=["sa1_7d_code"], inplace=True)
        df_rename = df_rename[
            (df_rename["sa1_7d_code"] < 3000000) & (df_rename["sa1_7d_code"] >= 2000000)
        ]
        scores = [x for x in df_rename.columns if "score" in x]
        for score in scores:
            df_rename[score] = pd.to_numeric(df_rename[score], errors="coerce")
        df_l.append(df_rename)
    gdf_2016 = gdf_2016.merge(
        df_l[0], left_on="SA1_7DIG16", right_on="sa1_7d_code", how="left"
    )
    gdf_2011 = gdf_2011.merge(
        df_l[1], left_on="SA1_7DIG11", right_on="sa1_7d_code", how="left"
    )

    return gdf_2016, gdf_2011


def combine_2006_dataset():
    CD_2006 = load_shapefile_data("seifa_2006_cd_shapefile")
    seifa_2006 = wrangle_abs_spreadsheet_datasets("seifa_2006_cd")
    CD_2006["CD_CODE06"] = pd.to_numeric(CD_2006["CD_CODE06"]).astype("int")
    seifa_2006.columns = [
        "cd_code",
        "irsad_score",
        "irsd_score",
        "ier_score",
        "ieo_score",
        "population",
    ]
    seifa_2006["cd_code"] = pd.to_numeric(seifa_2006["cd_code"], errors="coerce")
    seifa_2006.dropna(subset=["cd_code"], inplace=True)
    seifa_2006["cd_code"] = seifa_2006["cd_code"].astype("int")
    seifa_2006 = seifa_2006[
        (seifa_2006["cd_code"] > 2000000) & (seifa_2006["cd_code"] < 3000000)
    ]
    CD_2006 = CD_2006.merge(
        seifa_2006[
            [
                "cd_code",
                "ier_score",
                "ieo_score",
                "irsad_score",
                "irsd_score",
                "population",
            ]
        ],
        left_on="CD_CODE06",
        right_on="cd_code",
        how="left",
    )
    return CD_2006


def get_aurin_datasets_vic():
    gdf_1986, gdf_1991, gdf_1996, gdf_2001 = load_aurin_data(
        ["seifa_1986_aurin", "seifa_1991_aurin", "seifa_1996_aurin", "seifa_2001_aurin"]
    )
    return gdf_1986, gdf_1991, gdf_1996, gdf_2001


def convert_cds_colnames_gdf(df):
    name_change = {}
    drop_cols = []
    keep_cols = ["geometry", "ier_score", "ieo_score", "irsd_score", "irsad_score"]
    for col in list(df.columns):
        # print(col)
        if "index_of_economic_resources" in col:
            name_change[col] = "ier_score"

        elif "index_of_education_and_occupation" in col:
            name_change[col] = "ieo_score"

        elif "rural_index_of_relative_socio_economic_advantag" in col:
            name_change[col] = "rirsa_score"
        elif "urban_index_of_relative_socio_economic_advantag" in col:
            name_change[col] = "uirsa_score"
        elif "index_of_relative_socio_economic_disadvantage" in col:
            name_change[col] = "irsd_score"
        elif "_population" in col:
            name_change[col] = "population"
        elif "isad" in col:
            name_change[col] = "irsad_score"
        elif col not in keep_cols:
            drop_cols.append(col)

    return df.rename(columns=name_change).drop(columns=drop_cols)


def calc_area(gdf, crs="EPSG:32756"):
    return gdf.geometry.to_crs(crs).area


def w_avg(df, values, weights):

    d = df[values]
    w = df[weights]

    out = (d * w).sum() / w.sum()
    return out


def preprocess_victorian_datasets(force_rebuild=False, save_file=True):
    preprocessed_path = get_cached_path("preprocessed_vic_seifa.csv")
    if (preprocessed_path.exists() == False) or (force_rebuild == True):
        print("Downloading and assembling Victorian data. This may take a moment.")
        gdf_2016, gdf_2011 = combine_victorian_abs_spreadsheets()
        # print('df_comb max year before combining with gdf', df_comb.year.max())
        gdf_2006 = combine_2006_dataset()
        gdf_1986, gdf_1991, gdf_1996, gdf_2001 = get_aurin_datasets_vic()
        suburbs_coordinates, _ = wrangle_victorian_gis_data()
        concat_stack = []
        for year, df in zip(
            [
                2011,
                2016,
                1986,
                1991,
                1996,
                2001,
                2006,
            ],
            [
                gdf_2011,
                gdf_2016,
                gdf_1986,
                gdf_1991,
                gdf_1996,
                gdf_2001,
                gdf_2006,
            ],
        ):
            print(f"Processing {year}")
            if year < 2011:
                df_rename = convert_cds_colnames_gdf(df)
            else:
                df_rename = df
            df_union = gpd.overlay(
                df_rename.to_crs("EPSG:4326"), suburbs_coordinates.to_crs("EPSG:4326")
            )
            df_union["area"] = calc_area(df_union)
            df_union["area"] = df_union["area"].fillna(0)
            col_dict = {}
            for col in [
                "ieo_score",
                "ier_score",
                "irsad_score",
                "rirsa_score",
                "uirsa_score",
                "irsd_score",
            ]:
                if col in df_union.columns:
                    col_dict[col] = df_union.groupby("Site_suburb").apply(
                        w_avg, col, "area"
                    )

            out = pd.DataFrame(col_dict).reset_index()
            out["year"] = year
            concat_stack.append(out)
        total_df = pd.concat(concat_stack)
        if save_file == True:
            total_df.to_csv(preprocessed_path, index=False)
        else:
            return total_df

    total_df = pd.read_csv(preprocessed_path, na_values=["-"])
    return total_df
