# run all functions
# run grid_poid_storms

# This script plots a frequency distribution of how often a daily rainfall 
# total occurs in any grid box over land on the SE Asutralian domain in AWAP
# and in BARRA. The BARRA data is filtered to remove very large differences
# from AWAP record amounts by 100mm or more than twice the period's record

# assign the data
filtered_data = AWAPmax_x2_plus100
AWAP_data = np.reshape(prcp_data['AWAP_ann'], prcp_data['AWAP_ann'].size)

# plot the raw data hist for BARRA daily totals
plt.hist(BARRA_raw_1d_prcp, bins = np.arange(0, 500, 20), histtype = 'step', log = True, fill = True, color = 'grey', edgecolor = 'k', alpha = 0.3, label = "BARRA original")

# make the filtered data dimensionless and plot the histogram on the same axis
data_1d = np.reshape(filtered_data, filtered_data.size)
data_1d = data_1d[~np.isnan(data_1d)] # remove the nans
plt.hist(data_1d, bins = np.arange(0, 500, 20),histtype = 'step', log=True, color='b',  edgecolor='b', label = "BARRA filtered")

# for AWAP
data_1d = np.reshape(AWAP_data, AWAP_data.size)
data_1d = data_1d[~np.isnan(data_1d)] # remove the nans
plt.hist(data_1d, bins = np.arange(0, 500, 20), histtype = 'step', log=True,  edgecolor='r', label = "AWAP")

# set titles 
plt.title("Distribution of rainfall amounts")
plt.legend()
plt.ylabel("Frequency")
plt.xlabel("Precipitation (mm)")
plt.ylim((1, 10**8))
plt.xlim((0,500))

plt.show()
