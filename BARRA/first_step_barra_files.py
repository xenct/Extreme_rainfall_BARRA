## open terminal
## launch virtual desktop:

# cd /opt/Strudel/
# ./strudel.sh

## Enter username gt3409 (and password)
## launch terminal in VDI
## get to BARRA directory:

# cd /g/data/ma05/BARRA_R/v1
# module use /g/data3/hh5/public/modules
# module load conda/analysis3

## launch ipython

# ipython

cd /g/data/ma05/BARRA_R/v1

from netCDF4 import Dataset                                     
import pandas as pd
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

# make a list of filenames from the start date to the end date
# help for listing dates from https://stackoverflow.com/questions/7274267/print-all-day-dates-between-two-dates comment by Gringo Suave accessed on 14/03/2018

def list_source_filenames(start_date, end_date)
    delta = end_date - start_date
    an_filenames = []
    fc_filenames = []
    for day in range(delta.days + 1):
        date = start_date + datetime.timedelta(day)
        year = date.year
        month = date.month
        day = date.day
        for hour in ["00", "06", "12", "18"]:
            an_filenames.append(f"analysis/spec/accum_prcp/{year}/{month:02d}/accum_prcp-an-spec-PT0H-BARRA_R-v1-{year}{month:02d}{day:02d}T{hour}00Z.nc")
            fc_filenames.append(f"forecast/spec_proc/accum_prcp/{year}/{month:02d}/accum_prcp-fc-spec_proc-PT1H-BARRA_R-v1-{year}{month:02d}{day:02d}T{hour}00Z.nc")
    return an_filenames, fc_filenames

start_date = datetime.date(2010, 1, 1)
end_date = datetime.date(2010, 1, 2)
an_filenames, fc_filenames = list_source_filenames(start_date, end_date)

# Load data
i = 0
filename = fc_filenames[i]
nc_fid = Dataset(filename, 'r')                                     

lat_all = nc_fid.variables['latitude'] 
lat_mask = (np.array(lat_all) > -45) & (np.array(lat_all) < -30)
lat = lat_all[lat_mask]		# Select the lat range of interest
                      
lon_all = nc_fid.variables['longitude']
lon_mask = (np.array(lon_all) > 135) & (np.array(lon_all) < 155)
lon = lon_all[lon_mask] 	# Select the lon range of interest
                         
accum_prcp = nc_fid.variables['accum_prcp'][:,lat_mask,lon_mask]

# Create associations of forecast number and forecast grid
forecast_name = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9']
forecasts = {}
for i in range(9):
	forecasts[forecast_name[i]] = pd.DataFrame(accum_prcp[i,:,:])

# Create associations for hourly total over grid
hourly_name = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9']
hourly_data = {}
for i in range(9-1):
	hourly_data[hourly_name[i]] = forecasts[forecast_name[i+1]] - forecasts[forecast_name[i]]

# Write a new dataset
# help from 
# https://www.unidata.ucar.edu/software/netcdf/examples/programs/simple_xy_wr.py 
# by Jeff Whitaker <jeffrey.s.whitaker@noaa.gov> 

def write_nc_dataset(lat, lon, date):
    # First, set the dimensions of the data:
    nx = len(lon)
    ny = len(lat)
    # Then, open a new netCDF file for writing
    ncfile = Dataset(f"/home/563/gt3409/Documents/hourly{year}{month:02d}{day:02d}.nc", 'w')
    # create x and y dimensions
    ncfile.createDimension('lon', nx)
    ncfile.createDimension('lat', ny)
    # Create the variable
    hourly_prcp = ncfile.createVariable('hourly_prcp', 'float64', ('lon', 'lat'))
    # Write data to variable
    hourly_prcp[:] = hourly_data['h1']
    # Close the file
    ncfile.close() 
    return

# Plot a map of the region
m = Basemap(projection = "mill", llcrnrlon = 65.055, llcrnrlat = -64.945, urcrnrlon = 196.945, urcrnrlat = 19.425)
m.drawcoastlines()
# m.fillcontinents()
parallels = np.arange(-70, 20., 10.)
m.drawparallels(parallels, labels = [1,0,0,0], fontsize = 8)
meridians = np.arange(60., 200, 10.)
m.drawmeridians(meridians, labels = [0,0,0,1], fontsize = 8)
plt.title("BARRA-R")
plt.xlabel("\nLongitude")
plt.ylabel("Latitude\n\n")
plt.show()

#https://matplotlib.org/basemap/users/examples.html
