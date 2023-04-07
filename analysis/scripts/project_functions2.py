import geopandas as gpd
import geoplot as gplt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# aqi = pd.concat(pd.read_csv(f"../data/raw/annual_aqi_by_cbsa_{year}.csv") for year in range(2011, 2023))

# concentration = pd.concat(pd.read_csv(f"../data/raw/annual_conc_by_monitor_{year}.csv") for year in range(2011, 2023))


def processing(
    src1="../data/raw/annual_aqi_by_cbsa_year.csv",
    src2="../data/raw/annual_conc_by_monitor_year.csv",
    columns=[
        "CBSA Name",
        "Median AQI",
        "Max AQI",
        "90th Percentile AQI",
        "State Name",
        "Pollutant Standard",
        "Method Name",
        "Year",
        "Days CO",
        "Days NO2",
        "Days Ozone",
        "Days PM2.5",
        "Days PM10",
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


def wrangling(df=processing()):
    # df2 = df[df["Parameter Name"] == "Relative Humidity "]
    # df2 = df2.groupby(["CBSA Name"])[["Arithmetic Mean"]].mean().reset_index()
    # list = []
    # for i in df2["Arithmetic Mean"]:
    #     if i < 40:
    #         list.append("Dry")
    #     elif i < 60:
    #         list.append("Moderate")
    #     else:
    #         list.append("Humid")
    # df2["Dryness"] = list

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
    )

    # return df2.drop(columns=["Arithmetic Mean"]).merge(df, on="CBSA Name", how="right")
    # df2.assign(Dryness = ("Dry" if x < 40 else "Moderate" if x < 60 else "Humid" for x in df2["Arithmetic Mean"]))
    # print(df.columns)


def mapprep(
    df: pd.DataFrame = wrangling(),
    index="CBSA Name",
    values: list[str] = [
        "Median AQI",
        "Max AQI",
        "Days CO",
        "Days NO2",
        "Days Ozone",
        "Days PM2.5",
        "Arithmetic Mean",
    ],
    shapefile="../data/raw/cb_2018_us_cbsa_500k/cb_2018_us_cbsa_500k.shp",
    shapeindex="NAME",
):
    return gpd.GeoDataFrame(
        df.groupby([index])[values]
        .median()
        .merge(gpd.read_file(shapefile), how="inner", left_index=True, right_on=shapeindex)
        .dropna(inplace=False)
    )
