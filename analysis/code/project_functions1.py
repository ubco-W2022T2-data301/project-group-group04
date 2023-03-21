# coding=utf-8
"""A collection of project functions for Gavin's portion of the project"""
import sys


from functools import cache
import pathlib
from typing import TypedDict
import pandas as pd
import geopandas as gpd
import numpy as np

__all__: tuple[str, ...] = (
    "PROJECT_ROOT",
    "is_heavy_metal",
    "load_and_process_healthdata",
    "load_and_process",
    "load_preprocessed_1",
    "load_toml",
)

if sys.version_info >= (3, 11):
    from tomllib import load as load_toml
else:
    from tomli import load as load_toml  # cspell: ignore tomli


class Loading(TypedDict):
    cols_to_drop: list[str]
    ignore_params: list[str]


class Config(TypedDict):
    heavy_metals: list[str]
    Loading: Loading


PROJECT_ROOT: pathlib.Path = pathlib.Path(__file__).parent.parent.parent.resolve()
with open(pathlib.Path(__file__).parent / "config1.toml", "rb") as cfg:
    config: Config = load_toml(cfg)  # type: ignore

__HEAVY_METALS__ = set(config["heavy_metals"])


@cache
def is_heavy_metal(substance: str) -> bool:
    """Determine if a parameter name is considered a heavy metal

    Parameters
    ----------
    substance : str
        Parameter name to check

    Returns
    -------
    bool
        Whether or not the parameter is a heavy metal
    """
    return any(heavy_metal in substance for heavy_metal in __HEAVY_METALS__)


def load_preprocessed_1(
    geodata: pathlib.Path,
    data: pathlib.Path,
    *,
    use_pyarrow: bool = False,
    gpd_kwargs: dict = dict(),
) -> gpd.GeoDataFrame:
    """Load already processed data that is formatted and cleaned to be useable here

    Parameters
    ----------
    geodata : pathlib.Path
        The file to load geodata from. Must contain a column titled CBSAFP.
    data : pathlib.Path
        The file to load the air quality data from. Must contain a column titled CBSAFP.
    use_pyarrow : bool, optional
        Should pyarrow be used to as a speedup for pd.read_csv, by default False
    gpd_kwargs : dict, optional
        Optional keyword arguments to pass to gpd.read_file, like engine arguments. , by default dict()

    Returns
    -------
    gpd.GeoDataFrame
        The loaded preprocessed data
    """
    base = gpd.read_file(geodata, **gpd_kwargs)  # type: ignore
    base["CBSAFP"] = base["CBSAFP"].astype("float64")
    return base.merge(  # type: ignore
        pd.read_csv(data, engine=("pyarrow" if use_pyarrow else None)),
        how="right",
        right_on="CBSAFP",
        left_on="CBSAFP",
    )


def load_and_process_healthdata(*, use_pyarrow: bool = False) -> gpd.GeoDataFrame:
    """Load and do basic processing on the data to remove extraneous information for the health data

    Parameters
    ----------
    use_pyarrow : bool, optional
        Should pyarrow be used to as a speedup for pd.read_csv, by default False

    Returns
    -------
    gpd.GeoDataFrame
        The loaded and processed health data
    """
    healthdata = pd.read_csv(
        PROJECT_ROOT
        / "data/raw/PLACES__Local_Data_for_Better_Health__Census_Tract_Data_2022_release.csv",
        usecols=[
            "StateAbbr",
            "StateDesc",
            "CountyName",
            "CountyFIPS",
            "LocationName",
            "Data_Value",
            "Low_Confidence_Limit",
            "High_Confidence_Limit",
            "TotalPopulation",
            "Geolocation",
            "LocationID",
        ],
        engine=("pyarrow" if use_pyarrow else None),
    ).loc[lambda frame: ~frame["StateDesc"].isin({"Alaska", "Hawaii"})]
    healthdata["Longitude"] = healthdata["Geolocation"].apply(
        lambda x: float(x[7:-1].split(" ")[0])
    )
    healthdata["Latitude"] = healthdata["Geolocation"].apply(
        lambda x: float(x[7:-1].split(" ")[1])
    )
    healthdata["Pop_With_Asthma"] = (
        healthdata["Data_Value"] * healthdata["TotalPopulation"]
    )
    healthdata["CountyState"] = (
        healthdata["CountyName"] + ", " + healthdata["StateAbbr"]
    )
    point_based = healthdata.groupby("CountyFIPS")[
        ["Pop_With_Asthma", "TotalPopulation", "CountyState", "Longitude", "Latitude"]
    ].agg(
        {
            "Pop_With_Asthma": "sum",
            "TotalPopulation": "sum",
            "CountyState": "min",
            "Longitude": "mean",
            "Latitude": "mean",
        }
    )
    point_based["Percentage"] = (
        point_based["Pop_With_Asthma"] / point_based["TotalPopulation"]
    )
    return gpd.GeoDataFrame(point_based, geometry=gpd.points_from_xy(point_based.Longitude, point_based.Latitude))  # type: ignore


def load_and_process(
    years: range, *, use_pyarrow: bool = False, gpd_kwargs: dict = dict()
) -> gpd.GeoDataFrame:
    """Load and do basic processing on the data to remove extraneous information.

    Parameters
    ----------
    years : range
        Range of years for which to load data for.

    Returns
    -------
    gpd.GeoDataFrame
        The loaded and basic processed dataframe with geographic shape data
    """
    pd_kwargs = {"engine": "pyarrow"} if use_pyarrow else {}
    _years = list(years)
    df = (
        pd.concat(
            (
                pd.read_csv(
                    (PROJECT_ROOT / f"data/raw/annual_conc_by_monitor_{x}.csv"),
                    usecols=[
                        "Year",
                        "CBSA Name",
                        "Parameter Name",
                        "Arithmetic Mean",
                        "Units of Measure",
                        "State Name",
                        "State Code",
                        "Latitude",
                        "Longitude",
                        "Observation Count",
                        "Required Day Count",
                    ],
                    **pd_kwargs,
                )
                for x in _years
            )
        )
        .loc[
            lambda frame: (~frame["State Code"].isin({2, 15, 72}))
            & (~frame["Arithmetic Mean"].isna())
            & (frame["Observation Count"] >= frame["Required Day Count"])
            & ~frame["Parameter Name"].isin(config["Loading"]["ignore_params"])
            & ~frame["Parameter Name"].str.contains("Unadjusted")
        ]
        .merge(
            pd.concat(
                (
                    pd.read_csv(
                        (PROJECT_ROOT / f"data/raw/annual_aqi_by_cbsa_{x}.csv"),
                        usecols=[
                            "Year",
                            "CBSA",
                            "CBSA Code",
                            "Max AQI",
                            "90th Percentile AQI",
                            "Median AQI",
                            "Days with AQI",
                        ],
                        **pd_kwargs,
                    )
                    for x in _years
                )
            ),
            how="inner",
            left_on=["Year", "CBSA Name"],
            right_on=["Year", "CBSA"],
        )
        .drop(columns=["CBSA"])
    ).apply(
        lambda x: pd.Series(
            [
                x["Year"],
                x["State Name"],
                (
                    x["Arithmetic Mean"] * 1000
                    if x["Units of Measure"] == "Parts per million"
                    else x["Arithmetic Mean"]
                ),
                (
                    x["Units of Measure"]
                    if x["Units of Measure"] != "Parts per million"
                    else "Parts per billion"
                ),
                x["Parameter Name"],
                x["CBSA Code"],
                x["Max AQI"],
                x["90th Percentile AQI"],
                x["Median AQI"],
                x["CBSA Name"],
                x["Latitude"],
                x["Longitude"],
                x["Days with AQI"],
            ],
            index=[
                "Year",
                "State Name",
                "Arithmetic Mean",
                "Units of Measure",
                "Parameter Name",
                "CBSA Code",
                "Max AQI",
                "90th Percentile AQI",
                "Median AQI",
                "CBSA Name",
                "Latitude",
                "Longitude",
                "Days with AQI",
            ],
        ),
        axis=1,
    )
    df["Parameter Name"] = (
        df["Parameter Name"]
        .replace(
            {
                "Nitric oxide (NO)": "Nitric oxides",
                "Reactive oxides of nitrogen (NOy)": "Nitric oxides",
                "Oxides of nitrogen (NOx)": "Nitric oxides",
                "Nitrite PM2.5 LC": "Nitric oxides",
                "NOy - NO": "Nitric oxides",
            }
        )
        .apply(
            lambda x: "Ammonium compounds"
            if "Ammonium" in x
            else "Benzenes"
            if ("Xylene") in x
            or ("benzene" in x.lower())
            or (x in {"Toluene", "Styrene"})
            else "Heavy Metals"
            if is_heavy_metal(x)
            else "Various Particulates"
            if (x == "Sodium Ion Pm2.5 LC") or ("PM2.5 LC" in x)
            else x
        )
    )
    df["Max AQI"] = df["Max AQI"].map(
        lambda x: x if 0 <= x <= 500 else 501 if x > 500 else 0
    )
    df = (
        df.groupby(["Year", "CBSA Name", "Parameter Name", "CBSA Code"])
        .agg(
            {
                "Arithmetic Mean": np.median,
                "Units of Measure": "min",
                "State Name": "min",
                "Max AQI": np.median,
                "90th Percentile AQI": np.median,
                "Median AQI": np.median,
                "Latitude": np.median,
                "Longitude": np.median,
                "Days with AQI": np.median,
            }
        )
        .reset_index()
        .loc[
            lambda x: x["Parameter Name"].isin(
                i
                for i in x["Parameter Name"].unique()
                if len(np.where(x["Parameter Name"] == i)[0]) >= 410
            )
        ]
        .reset_index(drop=True)
    )
    return gpd.read_file(
        PROJECT_ROOT / "data/raw/cb_2018_us_cbsa_500k/cb_2018_us_cbsa_500k.shp",
        **gpd_kwargs,
    ).merge(  # type: ignore
        df,
        how="right",
        left_on="NAME",
        right_on="CBSA Name",
    )
