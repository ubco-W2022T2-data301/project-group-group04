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
    "load_and_process",
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


def load_and_process(years: range) -> gpd.GeoDataFrame:
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
    return (
        gpd.read_file(
            PROJECT_ROOT / "data/raw/cb_2018_us_cbsa_500k/cb_2018_us_cbsa_500k.shp"
        )
        .merge(
            df,
            how="right",
            left_on="NAME",
            right_on="CBSA Name",
        )
    )
