

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

# this shows the stations overlapped
#remarkedbly good
for station in list(hourly_rain_rate.keys())[:]:
    plt.plot(BARRA_timeseries[station])
    plt.plot(hourly_rain_rate[station])
    plt.title(f'{vic_aws_info["name"][station]}')
    plt.savefig(f"Documents/images/hourly_timeseries_AWS_BARRA_{station}.png")
    plt.close()

plt.show()

# Calculate the monthly max value
BARRA_ts_month_max = BARRA_timeseries.resample('M').max()
AWS_month_max = hourly_rain_rate.resample("M").max()

# for each month check the timing of the max
plt.figure()
plt.subplot(211)   
plt.plot(BARRA_ts_month_max, color = 'r', alpha = 0.2)
plt.title("BARRA monthly max")  
plt.xlabel("date")
plt.ylabel("Max 1 hour precipitation (mm)")
plt.xlim((datetime(2010,1,1), datetime(2016,1,1)))  
plt.ylim((0,130))

plt.subplot(212)
plt.plot(AWS_month_max, color = 'k', alpha=0.2)
plt.title("AWS monthly max") 
plt.xlabel("date")
plt.ylabel("Max 1 hour precipitation (mm)")
plt.xlim((datetime(2010,1,1), datetime(2016,1,1)))  
plt.ylim((0,130))
plt.tight_layout()
#plt.savefig("Documents/images/monthly_1hour_max_BARRA_AWS.png")

hour_max_by_month = {}
# value of monthly max from AWS        
hour_max_by_month['AWS_value'] = hourly_rain_rate.groupby(pd.Grouper(freq = "M")).max()
# value of monthly max from BARRA
hour_max_by_month['BARRA_value'] = BARRA_timeseries.groupby(pd.Grouper(freq = "M")).max()
# time of monthly max from AWS
hour_max_by_month['AWS_time'] = hourly_rain_rate.groupby(pd.Grouper(freq = "M")).idxmax() 
# time of monthly max from BARRA
hour_max_by_month['BARRA_time'] = BARRA_timeseries.groupby(pd.Grouper(freq = "M")).idxmax() 

# difference?
# A negative difference means that the precipitation is early in BARRA compared to obs
timing_diff = (hour_max_by_month['BARRA_time'] - hour_max_by_month['AWS_time'])


hour_diff = {}
for station in timing_diff.keys():
    hour_diff[station]=[]
    # calculate the timing difference in hours from BARRA relative to AWS
    for i in timing_diff.index:
        try:
            hour_diff[station].append(int(timing_diff[station][i].total_seconds()/3600)) 
        except:
            hour_diff[station].append(np.nan)

hour_diff = pd.DataFrame(hour_diff, index = timing_diff.index)


i = 0
plt.figure(figsize=(12,6))
for station in hour_diff.keys():
    x = i*np.ones(len(hour_diff[station]))
    plt.scatter(x = x, y = hour_diff[station], alpha = 0.2, color = 'k')
    i += 1
plt.ylim(-25,25)
plt.yticks(np.arange(-24,25,6))
plt.grid(axis = 'y')
plt.ylabel("<- too early  (hours)  too late ->")
plt.title("BARRA max preciptation timing lag from AWS")
plt.axhline(0, color = 'r', lw = 0.6)
plt.xticks(np.arange(0,len(hour_diff.keys())), hour_diff.keys(), rotation = 'vertical')
plt.xlabel("station")
plt.tight_layout()
plt.show()



plt.figure(figsize=(12,6))
for station in hour_diff.keys():
    plt.scatter(x = hour_diff.index, y = hour_diff[station], alpha = 0.2, color = 'k')
plt.ylim(-25,25)
plt.yticks(np.arange(-24,25,6))
plt.grid(axis = 'y')
plt.ylabel("<- too early  (hours)  too late ->")
plt.title("BARRA max preciptation timing lag from AWS")
#plt.axhline(0, color = 'r', lw = 0.6)
plt.xticks(rotation = 'vertical')
plt.xlabel("month")
plt.tight_layout()
plt.show()


hour_diff_within_day = hour_diff[hour_diff<25][hour_diff>-25].values.reshape(hour_diff.size)
# remove any nans
hour_diff_within_day =[t for t in hour_diff_within_day if t==t]

plt.figure(figsize=(5,4))
plt.hist(hour_diff_within_day, bins=np.arange(-24.5, 26), density = True)
plt.xticks(np.arange(-24, 25, 3), [-24,'',-18,'',-12,'',-6,'',0,'',6,'',12,'',18,'',24])
plt.xlim(-24, 24)
plt.xlabel("Lag of BARRA behind AWS (hours)")
plt.ylabel("Probability")
plt.title("Timing of monthly maximum 1 hour precipitation\nVictoria 2010-2015")
plt.grid(axis = 'x')
plt.axvline(0, color = 'k', linestyle = '--')
plt.tight_layout()
plt.savefig("Documents/images/BARRA_AWS_hour_max_timing_comparison.png")
plt.show()


plt.hist(hour_mag_diff_within_day, bins=np.arange(-0.5,25))
plt.xticks(np.arange(-0, 25, 3), [0,'',6,'',12,'',18,'',24])
plt.xlabel("Timing difference (hours)")
plt.ylabel("Frequency")
plt.title("Absolute timing difference of monthly maximum 1 hour precipitation\nBARRA and AWS in Victoria 2010-2015")
plt.xlim(-0.5, 24)
plt.grid(axis = 'x',lw = 0.5)
plt.tight_layout()
# plt.axvline(0, color = 'k')
# plt.savefig("Documents/images/BARRA_AWS_hour_max_abs_timing_comparison.png")
plt.show()




