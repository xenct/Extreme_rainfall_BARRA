"""This python script aims to calculate the mean value of every lat/lon grid cells for a number of days. It is designed to read data from my VDI desktop and write a netCDF of the mean daily precipitation values.
This code is written to work from /home/563/gt3409/"""

# Import packages
from netCDF4 import Dataset
import numpy as np
from datetime import timedelta, date, datetime
import time
import matplotlib.pyplot as plt

# Get data:
filename = "Documents/AWAP_PRCP_2012-2013_0.5deg_land.nc"
data = Dataset(filename, 'r')

# Times in the AWAP file are daily given as "YYYYMMDD."
# Our variable of interest is called 'pre'.
# It has dimensions (time = 731, lat = 68, lon = 88)
# time [20120101., 20121231.] ie Jan 1 2012 to Dec 31 2013
# lat [-10.0, -43.5]
# lon [112, 155.5]

# Need to change the time and lat and lon dimensions to match with BARRA data

# list of dates
start_date = date(2012, 1, 1)
end_date = date(2012, 1, 7)

time_list = []
day = start_date
while day <= end_date:
    time_list.append(float(day.strftime('%Y%m%d.')))
    day += timedelta(1) 

# Use the list of dates to make an array of the subset of times 
day_indices = {}
AWAP_lists = []
for time in time_list:
    day_indices[time] = np.where(data['time'][:] == time)
    AWAP_lists.append(data['pre'][day_indices[time]][0])

def lat_lon_mask(lons_full, lats_full, lon_min, lon_max, lat_min, lat_max):
    """Thie function takes a full list of latitudes and longitudes, and minimum and maximum values for lats and lons. The function returns a 2D mask which specifies True for every coordinate between (and including) the boundaries. the function also returns the shortened lats and lons"""
    # Mask lons
    lon_mask = (lons_full >= lon_min) & (lons_full <= lon_max)
    lons = lons_full[lon_mask]
    # Mask lats
    lat_mask = (lats_full >= lat_min) & (lats_full <= lat_max)
    lats = lats_full[lat_mask]
    # make 2D mask
    lat_lon_mask = lon_mask[np.newaxis, :] & lat_mask[:, np.newaxis]
    return lat_lon_mask, lats, lons

lat_lon_mask, lats, lons = lat_lon_mask(lons_full = data['lon'][:], lats_full = data['lat'][:], lon_min = 135, lon_max = 155, lat_min = -45, lat_max = -30)

data.close()

# Get the mean
def prcp_mean(data, times, lats, lons):
    """This function takes data, and its 3 dimensions: times, lats, and lons to return a 2D array of mean values.  Missing values are treated as zero.  The mean is calculated progressively, that is for each time cycle the mean is calculated from the mean of all the time periods before.
eg mean(n = 5) = 4/5 * mean(n = 4) + 1/5 * value(5)"""
    # Make empty array of the size that lat and lon define
    prcp_mean = np.zeros((len(lats), len(lons)))
    # Start a counter of the number of vlaues averaging across
    n = 0
    # For each period of time get the orginal 2D records
    for time in times:
        print("now calculating for {time.}")
        time_ix = times.index(time)
        prcp_value = data[time_ix][lat_lon_mask].reshape(len(lats), len(lons))
        # For each latitude and each longitude calculate the mean progressively
        for lat in lats:
            lat_ix = np.where(lats == lat)
            for lon in lons:
                lon_ix = np.where(lons == lon)
                prcp_mean[lat_ix, lon_ix] = (n * prcp_mean[lat_ix, lon_ix] + prcp_value[lat_ix, lon_ix])/(n + 1)
        n += 1
    return prcp_mean

prcp_mean = prcp_mean(data = AWAP_lists, times = time_list, lats = lats, lons = lons)

# plt.imshow(prcp_mean, cmap = 'nipy_spectral')
# plt.show()

def write_nc_dataset(prcp_mean, lat_array, lon_array, start_date, end_date):
    """This function takes a 2D array of mean precipitation, and a list of latitudes and longitudes.
It writes a netCDF file.  Works from /g/ outside of data/ and data3/ """
    filename = f"data3/w42/gt3409/mean_prcp-AWAP-SE-Aust-{start_date.strftime('%Y%m%d')}-to-{end_date.strftime('%Y%m%d')}.nc"
    ncfile = Dataset(filename, 'w')
    ncfile.description = f"AWAP mean daily precipitation for each grid cell from {start_date.strftime('%d %B %Y')} UTC to {end_date.strftime('%d %B %Y')} UTC over the greater Victorian region."
    # Specify dimensions
    ncfile.createDimension('lats', len(lat_array))
    ncfile.createDimension('lons', len(lon_array))
    # Specify variables
    lats = ncfile.createVariable("lats", "f4", ("lats",))
    lons = ncfile.createVariable("lons", "f4", ('lons',))
    prcp = ncfile.createVariable('mean_prcp', 'float32', ('lats', 'lons'))
    # Write data to variables
    lats[:] = lat_array
    lons[:] = lon_array
    prcp[:,:] = prcp_mean
    # Set info for units for CF conventions
    lats.units = 'degrees_north'
    lats.long_name = 'latitude'
    lats.standard_name = 'latitude'
    lats.axis = u'Y'
    lons.units = 'degrees_east'
    lons.long_name = 'longitude'
    lons.standard_name = 'longitude'
    lons.axis = u'X'
    prcp.long_name = 'precipitation_amount'
    prcp.units =  'kg m-2 per day'
    # Write data for records
    ncfile.title = f"South Eastern Australia AWAP mean daily precipitation from {start_date.strftime('%d %B %Y')} UTC to {end_date.strftime('%d %B %Y')} UTC."
    ncfile.summary = f"South Eastern Australia AWAP mean daily precipitation from {start_date.strftime('%d %B %Y')} UTC to {end_date.strftime('%d %B %Y')} UTC."
    ncfile.institution = "University of Melbourne"
    ncfile.organisation = "ARC Centre of Excellence for Climate Extremes"
    ncfile.source = "AWAP"
    ncfile.license = ""
    ncfile.Conventions = 'CF-1.6, ACDD-1.3'
    ncfile.date_created = date.today().strftime("%Y-%m-%d")
    ncfile.creator_name = "Genevieve Christina Tolhurst"
    ncfile.contact = "gtolhurst@student.unimelb.edu.au"
    ncfile.creator_email = "gtolhurst@student.unimelb.edu.au"
    ncfile.history = f"Created {date.today().strftime('%Y-%m-%d')}" 
    ncfile.references = "Jones, D, Wang, W, & Fawcett, R 2009, 'High-quality spatial climate data-sets for Australia', Australian Meteorological and Oceanographic Journal, vol. 58, no. 4, pp. 233-248."
    ncfile.time_coverage_start = f"{start_date.strftime('%Y-%m-%d')} 00:00 UTC"
    ncfile.time_coverage_end = f"{end_date.strftime('%Y-%m-%d')} 23:00 UTC"
    ncfile.geospatial_lat_min = lats[0]
    ncfile.geospatial_lat_max = lats[-1]
    ncfile.geospatial_lon_min = lons[0]
    ncfile.geospatial_lon_max = lons[-1]
    # Close the file
    ncfile.close() 
    print(f"{filename} successfully created")
    return

write_nc_dataset(prcp_mean, lats, lons, start_date, end_date)
