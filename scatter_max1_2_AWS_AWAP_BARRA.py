
# packages for loading netCDFs
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import timedelta, date, datetime, timezone
import xarray as xr
import itertools
import random

# Getting data from netCDF files
# Write the function
def load_AWS_netCDF(filename, var = ['temp', 'prec', 'humd', 'wspd', 'wdir', 'mslp'], lat_name='lati', lon_name='long', height_name='hght', station_id = 'bmid', station_name='name', time_name='time'):
    """
    This function loads a state's AWS hourly netCDF.
    """
    data = Dataset(filename, 'r')
    station_ids = data['bmid'][:]
    time = data['time'][:]
    # Convert the index to datetime (the indices are minutes since 1 Jan 1990 UTC)
    index_original = time
    date_index =  [datetime(1990,1,1,tzinfo=timezone.utc)+timedelta(0,0,0,0,i) for i in index_original]  
    # retrieve the variable data
    aws_data = {}
    aws_dfs = {}
    try:
        for v in var:
            aws_data[v] = data[v][:]
            aws_dfs[v] = pd.DataFrame(aws_data[v], 
                                      index=date_index,
                                      columns = station_ids)
    except IndexError:
        raise IndexError(f"{var} not found. \nPick a subset of ['temp', 'prec', 'humd', 'wspd', 'wdir', 'mslp']")
    
    # Convert the array of bytearrays to a list of names
    station_names = []
    for station in range(len(station_ids)):
        station_names.append(''.join([data['name'][station][i].decode('ascii') for i in range(50)]).strip())
    station_info = {}
    # Write a dataframe for the information:
    for i in range(len(station_ids)):
        station_info[station_ids[i]] = [station_names[i], 
                                        data['lati'][i],
                                        data['long'][i],
                                        data['hght'][i],
                                        ] 
    station_info_df = pd.DataFrame.from_dict(station_info,\
orient='index', columns=['name', 'lat', 'lon', 'h'])
    data.close()
    return station_info_df, aws_dfs

# Use the function for vic and nsw 
#vic_aws_info, vic_aws_data = load_AWS_netCDF("Documents/Project/AWS_hourly_station_data/AWS-Metar-data-VIC.nc", var=['prec'])
#nsw_aws_info, nsw_aws_data = load_AWS_netCDF("Documents/Project/AWS_hourly_station_data/AWS-Metar-data-NSW.nc", var=['prec'])
#for vdi
vic_aws_info, vic_aws_data = load_AWS_netCDF("Documents/AWS_data/AWS-Metar-data-VIC.nc", var=['prec'])
nsw_aws_info, nsw_aws_data = load_AWS_netCDF("Documents/AWS_data/AWS-Metar-data-NSW.nc", var=['prec'])


# The data has 30 min timesteps, and the value for precipitation is
# rainfall accumulation since 9am local time. The time is defined by 
# as minutes since 1900-01-01 00:00:00 
rain_rate_30min = {}
for station in vic_aws_info.index:
    # get rid of empties
    if np.sum(vic_aws_data['prec'][station])<1:
        continue
    # make the precipitation data from the station a pandas series
    ts = pd.Series(vic_aws_data['prec'][station])
    # restrict period
    ts = ts[ts.index >= datetime(2010,1,1,0, tzinfo=timezone.utc)]
    # remove sites with too many missing records, must be > 90% complete:
    missing = np.sum(np.isnan(ts))/len(ts)
    if missing > 0.1:
        continue
    # Calculate the first difference each step of the time series
    diff = ts.diff()
    # Where the following value is less than the preceeding (assuming
    # accumulation reset) replace with timeseries value
    diff[diff<0] = ts[diff<0]
    # need to catch the cases where the midnight rainfall is greater 
    # than the previous days accumulation. But ignoring this for now,
    # would matter more for smaller rainfall totals
    # Where the 30min rain amount is greater than 175mm replace with nan
#    diff[diff>175] = np.nan
    # Save this to the dict
    rain_rate_30min[station] = diff

halfhourly_rain_rate = pd.DataFrame(rain_rate_30min)
# from the half-hourly data, accumluate into hourly data, as the sum
# of rainfall of half hour before and on the hour. ie 1:30 + 2:00 together
# make 2:00 hourly. 
hourly_rain_rate = pd.DataFrame(rain_rate_30min).resample(rule = 'H', closed='right', label = 'right').sum() 
# collect daily rainfall totals
daily_rain_rate = pd.DataFrame(rain_rate_30min).resample(rule = 'D', closed='right', label = 'right').sum() 


# run all_functions.py first
# hourly BARRA_R data in files by year 
start_year = 2010
final_year = 2015

BARRA_hourly_time = {}
BARRA_hourly={}
for year in range(start_year, final_year + 1):
    BARRA_hourly[year], BARRA_lats, BARRA_lons, time = load_3D_netCDF(f'/g/data/w42/gt3409/BARRA_R/hourly_prcp/accum_prcp-BARRA_R-v1-{year}.nc', time_name='times')
    BARRA_hourly_time[year] = time

# write the data array
BARRA_hr_da = {}
for year in range(start_year, final_year + 1):
    # Coordinates for the data array
    coords = {'time': BARRA_hourly_time[year], 'lats': BARRA_lats, 'lons': BARRA_lons}
    BARRA_hr_da[year] = xr.DataArray(BARRA_hourly[year], coords = coords, dims = coords.keys()) 

# write timeseries BARRA of the corresponding grid point to station
BARRA_stations = {}
for station in hourly_rain_rate.keys():
    data={}
    BARRA_stations[station] = []
    for year in range(start_year, final_year + 1):
        data[year] = BARRA_hr_da[year].sel(lats = [vic_aws_info['lat'][station]], lons = [vic_aws_info['lon'][station]], method = 'nearest').data.ravel() # ravel changes to 1d array 
        BARRA_stations[station] = np.concatenate([BARRA_stations[station],data[year]]) 
bht = BARRA_hourly_time
BARRA_hourly_time = np.concatenate([bht[year] for year in range(start_year, final_year+1)])   

# Make BARRA timeseries into same pd dataframe set up
BARRA_time_index = [datetime(t.year, t.month, t.day, t.hour, t.minute, t.second, tzinfo =timezone.utc) for t in BARRA_hourly_time]
BARRA_timeseries = pd.DataFrame(BARRA_stations, index = BARRA_time_index)


# new bit on Mon 3 Dec
BARRA_stations_dict = {}
bsd = BARRA_stations_dict
for station in BARRA_timeseries.keys():
    max_2, max_1 =  np.sort(BARRA_timeseries[station])[-2:]
    bsd[station] = [max_1, max_2, max_1/max_2, max_1-max_2]

# plot this info on a scatter plot
# first set up the background
plt.figure(figsize = (7, 5))
plt.title("Victoria hourly rainfall maximums\n BARRA at AWS locations 2010-2015")
plt.xlabel("Second maximum (mm)")
plt.ylabel("First maximum (mm)")
plt.xlim(0, 150)
plt.ylim(0, 150)
x = np.arange(0, 150)
# ratio lines
for ratio in np.arange(1,4.1, 1):
    plt.plot(x, ratio * x, '--r', alpha = 0.3)
# difference lines
for diff in np.arange(0, 151, 20):
    plt.plot(x, x + diff, ':k', alpha = 0.3)
plt.scatter(pd.DataFrame(bsd).iloc[[1]], pd.DataFrame(bsd).iloc[[0]], color ='k', marker = '.')
# plt.savefig("Documents/images/hourly_BARRA_1stMax_v_2ndMax.png")

# do the same with AWS 
hrr = hourly_rain_rate
AWS_maximums_dict = {}
amd = AWS_maximums_dict
for station in hrr.keys():
    max_2, max_1 =  np.sort(hrr[station])[-2:]
    amd[station] = [max_1, max_2, max_1/max_2, max_1-max_2]


# first set up the background
plt.figure(figsize = (7, 5))
plt.title("Victoria hourly rainfall maximums\n AWS 2010-2015")
plt.xlabel("Second maximum (mm)")
plt.ylabel("First maximum (mm)")
plt.xlim(0, 150)
plt.ylim(0, 150)
x = np.arange(0, 150)
# ratio lines
for ratio in np.arange(1,4.1, 1):
    plt.plot(x, ratio * x, '--r', alpha = 0.3)
# difference lines
for diff in np.arange(0, 151, 20):
    plt.plot(x, x + diff, ':k', alpha = 0.3)
plt.scatter(pd.DataFrame(amd).iloc[[1]], pd.DataFrame(amd).iloc[[0]], color ='k', marker = '.')
# plt.savefig("Documents/images/hourly_AWS_1stMax_v_2ndMax.png")



# now compare AWS and BARRA
# first set up the background
plt.figure(figsize = (7,6))
plt.title("Victoria hourly rainfall maximums\n AWS and BARRA at AWS locations 2010-2015")
plt.xlabel("AWS maximum (mm)")
plt.ylabel("BARRA maximum (mm)")
plt.xlim(0, 150)
plt.ylim(0, 150)
x = np.arange(0, 150)
# ratio lines
for ratio in [.25, .33, .5, 1, 2, 3, 4]:
    plt.plot(x, ratio * x, '--r', alpha = 0.3)
# difference lines
for diff in np.arange(-140, 151, 20):
    plt.plot(x, x + diff, ':k', alpha = 0.3)
plt.scatter(pd.DataFrame(amd).iloc[[0]], pd.DataFrame(bsd).iloc[[0]], color ='k', marker = '.')
# plt.savefig("Documents/images/hourly_AWS_max_v_BARRA_max.png")


import statsmodels.api as sm
X = pd.DataFrame(amd).iloc[[0]].values[0]
Y =  pd.DataFrame(bsd).iloc[[0]].values[0]
model = sm.OLS(X, Y).fit()
model.summary()

# Now for AWAP daily
# write the data array
# Coordinates for the data array
coords = {'time': AWAP_times, 'lats': AWAP_lats, 'lons': AWAP_lons}
AWAP_data_array = xr.DataArray(prcp_data['AWAP_ann'], coords = coords, dims = coords.keys()) 

# write timeseries AWAP of the corresponding grid point to station
AWAP_stations = {}
for station in hourly_rain_rate.keys():
    data={}
    AWAP_stations[station] = AWAP_data_array.sel(lats = [vic_aws_info['lat'][station]], lons = [vic_aws_info['lon'][station]], method = 'nearest').data.ravel() # ravel changes to 1d array 

AWAP_maximums_dict = {}
for station in hrr.keys():
    max_2, max_1 =  np.sort(AWAP_stations[station])[-2:]
    AWAP_maximums_dict[station] = [max_1, max_2, max_1/max_2, max_1-max_2]


# first set up the background
plt.figure(figsize = (7, 5))
plt.title("Victoria daily rainfall maximums\n AWAP at AWS locations 2010-2015")
plt.xlabel("Second maximum (mm)")
plt.ylabel("First maximum (mm)")
plt.xlim(0, 350)
plt.ylim(0, 350)
x = np.arange(0, 350)
# ratio lines
for ratio in np.arange(1,4.1, 1):
    plt.plot(x, ratio * x, '--r', alpha = 0.3)
# difference lines
for diff in np.arange(0, 151, 20):
    plt.plot(x, x + diff, ':k', alpha = 0.3)
plt.scatter(pd.DataFrame(AWAP_maximums_dict).iloc[[1]], pd.DataFrame(AWAP_maximums_dict).iloc[[0]], color ='k', marker = '.')
# plt.savefig("Documents/images/hourly_AWAP_1stMax_v_2ndMax.png")



# AWAP all
AWAP_max1 = np.max(prcp_data['AWAP_ann'],0)    
AWAP_max2 = np.copy(prcp_data['AWAP_ann'])
AWAP_max2 = np.max(AWAP_max2*(AWAP_max2 != AWAP_max1),0) # set the AWAP_max value to 0, then find the next maximum 
# first set up the background
plt.figure(figsize = (7, 5))
plt.title("Victoria daily rainfall maximums\n AWAP over all SE Aust 2010-2015")
plt.xlabel("Second maximum (mm)")
plt.ylabel("First maximum (mm)")
plt.xlim(0, 300)
plt.ylim(0, 300)
x = np.arange(0, 300)
# ratio lines
for ratio in np.arange(1,4.1, 1):
    plt.plot(x, ratio * x, '--r', alpha = 0.3)
# difference lines
for diff in np.arange(0, 351, 50):
    plt.plot(x, x + diff, ':k', alpha = 0.3)
max_1 = AWAP_max1.reshape(AWAP_max1.size)
max_2 = AWAP_max2.reshape(AWAP_max2.size)

plt.scatter(max_2, max_1, color ='k', marker = '.', alpha = .1)
# plt.savefig("Documents/images/daily_AWAP_1stMax_v_2ndMax.png")


# BARRA all SE Aust
BARRA_max1 = np.max(prcp_data['BARRA_ann'],0)    
BARRA_max2 = np.copy(prcp_data['BARRA_ann'])
BARRA_max2 = np.max(BARRA_max2*(BARRA_max2 != BARRA_max1),0) # set the BARRA_max value to 0, then find the next maximum 
# first set up the background
plt.figure(figsize = (7, 5))
plt.title("Victoria daily rainfall maximums\n BARRA over all SE Aust 2010-2015")
plt.xlabel("Second maximum (mm)")
plt.ylabel("First maximum (mm)")
plt.xlim(0, 700)
plt.ylim(0, 700)
x = np.arange(0, 700)
# ratio lines
for ratio in np.arange(1,4.1, 1):
    plt.plot(x, ratio * x, '--r', alpha = 0.3)
# difference lines
for diff in np.arange(0, 701, 50):
    plt.plot(x, x + diff, ':k', alpha = 0.3)
max_1 = BARRA_max1.reshape(BARRA_max1.size)
max_2 = BARRA_max2.reshape(BARRA_max2.size)

plt.scatter(max_2, max_1, color ='k', marker = '.', alpha = .1)
plt.savefig("Documents/images/daily_BARRA_1stMax_v_2ndMax.png")



# BARRA vs AWAP all SE Aust
# first set up the background
plt.figure(figsize = (7, 5))
plt.title("Victoria daily rainfall maximums\n BARRA and AWAP SE Aust 2010-2015")
plt.xlabel("AWAP maximum (mm)")
plt.ylabel("BARRA maximum (mm)")
plt.xlim(0, 700)
plt.ylim(0, 700)
x = np.arange(0, 700)
# ratio lines
for ratio in [.25, .33, .5, 1, 2, 3, 4]:
    plt.plot(x, ratio * x, '--r', alpha = 0.3)
# difference lines
for diff in np.arange(-700, 701, 50):
    plt.plot(x, x + diff, ':k', alpha = 0.3)
# value lines
max_1 = BARRA_max1.reshape(BARRA_max1.size)
max_2 = BARRA_max2.reshape(BARRA_max2.size)

plt.scatter(AWAP_max1.reshape(AWAP_max1.size),BARRA_max1.reshape(BARRA_max1.size), color ='k', marker = 'o', alpha = .2, s = 8)
#plt.savefig("Documents/images/daily_BARRA_max_v_AWAP_max.png")



