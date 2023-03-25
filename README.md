# Group 04 - Regional Air Quality and its Effect on Asthma Prevalence in the US

- Your title can change over time.

## Important

To run this code locally, make sure at a minium all the packages listed in [requirements.txt](requirements.txt) are installed using your package manager of choice (`pip`, `conda`, `poetry`, etc), on at least python 3.9 or higher. However do note that installing [geoplot](https://residentmario.github.io/geoplot) may require installing system dependencies, such as `libgeos-dev` on linux, and may require [pillow](https://pillow.readthedocs.io/en/stable/) to be installed separately.

## Milestones

Details for Milestone are available on Canvas (left sidebar, Course Project).

## Describe your topic/interest in about 150-200 words

Our group will be analyzing the air quality among different locations within the United States and we will each be focusing on specific possible factors effecting the varying AQI levels. There are a large variety of locations outlined in our dataset and we will be narrowing in on locations based off of proximity to large bodies of water, landlocked metro areas, rural, urban, and industrialized areas. With these types of areas we will proceed to analyze any potential correlations that they have with amounts of chemical(s) that are present and are produced from various sources. With this we will be able to further explore and understand if there are any differences in air quality between rural vs urban locations, coastal vs central land locations, and industrialized vs rural. In addition to any findings and correlations we may determine, we would also like to assess any relations between AQI levels and asthma rates.

## Describe your dataset in about 150-200 words

This dataset is a combination of annual air quality index summaries sorted by CBSA (provided by EPA AirData, collected automatically, and then aggregated and published by the EPA) and asthma health data from the CDC, about the prevalence of asthma in 2020 and 2019 for 500 US cities. The data is from 2011 to 2022, and is provided in csv format under the public domain copyright exemption for US governmental works. The Air quality data provides data regarding the number of days air quality fell in the categories from "good" to "hazardous", as well as the average AQI for the year. Additionally, it also provides the number of days where certain pollutants, including but limited to CO, NO2, and Ozone were above the national air quality standard. The air concentration dataset includes metrics about different parameters that effect air quality in annual summaries for different CBSAs throughout the US and certain national baselines for acceptable quantities of these parameters. Further, the dataset provides data about average weather conditions in certain locations, and whether or not each monitor location had events that could be classified as "natural disasters" to help know if results might be skewed by any natural phenomena.

## Team Members

- Person 1: I'm Gavin Kendal-Freedman, a 3rd year at UBC Okanagan, Majoring in Chemistry, and taking a minor in Data Science, and I'm a dual US-Canadian citizen, originally from Seattle, WA, in the US, and I am a strong environmentalist.
- Person 2: Hello, I'm Sky and I'm a computer science major with a data science minor at UBC. I'm interested in data science and I'm excited to learn more about it in this course!

## Images

{You should use this area to add a screenshot of an interesting plot, or of your dashboard}

<img src ="images/test.png" width="100px">

## References

<a id="1">[1]</a> US Environmental Protection Agency. Air Quality System Data Mart [internet database] available via <https://www.epa.gov/outdoor-air-quality-data>. Accessed January 30, 2023.

<a id="2">[2]</a> PLACES. Centers for Disease Control and Prevention. Accessed January 30, 2023. <https://www.cdc.gov/places>

<a id="3">[3]</a> Aleksey Bilogur. Contiguous USA shapedata from geoplot's sample data available via <https://github.com/ResidentMario/geoplot-data>. Accessed March 2, 2023.

<a id="4">[4]</a> U.S. Census Bureau. 2018 Cartographic Boundary Files - Shapefile [internet database] available via <https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html>. Accessed March 4, 2023.


<!--

Can link to these in the following format, using the first number as an example: [[1]](#1)

Also, these can be referenced even from other files, using the syntax [[1]](/README.md#1)

-->

