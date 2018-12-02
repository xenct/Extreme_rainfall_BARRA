# This code aims to write a file for 24 hours of BARRA-R data
# this code is designed to run on my strudel with username gt3409
# The code will make a file for each 24 hour UTC period
# The code runs for python3.6
# the code is designed to run from /g/

# Import packages
from netCDF4 import Dataset
import numpy as np
from datetime import timedelta, date, datetime
import time

# Get filenames to read for the days
def list_source_filenames(start_date, end_date):
    """This function takes you to the BARRA_R/v1 directory, then takes
    the start date and end date as datetime objects and makes a 
    list of all possible forecats and analysis BARRA_R files in the 
    ma05 group which have arrays needed to make a hourly dataset from
    the start date up until, but not including the end date.
    The function returns a list of analysis files "an_filenames" and
    a list of forecast files "fc_filenames".
    """
    delta = end_date - start_date
    an_filenames = []
    fc_filenames = []
    for day in range(delta.days):
        DATE = start_date + timedelta(day)
        year = DATE.year
        month = DATE.month
        day = DATE.day
        for hour in ["00", "06", "12", "18"]:
            an_filenames.append(f"/g/data/ma05/BARRA_R/v1/analysis/spec/accum_prcp/{year}/{month:02d}/accum_prcp-an-spec-PT0H-BARRA_R-v1-{year}{month:02d}{day:02d}T{hour}00Z.nc")
            fc_filenames.append(f"/g/data/ma05/BARRA_R/v1/forecast/spec_proc/accum_prcp/{year}/{month:02d}/accum_prcp-fc-spec_proc-PT1H-BARRA_R-v1-{year}{month:02d}{day:02d}T{hour}00Z.nc")
    return an_filenames, fc_filenames

# Load the data from the filenames
def get_hourly_from_files(analysis_files, forecast_files, lon_min = 0, lon_max = 360, lat_min = -90, lat_max = 90):
    """ This function takes a list of analysis and a list of forecast
    netCDF filenames, reads them in, creates 6 hourly data for each 
    file pair saved to my home directory in Strudel.
    """
    if len(analysis_files) != len(forecast_files):
        return "Must have equal analysis files and forecast files"	# Quit function if this is wrong
    # Get the lat and lon of the study area. Only calculate this once as it stays the same
    an_data = Dataset(analysis_files[0], "r")
    lat = an_data.variables["latitude"]
    lat_mask = (np.array(lat) > lat_min) & (np.array(lat) < lat_max)
    lat_array = lat[lat_mask]
    lon = an_data.variables["longitude"]
    lon_mask = (np.array(lon) > lon_min) & (np.array(lon) < lon_max)
    lon_array = lon[lon_mask]
    hourly_prcp = {}	# This dictionary will store the hourly rainfall totals
    
    for an, fc in zip(analysis_files, forecast_files):
        # for every file pair get the data and calculate 6 * hourly rainfall arrays
        an_data = Dataset(an, "r")
        fc_data = Dataset(fc, "r")
        an_accum_prcp = an_data.variables['accum_prcp'][lat_mask,lon_mask]
        fc_accum_prcp = fc_data.variables['accum_prcp'][0:6,lat_mask,lon_mask]
        for i in range(6):
            # For the first six hours of forecasts calculate the hourly rainfall and store it under "YYYYMMDDHH"
            date_h = datetime.utcfromtimestamp(3600*(fc_data.variables["time_bnds"][:][:][:,1][i] - 1)).strftime('%Y%m%d%H')
            if i == 0:
                hourly_prcp[f"{date_h}"] = fc_accum_prcp[i] - an_accum_prcp
            else:
                hourly_prcp[f"{date_h}"] = fc_accum_prcp[i] - fc_accum_prcp[i - 1]
    hour_list = sorted(hourly_prcp.keys())
    prcp_list = []
    for hour in range(24):
        prcp_list.append(hourly_prcp[hour_list[hour]])
    prcp_array = np.array(prcp_list)
    return lat_array, lon[lon_mask], prcp_array

# Write the new dataset as a .nc file Helpful notes from http://pyhogs.github.io/intro_netcdf4.html
def write_nc_dataset(lat_array, lon_array, prcp_array):
    """This function takes the 1D arrays of latitude and longitude, and the 
    dictionary of 24 arrays of hourly precipitation and writes a .nc file
    to my gt3409 folder in w42 group in NCI. This file is three dimensional 
    (24, len(lat), len(lon)).  The file is called "accum_prcp-BARRA_R-v1-{DATE}.nc" where DATE
    is YYYYMMDD.
    """
    # Open a new netCDF file for writing write it to {filename}
    DATE_YMD = DATE.strftime('%Y%m%d')
    filename = f"/g/data3/w42/gt3409/accum_prcp-BARRA_R-v1-{DATE_YMD}.nc"
    ncfile = Dataset(filename, 'w')
    ncfile.description = f"BARRA-R 24 hour period from {start_date.strftime('%d %B %Y')} UTC over the greater Victorian region."
    # Specify dimensions
    ncfile.createDimension('times', 24)
    ncfile.createDimension('lats', len(lat_array))
    ncfile.createDimension('lons', len(lon_array))
    # Specify variables
    times = ncfile.createVariable("times", "i4", ("times",))
    lats = ncfile.createVariable("lats", "f4", ("lats",))
    lons = ncfile.createVariable("lons", "f4", ('lons',))
    prcp = ncfile.createVariable('prcp', 'float32', ('times', 'lats', 'lons'))
    # Write data to variables
    times[:] = np.arange(24)
    lats[:] = lat_array
    lons[:] = lon_array
    # Set info for units for CF conventions
    times.units = f'hours since {DATE} 00UTC'
    times.long_name = "time"
    times.standard_name = "time"
    times.axis = u'T' 
    times.calendar = "standard"
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
    ncfile.summary = f"South Eastern Australia {DATE.strftime('%d %B %Y')} BARRA-R hourly precipitation reanalysis v1"
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
    ncfile.time_coverage_start = f"{DATE.strftime('%d-%m-%Y')} 00:00 UTC"
    ncfile.time_coverage_end = f"{DATE.strftime('%d-%m-%Y')} 23:00 UTC"
    ncfile.geospatial_lat_min = lats[0]
    ncfile.geospatial_lat_max = lats[-1]
    ncfile.geospatial_lon_min = lons[0]
    ncfile.geospatial_lon_max = lons[-1]

    for hour in times:
        prcp[hour,:,:] = prcp_array[hour][:,:]
    # Close the file
    ncfile.close() 
    print(f"File /g/{filename} successfully created")
    return

program_start_time = time.time()

DATE = start_date
while DATE <= end_date:
    # Get filenames to read for each day
    an_filenames, fc_filenames = list_source_filenames(DATE, DATE + timedelta(1))
    # Load the data from the filenames
    lat_array, lon_array, hourly_prcp = get_hourly_from_files(an_filenames, fc_filenames, lon_min = 135, lon_max = 155, lat_min = -45, lat_max = -30)
    # Save the dataset to file
    write_nc_dataset(lat_array, lon_array, hourly_prcp, )
    print(f"{(time.time() - program_start_time):.2f} seconds have elapsed.")
    DATE = DATE + timedelta(days = 1)

