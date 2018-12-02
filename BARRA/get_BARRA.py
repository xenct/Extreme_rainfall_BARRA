# Get BARRA daily data

start_date = date(2010,1,4) # first valid date
end_date = date(2016,1,1) # last available date for daily rainfall to 9am AEST

BARRA_data = [] # Start with an empty list for the BARRA data
_, BARRA_lats, BARRA_lons = load_2D_netCDF(f"/g/data3/w42/gt3409/BARRA_R/daily_prcp/{start_date.year}/{start_date.month:02d}/accum_prcp-BARRA_R-v1-daily-{start_date.strftime('%Y%m%d')}.nc", 'prcp') # load the BARRA lats and lons once only
for DATE in date_range(start_date, end_date): # for all date
    print(DATE) # to keep track of progress
    filename = f"/g/data3/w42/gt3409/BARRA_R/daily_prcp/{DATE.year}/{DATE.month:02d}/accum_prcp-BARRA_R-v1-daily-{DATE.strftime('%Y%m%d')}.nc"
    data, _, _ = load_2D_netCDF(filename, 'prcp')
    BARRA_data.append(data) # add day to list
BARRA_data = np.array(BARRA_data) # convert list to numpy array


# Total six year precipitation totals
BARRA_TOT = np.nansum(BARRA_data, axis=0)
BARRA_99p = np.nanpercentile(BARRA_data, axis=0, q=99)
BARRA_95p = np.nanpercentile(BARRA_data, axis=0, q=95)

data = BARRA_data[0:365]
data_climate = BARRA_data

def counts_above_percentile(data_climate, data, percentile):
    """This function takes a long record of data (data_cliamte) and a shorter period of data, calculates the percentile threshold for each gridbox based on data_climate, and then counts the number of times the percentil is exceeded. Return an array of counts"""
    data_percentile = np.nanpercentile(data_climate, axis=0, q=percentile) #calculate the value of the qth percentile for each grid box in the array and save this as data_percentile
    counts_array = np.zeros(data[0].shape) #start counts at zero
    for day in range(len(data)):
        counts_array += np.greater_equal(data[day], BARRA_95p)
    return counts_array

def tot_from_percentile(data_climate, data, percentile):
    """This function takes a long record of data (data_cliamte) and a shorter period of data, calculates the percentile threshold for each gridbox based on data_climate, and then ..."""
    data_percentile = np.nanpercentile(data_climate, axis=0, q=percentile) #calculate the value of the qth percentile for each grid box in the array and save this as data_percentile
    tot_array = np.zeros(data[0].shape) #start counts at zero
    for day in range(len(data)):
        tot_array += (data[day]*[np.greater_equal(data[day], data_percentile)])[0]
    return tot_array

def prop_from_percentile(data_climate, data, percentile):
    """This function takes a long record of data (data_cliamte) and a shorter period of data, calculates the percentile threshold for each gridbox based on data_climate, and then ...."""
    data_percentile = np.nanpercentile(data_climate, axis=0, q=percentile) #calculate the value of the qth percentile for each grid box in the array and save this as data_percentile
    prop_array = np.zeros(data[0].shape) #start counts at zero
    for day in range(len(data)):
        prop_array += (data[day]*[np.greater_equal(data[day], data_percentile)])[0]
    prop_array = prop_array/np.sum(data, axis=0)
    return prop_array

prop_array = prop_from_percentile(BARRA_data, BARRA_data, 95)
map_BARRA(prop_array, BARRA_lats, BARRA_lons, levels = np.arange(0,1.1,0.1), colormap = plt.cm.get_cmap('RdBu_r', 10), cmap_label = "Proportion of total rainfall from {percentile}th percentile")
plt.show()





# map 6 year annual mean:
map_BARRA(np.nansum(BARRA_data, axis=0)/6, BARRA_lats, BARRA_lons, levels= levels['year'], title = "BARRA annual mean rainfall\n2010-2015") 
plt.savefig("/home/563/gt3409/Documents/images/BARRA_annual_mean_2010-2015.png")
plt.show()

# map of 95th percentiles for 2010-2015
map_BARRA(np.nanpercentile(BARRA_data, axis=0, q=95), BARRA_lats, BARRA_lons, levels = levels['day'], title = "BARRA 95th percentile value\n2010-2015") 
plt.savefig("/home/563/gt3409/Documents/images/BARRA_95p_2010-2015.png")
plt.show()
