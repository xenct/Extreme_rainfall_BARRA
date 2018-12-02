""" This python script calculates the mean value for each lat and lon for a number of days. It is designed to run from /g/ outside of data and data3
"""

# Load packages
from netCDF4 import Dataset   
import numpy as np
from datetime import timedelta, date, datetime
import time

def list_data_files(start_date, end_date):
    """ This function as the user for the start dates and end dates of the averaging period. The end date is included in the list. The function returns a list of the hourly files needed. 
"""
    ## make a list of the filenames needed
    day = start_date
    filenames = []
    while day <= end_date:
        date = day.strftime('%Y%m%d')
        filenames.append(f"data3/w42/gt3409/accum_prcp-BARRA_R-v1-{date}.nc")
        day = day + timedelta(1)
    return filenames

def spatial_hourly_mean(filenames):
    """takes the filenames, finds the hourly mean rainfall for each lat and lon, returns a 2D array of hourly rainfall means, and the lats and lons as lists"""
    # Get the first fiule to get some intial information
    data = Dataset(filenames[0], "r")
    # make an empty array of zeros of the same size as the data to build the mean precipitation array
    prcp_mean = np.zeros(data['prcp'][0].shape)
    # list the lat and lon values
    lats = [float(f"{x:.3f}") for x in data.variables['lats'][:]]
    lons = [float(f"{x:.3f}") for x in data.variables['lons'][:]]
    # For each day file of hourly data over a day get the average for each point
    n = 0
    for file in filenames:
        print(f"calculating for {file} ...")
        data = Dataset(file, "r")
        # For each hour of data calculate the average value
        for hour in data['times']:
            prcp_value = data['prcp'][hour]
            # For each line of lat 
            for lon in range(len(lons)):
                # and each line of lon
                for lat in range(len(lats)):
                    # Put this as a value of the new map
                    prcp_mean[lat, lon] = (n * prcp_mean[lat, lon] + prcp_value[lat, lon])/(n + 1)
            n += 1
        data.close()
    return prcp_mean, lats, lons

def write_nc_dataset(prcp_mean, lat_array, lon_array, start_date, end_date):
    """This function takes a 2D array of mean precipitation, and a list of latitudes and longitudes.
It writes a netCDF file."""
    filename = f"data3/w42/gt3409/mean_prcp-BARRA_R-v1-{start_date.strftime('%Y%m%d')}-to-{end_date.strftime('%Y%m%d')}.nc"
    ncfile = Dataset(filename, 'w')
    ncfile.description = f"BARRA-R mean hourly precipitation for each grid cell from {start_date.strftime('%d %B %Y')} UTC to {end_date.strftime('%d %B %Y')} UTC over the greater Victorian region."
    ncfile.history = f"Created {date.today().strftime('%Y-%m-%d')}" 
    # Specify dimensions
    ncfile.createDimension('lats', len(lat_array))
    ncfile.createDimension('lons', len(lon_array))
    # Specify variables
    lons = ncfile.createVariable("lons", "f4", ('lons',))
    lats = ncfile.createVariable("lats", "f4", ("lats",))
    prcp = ncfile.createVariable('mean_prcp', 'float32', ('lats', 'lons'))
    # Write data to variables
    lons[:] = lon_array
    lats[:] = lat_array
    prcp[:,:] = prcp_mean
    # Set info for units for CF conventions
    lons.units = 'degrees_east'
    lons.standard_name = 'longitude'
    lons.long_name = 'longitude'
    lons.axis = u'X'
    lats.units = 'degrees_north'
    lats.standard_name = 'latitude'
    lats.long_name = 'latitude'
    lats.axis = u'Y'
    prcp.long_name = 'mean_hourly_precipitation_rate'
    prcp.units =  'kg m-2 h-1'
    # Write data for records
    ncfile.contact = "gtolhurst@student.unimelb.edu.au"
    ncfile.title = f"South Eastern Australia BARRA-R mean hourly precipitation from {start_date.strftime('%d %B %Y')} UTC to {end_date.strftime('%d %B %Y')} UTC."
    ncfile.summary = f"South Eastern Australia BARRA-R mean hourly precipitation from {start_date.strftime('%d %B %Y')} UTC to {end_date.strftime('%d %B %Y')} UTC."
    ncfile.Conventions = 'CF-1.6, ACDD-1.3'
    ncfile.source = "BARRA-R v1"
    ncfile.license = ""
    ncfile.date_created = date.today().strftime("%Y-%m-%d")
    ncfile.creator_name = "Genevieve Christina Tolhurst"
    ncfile.creator_email = "gtolhurst@student.unimelb.edu.au"
    ncfile.institution = "University of Melbourne"
    ncfile.organisation = "ARC Centre of Excellence for Climate Extremes"
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

## get start date
start_year, start_month, start_day = [int(x.strip(',')) for x in input("Enter start date (\"year, month, day\"): ").split()]
start_date = date(start_year, start_month, start_day)

## Get end date
end_year, end_month, end_day = [int(x.strip(',')) for x in input("Enter end date (\"year, month, day\"): ").split()]
end_date = date(end_year, end_month, end_day)

# Start timer
print("start timer ...")
program_start_time = time.time()

# Get a list of filenames from the date of interest
print("getting list of filenames ...")
filenames = list_data_files(start_date, end_date)

# Calculate the mean hourly rainfall for each cell in the BARRA-R reanalysis
print("calculating mean hourly rainfall rate for each grid cell ...")
prcp_mean, lats, lons = spatial_hourly_mean(filenames)

# Write a netCDF file with the mean precipitation calculted
print("writing netCDF ...")
write_nc_dataset(prcp_mean, lats, lons, start_date, end_date)

# Show the time for calculations and writing the file
print(f"{(time.time() - program_start_time):.2f} seconds have elapsed.")



