
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


# Do some stats for the hourly data
data = hourly_rain_rate
hourly_data_stats = {}
for station in data:
    data[station] = data[station][data[station]<175]
    stats = []
    # Rx1hr
    stats.append(np.nanmax(data[station]))
    # Rx3hr
    da = xr.DataArray(data[station], dims = ['time']).fillna(0)
    stats.append(float(np.max(da.rolling(time = 3).sum())))
    # Rx6hr
    stats.append(float(np.max(da.rolling(time = 6).sum())))
    # Rx12hr
    stats.append(float(np.max(da.rolling(time = 12).sum())))
    # Rx24hr
    stats.append(float(np.max(da.rolling(time = 24).sum())))
    # SDIIh average/median prcp for wet hours (prcp > 0.1)
    stats.append(np.nanmean(data[station][data[station]>0.1],0))
    stats.append(np.nanmedian(data[station][data[station]>0.1],0))
    # Count of hours when prcp amount is more than nnmm:
    # R1mmph
    stats.append(np.sum(data[station]>1,0))
    # R5mmph
    stats.append(np.sum(data[station]>5,0))
    # R10mmph
    stats.append(np.sum(data[station]>10,0))
    # R20mmph
    stats.append(np.sum(data[station]>20,0))
    # R30mmph
    stats.append(np.sum(data[station]>30,0))
    # max consecutive wet hours >0.1mm
    # cwh
    z = [(x[0], len(list(x[1]))) for x in itertools.groupby(data[station] > 0.1)]
    stats.append(max(z))
    # percentiles
    # 1 day return time for hourly data:
    stats.append(np.nanpercentile(data[station], 95.83, 0))
    # 1 week return time for hourly data
    stats.append(np.nanpercentile(data[station], 99.40, 0))
    # 1 month return time for hourly data
    stats.append(np.nanpercentile(data[station], 99.86, 0))
    # 1 year return time for hourly data
    stats.append(np.nanpercentile(data[station], 99.99, 0))
    hourly_data_stats[station] = stats
df = pd.DataFrame.from_dict(hourly_data_stats, orient='index', columns = ['rx1hr', 'rx3hr', 'rx6hr','rx12hr', 'rx24hr', 'sdiih_mean', 'sdiih_median', 'r1mmph', 'r5mmph', 'r10mmph', 'r20mmph', 'r30mmph','cwh', 'return1day', 'return7day', 'return30day', 'return1year']) 


# Do some stats for the daily data
data = daily_rain_rate
daily_data_stats = {}
for station in data:
    data[station] = data[station][data[station]<375] # vic record 24h rainfall
    stats = []
    # Rx1day
    stats.append(np.nanmax(data[station]))
    # Rx5day
    da = xr.DataArray(data[station], dims = ['time']).fillna(0)
    stats.append(float(np.max(da.rolling(time = 5).sum())))
    # SDII average/median prcp for wet days (prcp > 1mm)
    stats.append(np.nanmean(data[station][data[station]>1],0))
    stats.append(np.nanmedian(data[station][data[station]>1],0))
    # Count of days when prcp amount is more than nnmm:
    # r1mm
    stats.append(np.sum(data[station]>1,0))
    # R10mm
    stats.append(np.sum(data[station]>10,0))
    # R20mm
    stats.append(np.sum(data[station]>20,0))
    # R30mm
    stats.append(np.sum(data[station]>30,0))
    # R50mm
    stats.append(np.sum(data[station]>50,0))
    # max consecutive wet days
    # cwd
    z = [(x[0], len(list(x[1]))) for x in itertools.groupby(data[station]>1)]
    stats.append(max(z))
    # percentiles
    # r99p
    stats.append(np.nanpercentile(data[station][data[station]>1], 99, 0))    
    # r95p
    stats.append(np.nanpercentile(data[station][data[station]>1], 95, 0)) 
    # 1 month return time for daily data
    stats.append(np.nanpercentile(data[station], 96.67, 0))    
    # 1 year return time for daily data
    stats.append(np.nanpercentile(data[station], 99.73, 0))
    daily_data_stats[station] = stats
daily_df = pd.DataFrame.from_dict(daily_data_stats, orient='index', columns = ['rx1day', 'rx5day', 'sdii_mean','sdii_median', 'r1mm', 'r10mm', 'r20mm', 'r30mm', 'r50mm','cwd', 'r99p', 'r95p', 'return30day', 'return1year']) 



plt.figure(figsize=(20, 20))
i=0
for station in df[df['rx1hr']>100].index:
    i +=1
    plt.subplot(len(df[df['rx1hr']>100]),1, i)
    plt.plot(hourly_rain_rate[station][hourly_rain_rate[station]<175]) #175mm is the bom stated max for 60min in VIC http://www.bom.gov.au/water/designRainfalls/rainfallEvents/ausRecordRainfall.shtml
    plt.title(vic_aws_info['name'][station])
plt.savefig('Documents/Project/hourly_rain_vic_suspect.png')
plt.show()

# visualise Cumulative wet hours
for station in df.index:
    if df['cwh'][station][0]:
        plt.title("CWH")
        plt.scatter(random.randint(-100,100)/2000,df['cwh'][station][1], color='k', alpha = 0.2)
plt.xlim(-1, 1)
plt.show()

# visualise return rate probability
for station in df.index:                    
    plt.scatter(random.randint(-100,100)/2000, df['return1year'][station], color = 'k', alpha =0.2)                 
    plt.scatter(random.randint(-100,100)/2000+1, df['return30day'][station], color='k', alpha=0.2)
    plt.scatter(random.randint(-100,100)/2000+2, df['return7day'][station], color='k', alpha=0.2) 
    plt.scatter(random.randint(-100,100)/2000+3, df['return1day'][station], color='k', alpha=0.2)  
plt.title("Return period amount")
plt.xlim(-1, 4)                                                         
plt.show()   

for station in df.index: 
    plt.scatter(random.randint(-100,100)/2000+1, df['rx1hr'][station], color='k', alpha=0.2)                 
    plt.scatter(random.randint(-100,100)/2000+3, df['rx3hr'][station], color='k', alpha=0.2)  
    plt.scatter(random.randint(-100,100)/2000+6, df['rx6hr'][station], color='k', alpha=0.2)  
    plt.scatter(random.randint(-100,100)/2000+12, df['rx12hr'][station], color='k', alpha=0.2) 
    plt.scatter(random.randint(-100,100)/2000+24, df['rx24hr'][station], color='k', alpha=0.2) 
plt.title("Hourly maximum")
plt.xlim(0, 25)                                                         
plt.show()   

for station in df.index: 
    plt.scatter(random.randint(-100,100)/2000+1, df['r1mmph'][station], color='k', alpha=0.2)                 
    plt.scatter(random.randint(-100,100)/2000+2, df['r5mmph'][station], color='k', alpha=0.2)  
    plt.scatter(random.randint(-100,100)/2000+3, df['r10mmph'][station], color='k', alpha=0.2)  
    plt.scatter(random.randint(-100,100)/2000+4, df['r20mmph'][station], color='k', alpha=0.2) 
    plt.scatter(random.randint(-100,100)/2000+5, df['r30mmph'][station], color='k', alpha=0.2) 
plt.title("count of rain rate")
plt.xlim(0, 6)                                                         
plt.show()   

# plot dots to on awap and barra from daily aws in vic

AWS_lats = vic_aws_info['lat'][daily_rain_rate.keys()]
AWS_lons = vic_aws_info['lon'][daily_rain_rate.keys()]

aws_color = [np.mean(daily_rain_rate[i])*365 for i in daily_rain_rate] 
map_dots((np.nanmean(prcp_data['AWAP_ann'], 0)*365), BARRA_lats, BARRA_lons) 
                                                                                
aws_color = [np.nanpercentile(daily_rain_rate[i], 99) for i in daily_rain_rate] 
map_dots((np.nanpercentile(prcp_data['AWAP_ann'],99, 0)), BARRA_lats, BARRA_lons, levels = levels['day'], title = "AWAP and AWS R99p", cmap_label = "precipitation (mm)") 
#plt.savefig('Documents
map_dots((np.nanpercentile(prcp_data['BARRA_ann'],99, 0)), BARRA_lats,BARRA_lons, levels = levels['day'], title = "BARRA and AWS R99p", cmap_label = "precipitation (mm)") 
#plt.savefig('Documents

aws_color = [np.nanmax(daily_rain_rate[i]) for i in daily_rain_rate] 
map_dots((np.nanmax(prcp_data['AWAP_ann'], 0)), BARRA_lats, BARRA_lons, levels = levels['day'], title = "AWAP and AWS Rx1day", cmap_label = "precipitation (mm)") 
#plt.savefig('Documents
map_dots((np.nanmax(prcp_data['BARRA_ann'], 0)), BARRA_lats, BARRA_lons, levels = levels['day'], title = "BARRA and AWS Rx1day", cmap_label = "precipitation (mm)") 
#plt.savefig('Documents

aws_color = daily_df['rx1day']
map_dots((np.nanmax(prcp_data['AWAP_ann'], 0)), BARRA_lats, BARRA_lons, levels = levels['day'], title = "AWAP and AWS Rx1day", cmap_label = "precipitation (mm)") 
#plt.savefig('Documents
map_dots((np.nanmax(prcp_data['BARRA_ann'], 0)), BARRA_lats, BARRA_lons, levels = levels['day'], title = "BARRA and AWS Rx1day", cmap_label = "precipitation (mm)") 
#plt.savefig('Documents


