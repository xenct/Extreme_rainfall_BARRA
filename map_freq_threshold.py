# number of days above threshold AWAP and BARRA
# first, run "all_functions.py"


# Build the AWAP information
# AWAP data and coordinates
AWAP_data, AWAP_lats, AWAP_lons, AWAP_times = get_AWAP()

# Get BARRA info
start_date = date(2010,1,4)  
end_date = date(2012,12,31)
BARRA_data = []

for DATE in date_range(start_date, end_date):
    filename = f"/g/data3/w42/gt3409/BARRA_R/daily_prcp/{DATE.year}/{DATE.month:02d}/accum_prcp-BARRA_R-v1-daily-{DATE.strftime('%Y%m%d')}.nc" 
    data, _, _ = load_2D_netCDF(filename, 'prcp')
    BARRA_data.append(data)
    if day == start_date:
        _, BARRA_lats, BARRA_lons = load_2D_netCDF(filename, 'prcp')
    BARRA_day_data.close()
BARRA_data = np.array(BARRA_data)


# Set a threshold and levels and map both AWAP and BARRA
#threshold = 10.
#level = 'low'

for threshold, level in [(0.1, "very high"), (0.2, "very high"), (1.0, "very high"), (10, "med"), (20, "low"), (50, "very low")]:
    AWAP_counts = freq_exceed_2d(data = AWAP_data, threshold = threshold)/6 # /numbers of years
    BARRA_counts = freq_exceed_2d(data = BARRA_data, threshold = threshold)/6 #/number of years
    map_AWAP_above_BARRA(AWAP_counts, AWAP_lats, AWAP_lons, BARRA_counts, BARRA_lats, BARRA_lons, levels = freq_levels[level], colormap = freq_colormap, cmap_label = f"Days per year above {threshold}mm")
    plt.suptitle(t="Threshold exceedances 2010-2015", x=0.5, y=0.99) # this title sits a little too close to the AWAP title
    plt.savefig(f"/home/563/gt3409/Documents/images/AWAP_BARRA_days_pa_above_{threshold}mm.png")
    plt.close("all")


for threshold, level in [(0.1, "very high"), (0.2, "very high"), (1.0, "very high"), (10, "med"), (20, "low"), (50, "very low")]:
     AWAP_counts = freq_exceed_2d(data = AWAP_data, threshold = threshold)/6)
     plt.figure(figsize=(6,5))                                                                         
     map_AWAP(AWAP_counts, AWAP_lats, AWAP_lons,title = f"AWAP annual days above {threshold}mm\n2010-2015", levels = freq_levels[level], colormap = freq_colormap, cmap_label = f"Days per year above {threshold}mm")
     plt.tight_layout()                                                            
     plt.savefig(f"/home/563/gt3409/Documents/images/AWAP_days_pa_above_{threshold}mm.png") 
     plt.close("all") 
     #plt.show()              
                




