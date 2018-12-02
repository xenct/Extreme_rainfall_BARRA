# Run 'all_functions.py' before this code
#this code plots 2012 melbourne airport timseries of rainfall

# Get the AWAP data
AWAP, lats, lons, times = load_3D_netCDF("/home/563/gt3409/Documents/AWAP_PRCP_2012-2013_0.5deg_land.nc", "pre", "lat", "lon", "time")

# Choose a goal point
Melb_Coords = (-37.6655, 144.8321)

# Find the nearest grid box for the goal
indices, coords = nearest_coord(Melb_Coords, lats, lons)

# For every AWAP day record for 2012 for the grid point of Melbourne
AWAP_single = []
for day in AWAP[0:366]:
    # get the values of the grids around and including the goal point
    values_for_day = values_of_nsquare(day, indices, n = 0)
    AWAP_single.append(np.nanmean(values_for_day))

# For every AWAP day record for 2012 for the 9 grid points of Melbourne
AWAP_nine = []
for day in AWAP[0:366]:
    # get the values of the grids around and including the goal point
    values_for_day = values_of_nsquare(day, indices, n = 1)
    AWAP_nine.append(np.nanmean(values_for_day))

# Get the 2012 years station data from Melbourne airport
filename = "/home/563/gt3409/Documents/IDCJAC0009_086282_2012_Data.csv"
col_names = ["YYYY", "MM", "DD", "prcp", "accum_period", "Quality"]
station = pd.read_csv(filename, usecols = [2,3,4,5,6,7], skiprows = [0], parse_dates = [[0,1,2]], names = col_names, index_col = "YYYY_MM_DD")

# Plot a timeseries with 2 lines. For 2012: plot the prcp for the station, plot the prcp for the eq AWAP grid box, plot the prcp for the nearest 9 AWAP grid boxes, plot the prcp for BARRA 


time = np.arange(date(2012,1,1), date(2013,1,1))
# Build 2 lists. xticks_locs for the location of the first of the months and
xticks_locs = [date(2012, i, 1) for i in range(1,13)]
# xticks_labels for the three letter month labels "Jan", "Feb", etc
xticks_labels = [date(2012, i, 1).strftime('     %b') for i in range(1,13)]


fig = plt.figure()
ax1 = fig.add_subplot(111)
plt.grid(axis = 'y')
ax1.plot(time, AWAP_single, label = "AWAP single")
ax1.plot(time, AWAP_nine, label = "AWAP nine")
ax1.plot(time, station['prcp'], label = "Station")
plt.legend()
plt.title("2012 Melbourne Precipitation")
plt.xlabel("Date")
plt.xticks(xticks_locs, xticks_labels)
plt.ylabel("Daily Precipitation (mm)")
#ax1.plot(time, BARRA_single)
#ax1.plot(time, BARRA_25)
plt.show()

# plot scatter
fig = plt.figure()
ax1 = fig.add_subplot(111)
plt.grid(axis = 'both')
x = station['prcp']
y = AWAP_single
ax1.scatter(x = station['prcp'], y = AWAP_single, label = "AWAP single")
#calc linear regression
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
plt.plot(x, p(x), "r--")
plt.text(15, 1, f"y = {z[0]:.3f}x + {z[1]:.3f}", color = 'r') 
plt.title("2012 Melbourne Precipitation\nAWAP vs Station")
plt.xlabel("Station Obs (mm)")
plt.ylabel("AWAP (mm)")






