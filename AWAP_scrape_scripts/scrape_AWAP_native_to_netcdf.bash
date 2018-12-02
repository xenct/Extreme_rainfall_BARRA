# Download the .grid.Z files first using the BoM_AWAP.bash script
# first navigate to the directory you want to download all the .grid.Z files
# then use the bash script to download each day within the time period

# for year in {1963..1990};
# do
#   mkdir ~/Documents/Project/${year}
#   cd ~/Documents/Project/${year}
#   next_year=$((year+1))
#   bash ~/Documents/Project/AWAP_scrape_scripts/BoM_AWAP.bash ${year}0101-${next_year}0101 BoM/AWAP
#   cd ..
#   ncl ~/Documents/Project/AWAP_scrape_scripts/awapdaily2netcdf.ncl
#   rm ~/Documents/Project/${year}
# done

# go home
cd

# eg for the year 2016, make a 2016 directory
mkdir ~/Documents/2016

# navigate to the dirctory with the 2016
cd ~/Documents/2016

# to download all the .grid.Z files into the current directory run the next line in the terminal:
bash ~/Documents/BoM_AWAP.bash 20160101-20170101 BoM/AWAP

# then navigate to the directory with the year file in it (".." goes up a single level)
cd ..

# then run the ncl code to combine all the files from the one year into a single netCDF
# this creates a netcdf file in the current directory called "pre.2016.nc"
ncl ~/Documents/awapdaily2netcdf.ncl

# Next steps may include regridding the data, making each day recognised as a date, masking the ocean, etc. These can relatively easily be done with CDOs



