import geopandas as gpd
import geoplot as gplt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pyproj import CRS


def processing(
    src1="../data/raw/annual_aqi_by_cbsa_year.csv",
    src2="../data/raw/annual_conc_by_monitor_year.csv",
    columns=[
        "CBSA Name",
        "CBSA Code",
        "Median AQI",
        "State Name",
        "Pollutant Standard",
        "Method Name",
        "Year",
        "Parameter Name",
        "Arithmetic Mean",
        "Units of Measure",
    ],
    left=["Year", "CBSA"],
    right=["Year", "CBSA Name"],
    range=range(2011, 2023),
):
    return (
        pd.concat([pd.read_csv(src1.replace("year", str(i))) for i in range])
        .merge(
            pd.concat([pd.read_csv(src2.replace("year", str(i))) for i in range]),
            how="inner",
            left_on=left,
            right_on=right,
        )
        .loc[:, columns]
    )


def wrangling(df=processing(), col="Parameter Name", parameter=[True]):
    return (
        df.loc[df["Parameter Name"] == "Relative Humidity "]
        .groupby(["CBSA Name"])[["Arithmetic Mean"]]
        .median()
        .apply(
            lambda x: pd.Series(
                "Dry"
                if x["Arithmetic Mean"] < 40
                else "Moderate"
                if x["Arithmetic Mean"] <= 60
                else "Humid"
                if x["Arithmetic Mean"] > 60
                else None,
                index=["Dryness"],
            ),
            axis=1,
        )
        .merge(df, on="CBSA Name", how="right")
        .loc[df[col].isin(parameter) | (parameter == [True])]
    )


def mapprep(
    df: pd.DataFrame = wrangling(),
    index="CBSA Name",
    values: list[str] = ["Median AQI", "Arithmetic Mean", "Dryness"],
    shapefile="../data/raw/cb_2018_us_cbsa_500k/cb_2018_us_cbsa_500k.shp",
    shapeindex="NAME",
):
    return gpd.GeoDataFrame(
        df.groupby([index])[values]
        .median(numeric_only=True)
        .merge(gpd.read_file(shapefile), how="inner", left_index=True, right_on=shapeindex)
        .dropna(inplace=False)
    ).to_crs(CRS.from_user_input("EPSG:4269"))
