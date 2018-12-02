"""The purpose of this script is to read in the csv files
 of the list of stations and to make plots of the data"""

# Import packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Get data info from txt file. theres a bit of a weird for morewell. its too long
AWS_info = pd.read_fwf("/home/563/gt3409/Documents/AWS_data/AWS_sites.txt", names = ['ID', 'name',  "name2", "lat", "lon", "start_month", "start_year", "end_month", "end_year", "years", "complete","AWS","district"])


# List of stations' IDs
station_ids = [str(ID) for ID in AWS_info['ID']]

#station_ids = [ '76031', '79100', '81123', '82138', '83084', '84145', '85280', '86282', '88162', '89002', '90015', '90173']

# List of the stations' names
station_names = [name.strip().title() for name in (AWS_info['name']+' '+ AWS_info.fillna('')['name2'])]

#station_names = [ "Mildura Airport", "Horsham Aerodrome", "Bendigo Airport", "Wangaratta Aero", "Falls Creek", "Orbost", "Morwell (Latrobe Valley Airport)", "Melbourne Airport", "Wallan (Kilmore Gap)", "Ballarat Aerodrome", "Cape Otway Lighthouse", "Hamilton Airport"]

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

# List of the stations' coordinates 
station_locations = list(zip( list(AWS_info['lat']), list(AWS_info['lon'])))

#station_locations = [
# (-34.2358, 142.0867),
# (-36.6697, 142.1731),
# (-36.7395, 144.3266),
# (-36.4206, 146.3056),
# (-36.8708, 147.2755),
# (-37.6922, 148.4667),
# (-38.2094, 146.4747),
# (-37.6655, 144.8321),
# (-37.3807, 144.9654),
# (-37.5127, 143.7911),
# (-38.8556, 143.5128),
# (-37.6486, 142.0636)]

# Dictionary of {ids: (names, coords)}
station_info = {}
for i in range(len(station_ids)):
    station_info[station_ids[i]] = [station_names[i], station_locations[i]]

# Read in the data
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
  names = col_names)
 return station_df

# Define the full filename
file_location = "/home/563/gt3409/Documents/AWS_data/"
station_dataframes = {}
for ID in station_ids:
    filename = f"IDCJAC0009_{ID}_1800_Data.csv"
    station_dataframes[ID] = station_df_from_csv(filename = f"{file_location}{filename}")

# rough time series plot
#station_df.plot(x="YYYY_MM_DD", y = "prcp")

# rough histogram plot
#station_df.plot(x="YYYY_MM_DD", y = "prcp", kind = "hist", bins=120, xlim = [0, 30], ylim = [0, 4000])


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

# plot a figure with all the completeness barchart as subplots for the total BARRA 1990-2006 period
## at the moment the plots are ok, but all the labelling is the worst
fig = plt.figure()
counter = 0
for ID in station_ids:
    counter += 1
    plt.subplot(len(station_ids),1, counter)
    completeness_plot(dataframe = station_dataframes[ID], station_name = station_info[ID][0])
#plt.savefig(f"Completeness_plots_{counter}.png")


# write dictionary to store timesseries of aws data 
BARRA_period_data = {}
for ID in station_ids:
   # Plot timeseries for BARRA period
   ID_df = station_dataframes[ID] # set alias for convience of writing

   start_date = pd.datetime(2010, 1, 1) # set the start date
   end_date = pd.datetime(2016, 1, 1) # set the end date

   start_index = ID_df.index[ID_df["YYYY_MM_DD"] == start_date].tolist()[0]
   end_index = ID_df.index[ID_df["YYYY_MM_DD"] == end_date].tolist()[0]
   # Select  the data for tha BARRA time period
   BARRA_period_data[ID] = ID_df[start_index : end_index]


# Some quick stats for the few years
def quick_counts(data, threshold):
    count = 0
    years = round(len(data)/365.25, 1) #number of years averaging over
    for amount in data:
        if amount >= threshold:
            count += 1
    return round(count/years)

def prcptot(data, threshold = 1.0):
    total = 0
    for amount in data:
        if amount >= threshold:
            total += amount 
    years = round(len(data)/365.25, 1)
    annual_total = round(total/years, 1)
    return annual_total

quick_indices = {}
#quick_indices['Station_ID'] = ('R01mm', 'R10mm', 'R20mm', 'R95p', 'R99p', 'R95pTOT', 'R99pTOT', 'R95pPROP', 'R99pPROP', 'PRCPTOT')
for ID in station_ids:
    data = BARRA_period_data[ID]["prcp"]
    R01mm = quick_counts(data, 1)
    R10mm = quick_counts(data, 10)
    R20mm = quick_counts(data, 20)
    R95p  = round(np.nanpercentile(data, 95), 1)
    R99p  = round(np.nanpercentile(data, 99), 1)
    PRCPTOT = prcptot(data)
    R95pTOT = prcptot(data, R95p)
    R99pTOT = prcptot(data, R99p)
    R95pPROP= round(R95pTOT/PRCPTOT, 2)
    R99pPROP= round(R99pTOT/PRCPTOT, 2)
    quick_indices[ID] = (R01mm, R10mm, R20mm, R95p, R99p, R95pTOT, R99pTOT, R95pPROP, R99pPROP, PRCPTOT)

# write the dictionary to a csv file
with open('Documents/quick_indices.csv', 'w') as f:
    [f.write('{0},{1}\n'.format(key, value)) for key, value in quick_indices.items()]

columns = ('R01mm', 'R10mm', 'R20mm', 'R95p', 'R99p', 'R95pTOT', 'R99pTOT', 'R95pPROP', 'R99pPROP', 'PRCPTOT')
quick_indices_df = pd.DataFrame(list(quick_indices.values()), index = list(quick_indices.keys()), columns = columns)



#plot a barchart of the proportion of prcp for the 99th and 95th percentiles
r=np.arange(len(station_ids))
left = 0
colors = ['red', 'orange', 'skyblue']
fields = ['R95pTOT', 'R99pTOT','PRCPTOT']
qi_df = quick_indices_df
data = [qi_df['R99pTOT']/qi_df['PRCPTOT'],
       (qi_df['R95pTOT']-qi_df['R99pTOT'])/qi_df['PRCPTOT'],
       1-qi_df['R95pTOT']/qi_df['PRCPTOT']]
data_names = ["99-100","95-99","0-95"]

plt.figure(figsize=(6,4))       
left = 0
for i in range(len(data)):
   plt.barh(r, data[i], left=left, color = colors[i])
   left += data[i]
plt.title("Proportion of Total Precipitation from Extreme Days\nJan 2010 to Dec 2015")
plt.xticks(np.arange(0.,1.1, 0.2))
plt.xlabel("Proportion of total rainfall")
plt.xlim(0,1)
plt.yticks(np.arange(len(station_ids)), short_station_names, fontsize = 8)
plt.ylabel("Stations")
plt.legend(labels = data_names)
plt.tight_layout(pad = 1)
plt.savefig(f"/home/563/gt3409/Documents/AWS_extreme_props.png")
plt.show()

# Plot 6*2 timeseries plot of prcp for the 12 chosen sites. share the axes. title each location
fig, axarr = plt.subplots(nrows = 6, ncols = 2, sharex = True, sharey = True, figsize = (12, 16))
fig.suptitle("AWS Precipitation timeseries for 2010-2016", fontsize = 20, position = (0.5, 1))
fig.add_subplot(111, frameon = False) #define the overlay
i = 0
for row in axarr:
    for col in row:
        ID = station_ids[i]
        data = BARRA_period_data[ID]["prcp"]
        date_series = BARRA_period_data[ID]["YYYY_MM_DD"]
        line_20  = np.array([20 for i in range(len(date_series))])
        line_99p = np.array([quick_indices[ID][4] for i in range(len(date_series))])
        handle1, = col.plot(date_series, data, label = "prcp")          
        handle2, = col.plot(date_series, line_20, 'r', label = "20 mm")
        handle3, = col.plot(date_series, line_99p, 'r:', label = "99p")        
        col.set_title(f"{station_info[ID][0]} ID: {ID}", fontsize = 14, position = (.5,.8))
        col.set_ylim([0, 120])
        col.set_xlim([start_date, end_date])
        i += 1
#no labels for overlaying 'subplot'
plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off') 
plt.xlabel("Year", fontsize = 16) #common label
plt.ylabel("Daily Precipitation (mm)", fontsize = 16) # common label
plt.legend(handles = [handle1, handle2, handle3], loc = 'lower center', ncol = 3, bbox_to_anchor = (0.5, -0.07) ) #single legend
plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False) #hide inner axes labels
plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False) #hide inner axes labels
#plt.savefig(f"/home/563/gt3409/Documents/AWS_prcp_timeseries_lines.png") #save the fig











