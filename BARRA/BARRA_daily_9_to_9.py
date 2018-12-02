# this program will take the hourly data from the 24 hour utc files and make a file of daily rainfall totals from the BARRA data
# Each day will be its own netcdf similar to the structure of the BARRA data made by bom
from netCDF4 import Dataset   
import numpy as np
from datetime import timedelta, date, datetime
import time
from dateutil import tz

# Define the timezones, UTC and Victorian
utc_zone = tz.gettz('UTC')
vic_zone = tz.gettz('Australia/Melbourne')


def calc_daily_BARRA(rain_date, data, filename1 = ""):
    # Calculate the local start time, from 9am the day before the recorded rain date
    start_date = rain_date-timedelta(days=1)
    aest_start = datetime(start_date.year, start_date.month, start_date.day, 9, tzinfo = vic_zone)
    # Convert this to UTC time
    utc_start = aest_start.astimezone(utc_zone)
    # Get the name of the first file using UTC time, then load this data
    filename0 = f"/g/data3/w42/gt3409/BARRA_R/hourly_prcp/{utc_start.year}/{utc_start.month:02d}/accum_prcp-BARRA_R-v1-{utc_start.strftime('%Y%m%d')}.nc"
    if filename0 != filename1:
        data = Dataset(filename0, "r")
    # Define an array of zeros to add the rainfall accumulation to
    prcp_day = np.zeros(data['prcp'][0].shape)
    # Iterate over each of the 24 hours in the file, add the precipitation values if they occur after 9am local time
    for hour in range(24):
        # date of the file and utc 
        date = datetime(utc_start.year, utc_start.month, utc_start.day, hour, tzinfo = utc_zone)
        if date >= aest_start:
            prcp_day +=  data['prcp'][hour]
    data.close()
    # Get the second file
    utc_next = (utc_start + timedelta(days=1))
    filename1 = f"/g/data3/w42/gt3409/BARRA_R/hourly_prcp/{utc_next.year}/{utc_next.month:02d}/accum_prcp-BARRA_R-v1-{utc_next.strftime('%Y%m%d')}.nc"     
    data = Dataset(filename1, "r")
    for hour in range(24):
        # date of the file and utc 
        date = datetime(utc_next.year, utc_next.month, utc_next.day, hour, tzinfo = utc_zone)
        if date < (aest_start + timedelta(days=1)):
            prcp_day +=  data['prcp'][hour]
    return data, prcp_day, filename1

# Write the new dataset as a .nc file Helpful notes from http://pyhogs.github.io/intro_netcdf4.html
def write_nc_dataset(data, lat_array, lon_array, DATE):
    """This function takes the 1D arrays of a variable (ie daily precipitation), 
    latitude and longitude, and writes a .nc file to my gt3409 folder in w42 group in NCI.
    This file is two dimensional (len(lat), len(lon)).  The file is called 
    "accum_prcp-BARRA_R-v1-rainfall_to_9am-{DATE}.nc" where DATE is YYYYMMDD.
    """
    # Open a new netCDF file for writing write it to {filename}
    DATE_YMD = DATE.strftime('%Y%m%d')
    filename = f"/g/data3/w42/gt3409/BARRA_R/daily_prcp/{DATE.year}/{DATE.month:02d}/accum_prcp-BARRA_R-v1-daily-{DATE_YMD}.nc"
    ncfile = Dataset(filename, 'w')
    ncfile.description = f"BARRA-R 24 hour rainfall accumulation until 9AM {DATE.strftime('%d %B %Y')} AEST over the greater Victorian region."
    # Specify dimensions
    ncfile.createDimension('lats', len(lat_array))
    ncfile.createDimension('lons', len(lon_array))
    # Specify variables
    lats = ncfile.createVariable("lats", "f4", ("lats",))
    lons = ncfile.createVariable("lons", "f4", ('lons',))
    prcp = ncfile.createVariable('prcp', 'float32', ('lats', 'lons'))
    # Write data to variables
    lats[:] = lat_array
    lons[:] = lon_array
    prcp[:,:] = data
    # Set info for units for CF conventions
    lats.units = 'degrees_north'
    lats.long_name = 'latitude'
    lats.standard_name = 'latitude'
    lats.axis = u'Y'
    lons.units = 'degrees_east'
    lons.long_name = 'longitude'
    lons.standard_name = 'longitude'
    lons.axis = u'X'
    prcp.units =  'kg m-2'
    prcp.long_name = "precipitation_amount"
    prcp.standard_name = "precipitation_amount"
    # Write data for records
    ncfile.title = f"South Eastern Australia {DATE.strftime('%d %B %Y')} BARRA-R precipitation reanalysis v1"
    ncfile.summary = f"South Eastern Australia {DATE.strftime('%d %B %Y')} BARRA-R 24 hour precipitation reanalysis v1"
    ncfile.institution = "University of Melbourne"
    ncfile.organisation = "ARC Centre of Excellence for Climate Extremes"
    ncfile.source = "BARRA-R v1"
    ncfile.license = ""
    ncfile.Conventions = 'CF-1.6 ACDD-1.3'
    ncfile.date_created = date.today().strftime("%Y-%m-%d")
    ncfile.creator_name = "Genevieve Christina Tolhurst"
    ncfile.contact = "gtolhurst@student.unimelb.edu.au"
    ncfile.creator_email = "gtolhurst@student.unimelb.edu.au"
    ncfile.history = f"Created {date.today().strftime('%d-%m-%Y')}" 
    ncfile.references = "Jakob, D, et al 2017, 'An atmospheric high-resolution regional reanalysis for Australia', The Bulletin of the Australia Meteorological and Oceanographic Society, September, pp. 16-23"
    ncfile.time_coverage_start = f"{(DATE - timedelta(days=1)).strftime('%d-%m-%Y')} 09:00 AEST"
    ncfile.time_coverage_end = f"{DATE.strftime('%d-%m-%Y')} 9:00 AEST"
    ncfile.geospatial_lat_min = lats[0]
    ncfile.geospatial_lat_max = lats[-1]
    ncfile.geospatial_lon_min = lons[0]
    ncfile.geospatial_lon_max = lons[-1]
    for lat in range(len(lats)):
        prcp[lat,:] = data[lat][:]
    # Close the file
    ncfile.close() 
    print(f"File {filename} successfully created")
    return

def BARRA_9to9_day_square(start_date, end_date, station_coords, n = 1, filename_stub = "/g/data3/w42/gt3409/BARRA_R/daily_prcp"):
    """This function combines multiple functions here:
- date_range()
- load_2D_netCDF()
- nearest_coord()
- nsquare_day_prcp()
  - values_of_nsquare()
takes start and end dates, the name of the varaible, station coordinates for the goal loaction, and n for the size of the (2n+1)^2 box.
The function returns the dates for the timseries and the timseries of daily prcp amounts.
"""
    # Specify the date range
    dates = date_range(start_date, end_date)
    day_prcp = []
    for DATE in dates: # for each date
        filename = f"{filename_stub}/{DATE.year}/{DATE.month:02d}/accum_prcp-BARRA_R-v1-daily-{day.strftime('%Y%m%d')}.nc" # get the unique filename 
        print(f"filename: {filename}")
        prcp, lats, lons = load_2D_netCDF(filename, var_name = 'prcp') # load all the data for that day
        centre_indices, _ = nearest_coord(station_coords, lats, lons) # Get the indices of the nearest grid box
        day_prcp.append(np.mean(values_of_nsquare(prcp, centre_indices, 1))) # Write a list of mean daily prcp totals as day_prcp
    return dates, day_prcp

filename1 = ''
prcp_day = {}
data = Dataset(f"/g/data3/w42/gt3409/BARRA_R/hourly_prcp/2012/01/accum_prcp-BARRA_R-v1-20120101.nc", "r")
lats = data['lats'][:]
lons = data['lons'][:]

#for rain_date in date_range(datetime(2010, 1, 4), datetime(2016,1,1)):
#   data, prcp_day[f"{rain_date.strftime('%Y-%m-%d')}"], filename1 = calc_daily_BARRA(rain_date, data, filename1 = filename1)
#   map_BARRA(prcp_day[f"{rain_date.strftime('%Y-%m-%d')}"], lats, lons, title = f"BARRA-R {rain_date.strftime('%d %B %Y')}",levels= levels["day"])
#   plt.savefig(f"/home/563/gt3409/Documents/images/BARRA_day/BARRA_day_{rain_date.strftime('%Y%m%d')}")
#   plt.close("all")

#   write_nc_dataset(data =prcp_day[f"{rain_date.strftime('%Y-%m-%d')}"], lat_array = lats, lon_array = lons, DATE = rain_date)


