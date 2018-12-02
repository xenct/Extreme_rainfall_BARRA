
# Get data info from txt file. To add more sites to analysis. add the info here and load the data into the AWS_data folder
AWS_info = pd.read_fwf("/home/563/gt3409/Documents/AWS_data/AWS_sites.txt", names = ['ID', 'name',  "name2", "lat", "lon", "start_month", "start_year", "end_month", "end_year", "years", "complete","AWS","district"])
AWS_info['ID'] = [str(ID) for ID in AWS_info['ID']] # change IDs from int to str

# load the data for each station
start_date = datetime(2010,1,1)
end_date = datetime(2015,12,31)

station_data = {}
for ID in AWS_info['ID']:
    filename = f"/home/563/gt3409/Documents/AWS_data/IDCJAC0009_{ID}_1800_Data.csv"
    data = station_df_from_csv(filename)
    data = data[data["YYYY_MM_DD"] >= start_date] # only keep data after the start date
    data = data[data["YYYY_MM_DD"] <= end_date] # only keep data before the end date
    station_data[str(ID)] = data # save the  data to the dictionary of station data

# List of the stations' coordinates 
#station_locations = list(zip( list(AWS_info['lat']), list(AWS_info['lon'])))
#BARRA_data = {}
#for i in range(len(AWS_info)): # this loop is very slow because for every loop it must open a barra netCDF
#    print(f"Now calculating BARRA timeseries for station {AWS_info['ID'][i]}")
#    BARRA_data[AWS_info['ID'][i]] = BARRA_daily_ts(start_date, end_date, station_locations[i], n=0) 

# Write the barra timeseries data to a csv so we don't have to do the very slow loop again
# This file has a few problems, the dates start at 2010-01-01 but the data is from a few days later (3 I think). All the data is surrounded by []; I don't know why.
#with open('Documents/BARRA_data_ts_2010-2015.csv', 'w') as f:
#    writer = csv.writer(f)                                             
#    writer.writerow(["Date", '76031', '79100', '81123', '82138', '83084', '84145', '85280', '86282', '88162', '89002', '90015', '90173'])     
#    writer.writerows(zip([DATE.strftime("%Y_%m_%d") for DATE in BARRA_data['90015'][0]],BARRA_data['76031'][1],BARRA_data['79100'][1],BARRA_data['81123'][1],BARRA_data['82138'][1],BARRA_data['83084'][1],BARRA_data['84145'][1],BARRA_data['85280'][1],BARRA_data['86282'][1],BARRA_data['88162'][1],BARRA_data['89002'][1],BARRA_data['90015'][1],BARRA_data['90173'][1]))  

# Retrieve the data from the csv
df = pd.read_csv('/home/563/gt3409/Documents/BARRA_data_ts_2010-2015.csv', header = 0)

station_ids = [str(ID) for ID in AWS_info['ID']]

BARRA_stats = {}
# ID: [[min, q1, median, q2, max, p95, p99], Rx5day, SDII, R10mm, R20mm, R95pTOT, R99pTOT, PRCPTOT, CWD, CDD]
for ID in station_ids:
    data = df[ID]
    BARRA_stats[ID] = [round(x, 1) for x in np.nanpercentile(data, q= [0, 25, 50, 75, 100, 95, 99])] + [Rx5day(data), SDII(data), Rnnmm(data, 10), Rnnmm(data, 20), RqqpTOT(data, data, q = 95), RqqpTOT(data, data, q = 99), PRCPTOT(data), CWD(data), CDD(data)]


AWAP_data, AWAP_lats, AWAP_lons, AWAP_times = get_AWAP()
AWAP_data[AWAP_data > 9999] = np.nan

AWAP_sites = {}
for i in range(len(station_ids)):
    if station_ids[i] == "90015":
        _, AWAP_sites[station_ids[i]] = AWAP_daily_square(AWAP_data, AWAP_lats, AWAP_lons, AWAP_times, AWAP_times[0], AWAP_times[-1], station_coords= (-38.5, 143.5), n = 0) # Cape Otway falls off the edge of the AWAP value, this pushes it back to the land
        continue
    _, AWAP_sites[station_ids[i]] = AWAP_daily_square(AWAP_data, AWAP_lats, AWAP_lons, AWAP_times, AWAP_times[0], AWAP_times[-1], station_coords= station_locations[i], n = 0)

AWAP_stats = {}
for ID in station_ids:
    data = np.array(AWAP_sites[ID])
    AWAP_stats[ID] = [round(x, 1) for x in np.nanpercentile(data, q= [0, 25, 50, 75, 100, 95, 99])] + [Rx5day(data), SDII(data), Rnnmm(data, 10), Rnnmm(data, 20), RqqpTOT(data, data, q = 95), RqqpTOT(data, data, q = 99), PRCPTOT(data), CWD(data), CDD(data)]

AWS_stats = {}
for ID in station_ids:
    data = station_data[ID]['prcp']
    AWS_stats[ID] = [round(x, 1) for x in np.nanpercentile(data, q= [0, 25, 50, 75, 100, 95, 99])] + [Rx5day(data), SDII(data), Rnnmm(data, 10), Rnnmm(data, 20), RqqpTOT(data, data, q = 95), RqqpTOT(data, data, q = 99), PRCPTOT(data), CWD(data), CDD(data)]

#Make each dictionary into a pandas dataframe
AWAP_stats_df = pd.DataFrame.from_dict(AWAP_stats, orient='index')
AWS_stats_df = pd.DataFrame.from_dict(AWS_stats, orient='index')
BARRA_stats_df = pd.DataFrame.from_dict(BARRA_stats, orient='index')
# name all the columns by the statistic
column_names = ['min', 'q1', 'median', 'q3', 'max', '95p', '99p', 'Rx5day', "SDII", 'R10mm', 'R20mm', 'R95pTOT', 'R99pTOT', 'PRCPTOT', 'CWD', 'CDD'] 
for df in [AWAP_stats_df, AWS_stats_df, BARRA_stats_df]:
    df.columns = column_names

# For each of the datasets, plot min, q1, q2, q3, max, p95, p99
for i in range(7):
    plt.scatter(station_ids, [site[i] for site in AWAP_stats.values()], marker = '*', color = 'r')    
    plt.scatter(station_ids, [site[i] for site in AWS_stats.values()], marker = '_', color = 'k')
    plt.scatter(station_ids, [site[i] for site in BARRA_station.values()], marker = '.', facecolors = 'none', color = 'gray')
    plt.xticks(rotation = -90)
    plt.title("BARRA gridbox (.) vs AWS data (_) vs AWAP (*)\nmin, q1, median, q3, 95p, 99p, max")
    plt.tight_layout()
#    plt.savefig("/home/563/gt3409/Documents/images/AWS_BARRA_AWAP_quantiles.png")
plt.show()


# Compare the CDD and CWD for the datasets
plt.scatter(station_ids, AWAP_stats_df['CDD'], marker = '*', color = 'r') 
plt.scatter(station_ids, AWS_stats_df['CDD'], marker = '_', color = 'k')
plt.scatter(station_ids, BARRA_stats_df['CDD'], marker = '.', facecolors = 'none', color = 'gray')
plt.legend(labels = ['AWAP', "AWS", "BARRA"])
plt.title("Max Dry Spell")
plt.yticks(np.arange(0, 70, 5))
plt.xticks(rotation = -90)
plt.show()

plt.scatter(station_ids, AWAP_stats_df['CWD'], marker = '*', color = 'r')	 
plt.scatter(station_ids, AWS_stats_df['CWD'], marker = '_', color = 'k')
plt.scatter(station_ids, BARRA_stats_df['CWD'], marker = '.', facecolors = 'none', color = 'gray')
plt.legend(labels = ['AWAP', "AWS", "BARRA"])
plt.title("Max Wet Spell")
plt.yticks(np.arange(0, 20, 2))
plt.xticks(rotation = -90)
plt.show()

# Compare PRCPTOT
plt.scatter(station_ids, AWAP_stats_df['PRCPTOT'], marker = '*', color = 'r') 
plt.scatter(station_ids, AWS_stats_df['PRCPTOT'], marker = '_', color = 'k')
plt.scatter(station_ids, BARRA_stats_df['PRCPTOT'], marker = '.', facecolors = 'none', color = 'gray')
plt.legend(labels = ['AWAP', "AWS", "BARRA"])
plt.xticks(rotation = -90)
plt.title("PRCPTOT")
plt.show()

#compare all (note that AWAP data is from 2010-2014, but BARRA and AWS data is from 2010-2016)

for stat in column_names:
    plt.scatter(station_ids, AWAP_stats_df[stat], marker = '*', color = 'r') 
    plt.scatter(station_ids, AWS_stats_df[stat], marker = '_', color = 'k')
    plt.scatter(station_ids, BARRA_stats_df[stat], marker = '.', facecolors = 'none', color = 'gray')
    plt.legend(labels = ['AWAP', "AWS", "BARRA"])
    plt.xticks(rotation = -90)
    plt.title(stat)
    plt.savefig(f"/home/563/gt3409/Documents/images/{stat}_comparison.png")
    plt.show()
