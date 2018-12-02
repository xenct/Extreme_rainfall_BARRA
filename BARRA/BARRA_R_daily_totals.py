from netCDF4 import Dataset
import numpy as np
from datetime import timedelta, date, datetime
import matplotlib.pyplot as plt

# Open the data
# from load_netCDFs.py
def load_3D_netCDF(filename, var_name = "prcp", lat_name = "lats", lon_name = "lons", time_name = "times"):
    """This function loads a three dimensional netCDF.
    Give filename as a string.
    Give name of the measured variable.
    Give the names of the two spatial coordinates.
    Give the name of the time dimension.
    The function returns the variable, the two spatial dimensions, and the times."""
    data = Dataset(filename, 'r')
    var = data[var_name][:]
    lats = data[lat_name][:]
    lons = data[lon_name][:]
    times = data[time_name][:]
    data.close()
    return var, lats, lons, times

# find the coordinate for the station location
# from squares.py
def get_nearest_coord(goal, lats, lons):
    """This function takes a tuple of lat and lon of the goal location, and the lists of latitudes and longitudes and then returns the lat/lon indices of the nearest box and the coordinates associated with that location both as tuples."""
    # Calculate the closest lat and lon with data to the goal location
    # calculate the distance of each latitude from the goal latitude.
    d_lat = abs(lats - goal[0])
    # Find the index of the latitude with the smallest absolute distance from  the goal latitude.
    lat_ix = np.where((d_lat - min(d_lat)) == 0)[0][0] 
    # calculate the distance of each longitude from the goal longitude.
    d_lon = abs(lons - goal[1])
    # Find the index of the longitude with the smallest absolute distance from  the goal longitude.
    lon_ix = np.where((d_lon - min(d_lon)) == 0)[0][0]
    # store the indices in a tuple called "indices"
    indices = (lat_ix, lon_ix)
    # Store the lat and lon values of this nearest grid box as "coords"
    coords = (lats[lat_ix], lons[lon_ix])
    return indices, coords

# get the values of the closest (2n+1)^2 grids
# from squares.py
def values_of_nsquare(data, centre_indices, n = 1):
    """This function gets the values of the closest (2n+1)^2 grids from a tuple pair of indices relating to coordinates of lat and lon in 2D data.
The default of n = 1 describes a grid of 9. 
It returns a list of the values in the square, and the mean value."""
    # Calculate the indices of the closest (2n+1)^2 squares
    # this code should work on edge points but print a Caution message when this occurs
    lat_ix, lon_ix = centre_indices
    n2_square_coords = []
    for i in range(-n, n + 1):
        if (lon_ix + i >= 0) & (lon_ix + i < data.shape[1]): # data.shape[1] ~ len(lons)
            for j in range(-n, n + 1):
                if (lat_ix + j >= 0) & (lat_ix + j < data.shape[0]): # data.shape[0] ~ len(lats)
                    n2_square_coords.append([lat_ix + j, lon_ix + i])
                else:
                    print("Caution. Edge of lats reached.")
        else:
            print("Caution. Edge of lons reached.")
    # for each of the squares coordinates, get the prcp values and find the average
    values = []
    for lat, lon in n2_square_coords:
        values.append(data[lat, lon])
    return values

def nsquare_day_prcp(data, centre_indices, n = 1):
    """This function calculates the days rainfall, averages over the (2n+1)^2 grid boxes surrounding the central grid box.
It takes the 3D data, the 2-tuple of indices defining the central grid and an integer n describing the size of the averaging area. 
Returns one prcp value representing the mm of prcp in the square for 24 hours"""
    nsquare_means = [] # the 24 mean hourly rainfalls over (2n+1)^2 grids
    for time in range(24):
        values = values_of_nsquare(data[time], centre_indices, n)
        nsquare_means.append(np.mean(values))
    nsquare_day_prcp = np.sum(nsquare_means) # The daily mean value is the sum of the 24 mean values
    return nsquare_day_prcp

# from datetime import timedelta, date, datetime
def date_range(start_date, end_date):
    """This function takes a start date and an end date as datetime date objects.
It returns a list of dates for each date in order starting at the first date and ending with the last date"""
    return [start_date + timedelta(x) for x in range((end_date - start_date).days + 1)]

def BARRA_daily_square(start_date, end_date, station_coords, n = 1):
    # Specify the date range
    dates = date_range(start_date, end_date)
    day_prcp = []
    for date in dates: # for each date
        filename = f"/g/data3/w42/gt3409/accum_prcp-BARRA_R-v1-{date.strftime('%Y%m%d')}.nc" # get the unique filename 
        prcp, lats, lons, _ = load_3D_netCDF(filename) # load all the data for that day
        centre_indices, _ = nearest_coord(station_coords, lats, lons) # Get the indices of the nearest grid box
        day_prcp.append(nsquare_day_prcp(prcp, centre_indices, n)) # Write a list of daily prcp totals as day_prcp
    return dates, day_prcp

# Specify the date range
start_date = date(2012, 1, 1)
end_date = date(2012, 2, 1)
# Specify the relevant grid boxes
station_coords = (-37.69, 144.84) # this is melbourne airport
# Specify the variable
var_name = "precipitation_amount"
#Calculate the timeseries
dates, BARRA_single = BARRA_daily_square(start_date, end_date, station_coords, n = 0)
_, BARRA_nine       = BARRA_daily_square(start_date, end_date, station_coords, n = 1)
_, BARRA_25         = BARRA_daily_square(start_date, end_date, station_coords, n = 2)
_, BARRA_121        = BARRA_daily_square(start_date, end_date, station_coords, n = 5) #Similar (bit less) coverage to AWAP_nine

fig = plt.figure()
ax1 = fig.add_subplot(111)
plt.grid(axis = 'y')
ax1.plot(dates, BARRA_single, label = "BARRA single")
ax1.plot(dates, BARRA_nine, label = "BARRA nine")
ax1.plot(dates, BARRA_121, label = "BARRA 121")
plt.legend()
plt.title("Jan 2012 Melbourne Precipitation")
plt.xlabel("Date")
plt.xticks(dates, [date.day for date in dates])
plt.ylabel("Daily Precipitation (mm)")
plt.show()



