

# Get data info from txt file. theres a bit of a weird for morewell. It's too long
AWS_info = pd.read_fwf("/home/563/gt3409/Documents/AWS_data/AWS_sites.txt", names = ['ID', 'name',  "name2", "lat", "lon", "start_month", "start_year", "end_month", "end_year", "years", "complete","AWS","district"])

# station_ids = [str(ID) for ID in AWS_info['ID']]

# Long station names 
station_names = [name.strip().title() for name in (AWS_info['name']+' '+ AWS_info.fillna('')['name2'])]

# Short station names
short_station_names = ["Mildura",
 "Horsham",
 "Bendigo",
 "Wangaratta",
 "Falls Creek",
 "Orbost",
 "Morwell",
 "Melbourne",
 "Wallan",
 "Ballarat",
 "Cape Otway",
 "Hamilton"]

# List of the stations' paired lat lon coordinates 
station_locations = list(zip(list(AWS_info['lat']), list(AWS_info['lon'])))

# Read in the station data from csv file
def station_df_from_csv(filename):
 """This function take the filename of a csv file containing 
station data and returns a dataframe with four fields:
 "YYYY-MM-DD", "prcp", "accum_period", and "Quality". """
 # name of fields in csv file
 col_names = [
  "YYYY",
  "MM",
  "DD",
  "prcp",
  "accum_period",
  "Quality"]
 # read in the csv file
 station_df = pd.read_csv(
  filename,
  usecols = [2,3,4,5,6,7],
  skiprows = [0],
  parse_dates = [[0,1,2]],
  names = col_names,
  date_parser = pd.to_datetime)
 return station_df

# filename
# filename = f"/home/563/gt3409/Documents/AWS_data/IDCJAC0009_{ID}_1800_Data.csv"

# plot completeness
def completeness_plot(dataframe, station_name):
 """This function takes a dataframe of a station and the station name and show a plot of the proportion of complete records for each year in the record for that station"""
 # Get start and end year. the range between these two will be the x axis of the graph
 start_year = dataframe["YYYY_MM_DD"].iloc[0].year
 end_year = dataframe["YYYY_MM_DD"].iloc[-1].year
 # for each year, find the proportion of not NaNs of the number of years
 # find number of days in year
 day_tally = {}
 for day in dataframe["YYYY_MM_DD"]:
     day_tally[day.year] = day_tally.get(day.year, 0) + 1
 # find prcp data is NaN
 nan_tally = {}
 for record in dataframe.itertuples():
     if np.isnan(record[2]):    # if the rainfall amount is NaN then
         nan_tally[record[1].year] = nan_tally.get(record[1].year, 0) + 1
 # Calculate completeness
 completeness = []
 for year in range(start_year, end_year + 1):
     try:
         completeness.append((day_tally[year] - nan_tally[year]) / day_tally[year])
     except KeyError:
         completeness.append(1)
 # plot barchart
 plt.bar(np.arange(start_year, end_year + 1), completeness, width = 1., align = "edge")
 plt.xlim(1990, 2016)
 plt.ylim(0, 1)
 plt.xlabel("Year")
 plt.ylabel("Proportion of records")
 plt.title(f"{station_name} Completeness")
 fig = plt.gcf()
# fig.set_size_inches(10, 2)
 #plt.savefig(f"{station_name}_Completeness.png")
 return

def Rnnmm(data, threshold = 0):
    """Annual count of days when PRCP > threshold.
    This function takes a timeseries of daily data, and a threshold number.
    the function returns the annual average of days with rainfall totals above the threshold."""
    count = 0
    years = round(len(data)/365.25, 1) #number of years averaging over
    for amount in data:
        if amount >= threshold:
            count += 1
    return round(count/years)

def RqqpTOT(data, climate_data, q):
    """This function takes a short period of timeseries data, a reference period of cliamte data and a percentile threshold (q).
    The function calculates the total annual precipitation from days when daily rainfall exceeds the percentile threshold defined by the climate data.
    The function returns the total annual value.
"""
    threshold = np.nanpercentile(climate_data, q=q)
    years = len(data)/365.25 #number of years averaging over
    data = np.array(data)
    RqqpTOT = np.nansum(data[data >= threshold])/years 
    RqqpTOT = round(RqqpTOT,1)
    return RqqpTOT

def PRCPTOT(data):
    """This function takes a timeseries and returns the annual total precipitation from wet days, where wet days are defined as day where at least 1.0mm rainfall is recorded."""
    years = len(data)/365.25 # find the length of the data in years 
    prcptot = sum(data[data >= 1.])/years  # sum the total of daily prcp of days not less than 1.0mm then divide by number of years to get the annual mean prcptot. 
    prcptot = round(prcptot, 1)
    return prcptot

def SDII(data):
    """This function calculates the simple precipitation intensity index (SDII), the average precipitation on wet days.  This function takes a timeseries of daily precipitation totals, and then returns a value of SDII"""
    wet_days = len(data[data >= 1.])
    if wet_days ==0:
        print("No wet days")
        return np.nan
    tot_prcp = sum(data[data >= 1.])
    SDII = round(tot_prcp/wet_days, 1)
    return SDII

def CWD(data):
    """Maximum length of wet spell, ie the maximum number of consecutive days with RR >= 1.0mm"""
    lengths = set()
    spell_length = 0
    for prcp in data:
        if prcp >= 1.0:
            spell_length += 1
        else:
            lengths.add(spell_length)
            spell_length = 0
    return max(lengths)

def CDD(data):
    """Maximum length of dry spell, ie the maximum number of consecutive days with RR < 1.0mm"""
    lengths = set()
    spell_length = 0
    for prcp in data:
        if prcp < 1.0:
            spell_length += 1
        else:
            lengths.add(spell_length)
            spell_length = 0
    return max(lengths)

def Rx5day(data):
    """Monthly maximum consecutive 5-day precipitation"""
    Rx5day = 0
    for i in range(5, len(data)+1):
        tot_5day = sum(data[i-5:i])
        if tot_5day > Rx5day:
            Rx5day = tot_5day
    return round(Rx5day,1)





