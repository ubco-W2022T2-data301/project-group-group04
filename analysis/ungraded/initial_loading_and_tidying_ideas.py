import pandas as pd
import numpy as np
aqi = pd.concat(pd.read_csv(f"./data/raw/annual_aqi_by_cbsa_{x}.csv") for x in range(2011,2023))
conc = pd.concat(pd.read_csv(f"./data/raw/annual_conc_by_monitor_{x}.csv") for x in range(2011,2023))
res = conc.merge(aqi, left_on=["Year", "CBSA Name"], right_on=["Year","CBSA"])

#Excess Location information

ret = res.drop(columns=["State Code","County Code", "CBSA", "Local Site Name", "Address", "Latitude", "Longitude", "Datum"])

# High Null value columns

ret = res.drop(columns=["1st Max Non Overlapping Value", "1st NO Max DateTime", "2nd Max Non Overlapping Value", "2nd NO Max DateTime", "Date of Last Change", "Sample Duration"])

# Sample value (not actual value columns)

ret = ret.drop(ret.index[ret["Parameter Name"].isin(x for x in ret["Parameter Name"].unique() if "sample" in x.lower())])

# Parameters caught by that generator statement:
sample_data_cols = ["Sample Flow Rate- CV", "Sample Volume", "Elapsed Sample Time", "Sample Min Baro Pressure", "Sample Max Baro Pressure", "Sample Flow Rate CV - Teflon Filter", "Sample Flow Rate CV - Nylon Filter", "Sample Flow Rate CV - Quartz Filter", "Sample Volume - Teflon Filter", "Sample Volume - Nylon Filter", "Sample Volume - Quartz Filter"]

# Temperature, Pressure, Humidity, Radiation, and Precipitation 

ret = ret.drop(ret.index[ret["Parameter Name"].isin(x for x in ret["Parameter Name"].unique() if "temperature" in x.lower() or "pressure" in x.lower() or "humidity" in x.lower() or "radiation" in x.lower() or "precipitation" in x.lower())])

# Parameters caught by that generator statement:
temp_press_humid_rad_precip_cols =  ["Average Ambient Temperature", "Average Ambient Pressure", "Outdoor Temperature", "Relative Humidity ", "Solar radiation", "Barometric pressure", "Rain/melt precipitation", "Ambient Min Temperature", "Ambient Max Temperature", "Temperature Difference", "Ultraviolet radiation", "Indoor Temperature", "Ultraviolet radiation (type B)", "Net radiation", "Virtual Temperature", "Average Ambient Temperature for URG3000N", "Average Ambient Pressure for URG3000N"]

# Wind and Light Information

ret = ret.drop(ret.index[ret["Parameter Name"].isin(x for x in ret["Parameter Name"].unique() if "wind" in x.lower() or "light" in x.lower())])

# Parameters caught by that generator statement:
wind = ["Wind Speed - Scalar', 'Wind Direction - Scalar', 'Wind Speed - Resultant', 'Wind Direction - Resultant', 'Std Dev Hz Wind Direction", "Std Dev Hz Wind Speed", "Peak Wind Gust", "Vertical Wind Speed", "Std Dev Vt Wind Speed", "Vert Wind Direction", "Std Dev Vt Wind Direction", "Light scatter", "Light scatter (miles visibility)", "Light scatter (ug/m3)", "Light Absorption Coeffiecient"]

# Chloropiphenols https://en.wikipedia.org/wiki/Polychlorinated_biphenyl

ret = ret.drop(ret.index[ret["Parameter Name"].isin(x for x in ret["Parameter Name"].unique() if "chlorobiphenyl" in x.lower() or "mixture pcb" in x.lower())])

# More chlorine compounds

ret = ret.drop(ret.index[ret["Parameter Name"].isin(x for x in ret["Parameter Name"].unique() if "dichloro" in x.lower())])

# Random chemicals

ret = ret.drop(ret.index[ret["Parameter Name"].isin(x for x in ret["Parameter Name"].unique() if "(tsp) stp" in x.lower() or "(tsp) lc" in x.lower()])

# Xylenes

ret = ret.drop(ret.index[ret["Parameter Name"].isin(x for x in ret["Parameter Name"].unique() if "xylene" in x.lower())])

# Unadjusted

ret = ret.drop(ret.index[ret["Parameter Name"].isin(x for x in ret["Parameter Name"].unique() if "unadjusted" in x.lower())])

# Parameters with 10 or less measurements

ret = ret.drop(ret.index[ret["Parameter Name"].isin(x for x in ret["Parameter Name"].unique() if len(np.where(ret["Parameter Name"]==x)[0]) <= 100)])

# Mixing Height

ret = ret.drop(ret.index[ret["Parameter Name"] == "Mixing Height"])

# Other useless columns

ret =ret.drop(columns=["Site Num", "Pollutant Standard", "CBSA Code", "Certification Indicator", "Completeness Indicator"])

# Remove ~50K rows which contain the parameters with the lowest occurance 

ret = ret.drop(ret.index[ret["Parameter Name"].isin(x for x in sorted({k:len(np.where(ret["Parameter Name"]==k)[0]) for k in ret["Parameter Name"].unique()}.items(), key=lambda x: x[1])[:118])])
