# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %%
import pandas as pd
import geopandas as gpd
from vbadata.geo import suburbs_coordinates_df, councils_coordinates_df


# %%
boundaries_2011 = gpd.read_file(
    "/Users/garberj/data/vbadata_SEIFA/data_2011.gdb", layers=[0]
)
# boundaries_2011.head()


# %%
councils_df = councils_coordinates_df()


# %%
suburbs_raw = gpd.read_file(
    "/Users/garberj/repositories/vbadata/vbadata/data/geojson/suburb-10-vic.geojson"
)


# %%
vic_locations = pd.read_csv("/Users/garberj/data/vbadata_SEIFA/victorian_locations.csv")


# %%
vic_locations.head()


# %%
duplicated_suburbs = vic_locations[vic_locations.duplicated(subset=["locality_name"])][
    "locality_name"
].unique()


# %%
duplicated_suburbs


# %%
dup_suburbs_gdf = suburbs_raw[
    suburbs_raw["vic_loca_2"].apply(lambda x: x in duplicated_suburbs[:-1])
]


# %%
dup_suburbs_gdf.plot("vic_loca_2", legend=True, figsize=(10, 10))


# %%
dup_suburbs_gdf.sort_values("vic_loca_2")


# %%
councils_df.head()


# %%
from geopandas.tools import sjoin

dup_suburbs_join = sjoin(dup_suburbs_gdf, councils_df.to_crs("EPSG:4326"), how="left")


# %%
dup_suburbs_join.sort_values("vic_loca_2")


# %%
dup_suburbs_join["suburb_name_combined"] = dup_suburbs_join.apply(
    lambda x: f'{x["vic_loca_2"]} - {x["Site_Municipality"]}', axis=1
)


# %%
dup_suburbs_join.sort_values("suburb_name_combined")["suburb_name_combined"].values


# %%
def group_repeat_names(x):
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


# %%
dup_suburbs_join["fixed_multinames"] = dup_suburbs_join.apply(
    group_repeat_names, axis=1
)


# %%
dup_suburbs_join_dis = dup_suburbs_join.drop_duplicates(subset=["fixed_multinames"])


# %%
dup_suburbs_join_dis


# %%
double_name_converter = {
    code: name
    for code, name in zip(
        dup_suburbs_join_dis.loc_pid.values,
        dup_suburbs_join_dis.fixed_multinames.values,
    )
}


# %%
double_name_converter


# %%
def change_multinames(x, cdict=double_name_converter):
    if x["loc_pid"] in cdict:
        return cdict[x["loc_pid"]]
    else:
        return x["vic_loca_2"]


# %%
suburbs_raw["fixed_names"] = suburbs_raw.apply(change_multinames, axis=1)


# %%
suburbs_raw[suburbs_raw["loc_pid"] == "VIC2974"].head()


# %%
suburbs_raw.to_file(
    "/Users/garberj/repositories/vbadata/vbadata/data/geojson/qgis.geojson"
)


# %%
suburbs_raw = gpd.read_file(
    "/Users/garberj/repositories/vbadata/vbadata/data/geojson/suburbs_multiname.geojson"
)


# %%
suburbs_raw.head()


# %%


# %% [markdown]
# Geospatial representatin of 2011 and 2006 data

# %%
for fal in vic_locations[
    vic_locations.duplicated(subset=["postcode"])
].locality_name.values:
    print(fal)


# %%


# %%


# %%


# %%


# %%
ssc_2011 = pd.read_csv("/Users/garberj/data/vbadata_SEIFA/SSC_2011_AUST.csv")


# %%
ssc_2011 = ssc_2011[
    (ssc_2011["SSC_CODE_2011"] > 20000) & (ssc_2011["SSC_CODE_2011"] < 30000)
]


# %%
ssc_2011.head()


# %%
ssc_2011.tail()


# %%
ssc_2011.drop_duplicates(
    subset=["SSC_CODE_2011"],
    keep="first",
    inplace=True,
)


# %%
ssc_2011.shape


# %%
ssc_2011.shape


# %%
for name in ssc_2011["SSC_NAME_2011"]:
    if " Vic.)" in name:
        print(name)


# %%
ssc_2011 = pd.read_csv("/Users/garberj/data/vbadata_SEIFA/SSC_2011_AUST.csv")


# %%
ssc_2011 = ssc_2011[
    (ssc_2011["SSC_CODE_2011"] > 20000) & (ssc_2011["SSC_CODE_2011"] < 30000)
]


# %%
ssc_2011.head()


# %%
ssc_2011.tail()


# %%
ssc_2011.drop_duplicates(
    subset=["SSC_CODE_2011"],
    keep="first",
    inplace=True,
)


# %%
ssc_2011.shape


# %%
ssc_2011 = ssc_2011[(ssc_2011.SSC_CODE_2011 > 19999) & (ssc_2011.SSC_CODE_2011 < 30000)]


# %%
ssc_2011.shape


# %%
ssc_2011 = ssc_2011.drop_duplicates(subset="SSC_CODE_2011")


# %%
ssc_2011.shape


# %%
ssc_2006 = pd.read_excel("/Users/garberj/data/vbadata_SEIFA/ssc_2006.xlsx")


# %%
ssc_2006.shape


# %%
ssc_2011.shape


# %%
for name in ssc_2011["SSC_NAME_2011"]:
    if " Vic.)" in name:
        print(name)


# %%
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 10))
suburbs_raw.plot(ax=ax)
councils_df.boundary.plot(ax=ax, color="red")


# %%
df_2016 = pd.read_excel("/Users/garberj/data/vbadata_SEIFA/2016_SEIFA_SUBURB.xlsx")


df_2011 = pd.read_excel("/Users/garberj/data/vbadata_SEIFA/2011_SEIFA_SUBURB.xlsx")


# %%
df_2011 = df_2011[
    (df_2011["2011 State Suburb Code (SSC)"] > 19999)
    & (df_2011["2011 State Suburb Code (SSC)"] < 30000)
]


# %%
df_2011


# %%


# %%


# %%


# %%


# %%
print(df_2016.columns)


# %%
def convert_spreadsheet_colnames(df):
    name_change = {}
    drop_cols = []
    for col in df.columns:
        if ("Suburb (SSC) Code" in col) or ("state suburb code (ssc)" in col.lower()):
            name_change[col] = "suburb_code"
        elif "Suburb (SSC) Name" in col:
            name_change[col] = "suburb_name"
        elif "Economic Resources - Score" in col:
            name_change[col] = "ier_score"
        elif "Education and Occupation - Score" in col:
            name_change[col] = "ieo_score"
        elif "Resident Population" in col:
            name_change[col] = "population"
        else:
            drop_cols.append(col)
    print(drop_cols, name_change)
    return df.rename(columns=name_change).drop(columns=drop_cols)


# %%


def suburb_name_fix(x):
    if type(x) == str:
        if "(" in x:
            x = x.split("(")[0]
        return x.upper().strip()
    else:
        return x


# %%
df_vic_sub = df_2016[
    (df_2016["2016 State Suburb (SSC) Code"] < 30000)
    & (df_2016["2016 State Suburb (SSC) Code"] > 19999)
]


# %%
suburb_dict = df_vic_sub[
    ["2016 State Suburb (SSC) Code", "2016 State Suburb (SSC) Name"]
].to_dict("records")


# %%
df_out_l = []

for year, df in zip([2016, 2011], [df_2016, df_2011]):
    df_rename = convert_spreadsheet_colnames(df)
    df_rename = df_rename[
        (df_rename["suburb_code"] < 30000) & (df_rename["suburb_code"] > 19999)
    ]
    if year == 2006:

        df_rename = df_rename.merge(
            ssc_2006, left_on="suburb_code", right_on="SSC Code", how="left"
        )
        df_rename.rename(columns={"SSC Name": "suburb_name"}, inplace=True)
    if year == 2011:

        df_rename = df_rename.merge(
            ssc_2011[["SSC_CODE_2011", "SSC_NAME_2011"]],
            left_on="suburb_code",
            right_on="SSC_CODE_2011",
            how="left",
        )
        df_rename.rename(columns={"SSC_NAME_2011": "suburb_name"}, inplace=True)

    df_rename["year"] = year
    df_out_l.append(df_rename)


# %%
df_comb = pd.concat(df_out_l)


# %%
for name in df_comb.suburb_name.values:
    if " Vic.)" in name:
        print(name)


# %%
name_fixer_dict_2016 = {
    # 2016
    "Ascot (Ballarat - Vic.)": "ASCOT - BALLARAT",
    "Ascot (Greater Bendigo - Vic.)": "ASCOT - GREATER BENDIGO",
    "Bellfield (Banyule - Vic.)": "BELLFIELD - BANYULE",
    "Big Hill (Greater Bendigo - Vic.)": "BIG HILL - GREATER BENDIGO",
    "Big Hill (Surf Coast - Vic.)": "BIG HILL - SURF COAST",
    "Fairy Dell (Campaspe - Vic.)": "FAIRY DELL - CAMPASPE",
    "Golden Point (Ballarat - Vic.)": "GOLDEN POINT - BALLARAT",
    "Golden Point (Mount Alexander - Vic.)": "GOLDEN POINT - MOUNT ALEXANDER",
    "Happy Valley (Golden Plains - Vic.)": "HAPPY VALLEY - GOLDEN PLAINS",
    "Happy Valley (Swan Hill - Vic.)": "HAPPY VALLEY - SWAN HILL",
    "Hillside (East Gippsland - Vic.)": "HILLSIDE - EAST GIPPSLAND",
    "Hillside (Melton - Vic.)": "HILLSIDE - MELTON",
    "Killara (Wodonga - Vic.)": "KILLARA - WODONGA",
    "Merrijig (Mansfield - Vic.)": "MERRIJIG - MANSFIELD",
    "Moonlight Flat (Central Goldfields - Vic.)": "MOONLIGHT FLAT - CENTRAL GOLDFIELDS",
    "Moonlight Flat (Mount Alexander - Vic.)": "MOONLIGHT FLAT - MOUNT ALEXANDER",
    "Myall (Gannawarra - Vic.)": "MYALL - GANNAWARRA",
    "Newtown (Golden Plains - Vic.)": "NEWTOWN - GOLDEN PLAINS",
    "Newtown (Greater Geelong - Vic.)": "NEWTOWN - GREATER GEELONG",
    "Springfield (Macedon Ranges - Vic.)": "SPRINGFIELD - MACEDON RANGES",
    "Stony Creek (South Gippsland - Vic.)": "STONY CREEK - SOUTH GIPPSLAND",
    "Thomson (Greater Geelong - Vic.)": "THOMSON - GREATER GEELONG"
    #     #2011
    #     'Ascot (Ballarat - Vic.)': 'ASCOT - BALLARAT',
    #     'Ascot (Greater Bendigo - Vic.)': 'ASCOT - GREATER BENDIGO',
    #     'Bellfield (Banyule - Vic.)': 'BELLFIELD - BANYULE',
    #     'Big Hill (Greater Bendigo - Vic.)':'BIG HILL - GREATER BENDIGO' ,
    #     'Golden Point (Ballarat - Vic.)': 'GOLDEN POINT - BALLARAT',
    #     'Hillside (Melton - Vic.)': 'HILLSIDE - MELTON',
    #     'Merrijig (Mansfield - Vic.)': 'MERRIJIG - MANSFIELD',
    #     'Newtown (Greater Geelong - Vic.)': 'NEWTOWN - GREATER GEELONG',
    #     'Stony Creek (South Gippsland - Vic.)': 'STONY CREEK - SOUTH GIPPSLAND',
    #     'Thomson (Greater Geelong - Vic.)': 'THOMSON - GREATER GEELONG',
}


# %%
def fix_2016_multisuburbs(x, cdict=name_fixer_dict_2016):
    if x["suburb_name"] in cdict:
        return cdict[x["suburb_name"]]
    else:
        return x["suburb_name"]


# %%
df_comb["suburb_name_fix"] = df_comb.apply(fix_2016_multisuburbs, axis=1)


# %%
"ASCOT - BALLARAT" in df_comb.suburb_name_fix.values


# %%
df_comb["Site_suburb"] = df_comb.suburb_name_fix.apply(suburb_name_fix)


# %%
df_comb[df_comb["Site_suburb"] == "ASCOT - BALLARAT"]


# %%
df_2011.head()


# %%
df_comb

# %% [markdown]
# # Assemble 2006 geodataframes

# %%


# %%
CD_2006 = gpd.read_file(
    "/Users/garberj/data/vbadata_SEIFA/1259030002_cd06avic_shape/CD06aVIC.shp"
)


# %%
CD_2006.plot()


# %%
CD_2006.head()


# %%
CD_2006["CD_CODE06"] = pd.to_numeric(CD_2006["CD_CODE06"]).astype("int")


# %%
seifa_2006 = pd.read_excel("/Users/garberj/data/vbadata_SEIFA/seifa_2006_CD.xlsx")


# %%
seifa_2006.columns = [
    "cd_code",
    "irsad_score",
    "irsd_score",
    "ier_score",
    "ieo_score",
    "population",
]


# %%
seifa_2006.head()


# %%
seifa_2006 = seifa_2006[
    (seifa_2006["cd_code"] > 2000000) & (seifa_2006["cd_code"] < 3000000)
]


# %%
seifa_2006.head()


# %%
seifa_2006.tail()


# %%
CD_2006 = CD_2006.merge(
    seifa_2006[["cd_code", "ier_score", "ieo_score", "population"]],
    left_on="CD_CODE06",
    right_on="cd_code",
    how="left",
)


# %%
CD_2006.dtypes


# %%
CD_2006.plot("ier_score")


# %%


# %%
gdf_2001 = gpd.read_file(
    "/Users/garberj/data/vbadata_SEIFA/ABS_-_Socio-Economic_Indexes_for_Areas__SEIFA___CD__2001.json/data2516898914808603983.json"
)


# %%
gdf_1996 = gpd.read_file(
    "/Users/garberj/data/vbadata_SEIFA/ABS_-_Socio-Economic_Indexes_for_Areas__SEIFA___CD__1996.json/data7336844287967253519.json"
)
gdf_1996.head()


# %%
gdf_1991 = gpd.read_file(
    "/Users/garberj/data/vbadata_SEIFA/ABS_-_Socio-Economic_Indexes_for_Areas__SEIFA___CD__1991.json/data354505989715425060.json"
)


# %%
gdf_1991.columns


# %%
gdf_1986 = gpd.read_file(
    "/Users/garberj/data/vbadata_SEIFA/ABS_-_Socio-Economic_Indexes_for_Areas__SEIFA___CD__1986.json/data7355794508419511170.json"
)


# %%
gdf_1986.columns


# %%
gdf_1996.columns


# %%
gdf_2001 = gdf_2001[gdf_2001["state_name"] == "Victoria"]


# %%
gdf_2001.columns


# %%
gdf_2001.statistical_subdivision


# %%
def convert_cds_colnames(df):
    name_change = {}
    drop_cols = []
    keep_cols = ["geometry", "ier_score", "ieo_score"]
    for col in list(df.columns):
        print(col)
        if "index_of_economic_resources" in col:
            name_change[col] = "ier_score"
        #         elif "state_code"

        elif "index_of_education_and_occupation" in col:
            name_change[col] = "ieo_score"

        elif "_population" in col:
            name_change[col] = "population"
        elif col not in keep_cols:
            drop_cols.append(col)
    print(drop_cols)
    print(name_change)
    return df.rename(columns=name_change).drop(columns=drop_cols)


# %%
CD_2006.head()


# %%
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(20, 20))

rename_1996.to_crs("EPSG:4326").plot(ax=ax)
suburbs_coordinates.boundary.plot(ax=ax, alpha=0.5, color="black")


# %%
def calc_area(gdf, crs="EPSG:32756"):
    return gdf.geometry.to_crs(crs).area


# %%
def w_avg(df, values, weights):

    d = df[values]
    w = df[weights]
    return (d * w).sum() / w.sum()


# %%
out.reset_index().head()


# %%
suburbs_raw.head()


# %%
suburbs_coordinates = suburbs_raw[["geometry", "fixed_name"]].rename(
    columns={"fixed_name": "Site_suburb"}
)


# %%
concat_stack = []
for year, df in zip(
    [1986, 1991, 1996, 2001, 2006], [gdf_1986, gdf_1991, gdf_1996, gdf_2001, CD_2006]
):
    df_rename = convert_cds_colnames(df)
    df_union = gpd.overlay(df_rename.to_crs("EPSG:4326"), suburbs_coordinates)
    df_union["area"] = calc_area(df_union)
    agg_ieo = df_union.groupby("Site_suburb").apply(w_avg, "ieo_score", "area")
    agg_ier = df_union.groupby("Site_suburb").apply(w_avg, "ier_score", "area")

    out = pd.DataFrame({"ieo_score": agg_ieo, "ier_score": agg_ier}).reset_index()
    out["year"] = year
    concat_stack.append(out)


# %%
combined = pd.concat(concat_stack)


# %%
suburbs_raw


# %%
suburbs_raw.to_file(
    "/Users/garberj/repositories/vbadata/vbadata/data/geojson/suburbs_multiname.geojson",
    driver="GeoJSON",
)


# %%
combined[combined["Site_suburb"] == "ASCOT - BALLARAT"]


# %%
fig, ax = plt.subplots()
combined[combined["Site_suburb"] == "ABBOTSFORD"].plot(
    x="year", y="ier_score", ax=ax, label="Abbotsford"
)
combined[combined["Site_suburb"] == "COLLINGWOOD"].plot(
    x="year", y="ier_score", ax=ax, label="Collingwood"
)
combined[combined["Site_suburb"] == "SOUTH YARRA"].plot(
    x="year", y="ier_score", ax=ax, label="South Yarra"
)
combined[combined["Site_suburb"] == "SANDRINGHAM"].plot(
    x="year", y="ier_score", ax=ax, label="Sandringham"
)


# %%
combined[combined["Site_suburb"] == "GOLDEN POINT"]


# %%
total_df = pd.concat([combined, df_comb])


# %%
import plotly.express as px

# px.line(data_frame=total_df.dropna(subset=['Site_suburb']), x='year', y='ier_score', color='Site_suburb')


# %%
# checking the coverage

total_df["ier_nan"] = total_df["ier_score"].isna()


# %%
(total_df.groupby("Site_suburb")["ier_nan"].sum() > 0).sum()


# %%
total_df[total_df["Site_suburb"] == "NEWTOWN"]


# %%
total_df["Site_suburb"].value_counts().head(20)


# %%
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
suburbs_coordinates[
    suburbs_coordinates.Site_suburb.apply(lambda x: "MOONLIGHT FLA" in x)
].plot(ax=ax)
suburbs_coordinates[
    suburbs_coordinates.Site_suburb.apply(lambda x: "HAVELO" in x)
].boundary.plot(ax=ax, color="red")


# %%
ssc_2006.head()


# %%
ssc_2011.head()


# %%
suburbs_raw = gpd.read_file(
    "/Users/garberj/repositories/vbadata/vbadata/data/geojson/suburb-10-vic.geojson"
)


# %%
suburbs_raw.head()


# %%
suburbs_raw[suburbs_raw.vic_loca_2.apply(lambda x: "GOLDEN" in x)].plot()


# %%
from vbadata.data import PublicDataset

dataset = PublicDataset()
df_private = dataset.df_from_parquet()


# %%
df_private[df_private["Site_suburb"].apply(lambda x: "Golden Point" in x)]


# %%
df_2006[df_2006["2006 State Suburb code (SSC)"] == 20002]


# %%
df_2006[df_2006["2006 State Suburb code (SSC)"] > 20000]


# %%
# total_df['ier_score'] = pd.to_numeric(total_df['ier_score'], errors='coerce')
import numpy as np

total_df["ier_year_missed"] = (total_df["ier_score"].isna().astype("int")) * total_df[
    "year"
]
total_df["ier_year_missed"][total_df["ier_year_missed"] == 0] = np.nan


# %%
# import sys
# !conda install --yes --prefix {sys.prefix} numpy
# import seaborn as sns
px.bar(total_df[total_df["ier_year_missed"] > 0]["ier_year_missed"].value_counts())


# %%
total_df[["Site_suburb", "ieo_score", "ier_score", "year"]].to_csv(
    "/Users/garberj/repositories/vbadata/vbadata/data/seifa_timeseries_suburb.csv",
    index=True,
)


# %%
def plot_suburb_ts(df, suburbs, score="ier_score"):
    fig, ax = plt.subplots()
    for suburb in suburbs:
        df[df["Site_suburb"] == suburb].plot(x="year", y=score, ax=ax, label=suburb)
    return fig


# %%
fig = plot_suburb_ts(
    total_df,
    ["ABBOTSFORD", "SANDRINGHAM", "SOUTH YARRA", "COLLINGWOOD", "BRUNSWICK EAST"],
)


# %%
total_df[total_df.Site_suburb == "ABBOTSFORD"]


# %%
df_comb[df_comb.Site_suburb == "ABBOTSFORD"]


# %%
df_comb.head()


# %%
union_1996[union_1996["Site_suburb"] == "ABBOTSFORD"].plot()


# %%
from vbadata.mapping import create_plotly_choropleth


# %%
get_ipython().run_line_magic("pinfo", "create_plotly_choropleth")


# %%


# %%
gdf_2001.plot()


# %%
gdf_2001_union = gpd.overlay(gdf_2001, suburbs_coordinates)


# %%


# %%
gdf_2001_union["area"] = gdf_2001_union.geometry.to_crs("EPSG:32756").area


# %%


# %%
gdf_2001.plot("poa")

# %% [markdown]
# ## Archive

# %%
for name in ssc_2006.sort_values("SSC Name")["SSC Name"]:
    if "(" in name:
        print(name)


# %%
union_1996["area"] = calc_area(union_1996)


# %%
agg_ieo = union_1996.groupby("Site_suburb").apply(w_avg, "ieo_score", "area")
agg_ier = union_1996.groupby("Site_suburb").apply(w_avg, "ier_score", "area")

out = pd.DataFrame({"ieo_score": agg_ieo, "ier_score": agg_ier})

out.head()


# %%
rename_1996 = convert_cds_colnames(gdf_1996)


# %%
union_1996 = gpd.overlay(rename_1996.to_crs("EPSG:4326"), suburbs_coordinates)


# %%
rename_1996.columns
