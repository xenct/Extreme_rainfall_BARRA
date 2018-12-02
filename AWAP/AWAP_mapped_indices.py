# This code calculates mean, max, and percentiles over awap and then maps them

AWAP_data, AWAP_lats, AWAP_lons, _ = get_AWAP()

# Find the mean value of the AWAP data array
AWAP_mean = np.nanmean(AWAP_data, axis = 0)
# Find the maximum value of the day rainfall data in AWAP data array
AWAP_max = np.nanmax(AWAP_data, axis = 0)
# Find the percentile of the AWAP data array, and replace the 99999.8984375 fill number with zero.
AWAP_95p = np.nanpercentile(AWAP_data, axis = 0, p=95)
AWAP_95p[AWAP_95p > 9999] = 0

AWAP_99p = np.nanpercentile(AWAP_data, axis = 0, p=99)
AWAP_99p[AWAP_99p > 9999] = 0


# Visualise the AWAP values
map_AWAP(AWAP_mean*365, AWAP_lats, AWAP_lons, levels = levels['year'])
plt.show()

map_AWAP(AWAP_max, AWAP_lats, AWAP_lons, levels = levels['day'])
plt.show()


