from pylab import cm
custom_RdBu = cm.get_cmap("RdBu",20)(np.arange(20))
custom_RdBu[9] = [1,1,1,1]
custom_RdBu[10] = [1,1,1,1]

cmap_custom_RdBu = LinearSegmentedColormap.from_list("RdWtBu", custom_RdBu, 20) 


AWAP_max, ref_lat, ref_lon = load_2D_netCDF('/g/data3/w42/gt3409/AWAP/AWAP_1961-1990_0.11_rx1day_small_land.nc', 'rx1day', 'lat', 'lon')     

count = 0
for i in range(len(BARRA_data)):
    # This identifier finds if the value of cell is greater 100mm more than double the maximum from 1961-1990 records
    identifier = (BARRA_data[i]>(2*AWAP_max+100))*(AWAP_ann>1)
    #print(f'There were {np.sum(identifier)} points of interest identified at i = {i}')
    if np.sum(identifier)>0:
        #map_prcp(BARRA_prcp[i], BARRA_lats, BARRA_lons, levels=levels['day'])
        #plt.show()
        count +=1
print(count)




BARRA_masked = np.zeros(BARRA_data.shape)
for i in range(len(BARRA_data)):
    BARRA_masked[i] = BARRA_data[i]*(BARRA_ann>1)*((BARRA_data[i]<(2*AWAP_max))&(BARRA_data[i]<(AWAP_max+100)))[0]


BARRA_twice_masked = np.zeros(BARRA_data.shape)
for i in range(len(BARRA_data)):
    BARRA_twice_masked[i] = BARRA_data[i]*(BARRA_ann>1)*((BARRA_data[i]<(2*AWAP_max)))[0]

BARRA_100_masked = np.zeros(BARRA_data.shape)
for i in range(len(BARRA_data)):
    BARRA_100_masked[i] = BARRA_data[i]*(BARRA_ann>1)*(BARRA_data[i]<(AWAP_max+100))[0]



lats = AWAP_lats
lons = BARRA_lats
AWAP_rx1day = rx1day(AWAP_data)
BARRA_rx1day_raw = rx1day(BARRA_data)*(AWAP_ann>1)
BARRA_rx1day_filtered = rx1day(BARRA_masked)
BARRA_rx1day_twice_filtered = rx1day(BARRA_twice_masked)
BARRA_rx1day_100_filtered = rx1day(BARRA_100_masked)

map_prcp(BARRA_rx1day_100_filtered, AWAP_lats, AWAP_lons, title = "BARRA filtered Rx1day\n100mm over record", levels = levels['day'])
plt.savefig('Documents/images/BARRA_filtered_100mm_over_record.png')

map_prcp(BARRA_rx1day_twice_filtered, AWAP_lats, AWAP_lons, title = "BARRA filtered Rx1day\ntwice over record", levels = levels['day'])
plt.savefig('Documents/images/BARRA_filtered_twice_over_record.png')

map_prcp(BARRA_rx1day_filtered, AWAP_lats, AWAP_lons, title = "BARRA filtered Rx1day\ntwice or > 100mm record", levels = levels['day'])
plt.savefig('Documents/images/BARRA_filtered_twice_over_100mm.png')

map_prcp(BARRA_rx1day_raw, AWAP_lats, AWAP_lons,title='BARRA original Rx1day', levels = levels['day'])
plt.savefig('Documents/images/BARRA_raw_rx1day.png')

map_prcp(AWAP_rx1day , AWAP_lats, AWAP_lons,title='AWAP Rx1day 2010-2015', levels = levels['day'])
plt.savefig('Documents/images/AWAP_rx1day.png')

map_prcp((AWAP_rx1day -BARRA_rx1day_raw), AWAP_lats, AWAP_lons, title = "AWAP - BARRA rx1day difference",cmap =cmap_custom_RdBu,  levels = np.arange(-200, 200, 20), cmap_extend = 'both', cmap_label = 'difference (mm)')
plt.savefig('Documents/images/AWAP-BARRA_raw_rx1day.png')

map_prcp((AWAP_rx1day -BARRA_rx1day_filtered), AWAP_lats, AWAP_lons, title = "AWAP - BARRA_filtered rx1day difference",cmap =cmap_custom_RdBu,  levels = np.arange(-200, 200, 20), cmap_extend = 'both', cmap_label = 'difference (mm)')
plt.savefig('Documents/images/AWAP-BARRA_filtered_rx1day.png')




AWAP_prcp =  prcp_data['AWAP_ann'][3:]
gpsa_loc = {}
for limit in range(0, 700, 50):
    gpsa_loc[limit] = np.where((AWAP_prcp>limit))  
    print(len(set(gpsa_loc[limit][0]))) 

BARRA_prcp =  prcp_data['BARRA_ann'][:-1]*(np.nansum(AWAP_ann,0)>1)
gpsb_loc = {}
for limit in range(0, 700, 50):
    gpsb_loc[limit] = np.where((BARRA_prcp>limit))  
    print(len(set(gpsb_loc[limit][0]))) 

gpsab_loc = {}
for limit in range(0, 700, 50):
    gpsab_loc[limit] = np.where(((BARRA_prcp-AWAP_prcp)>limit))  
    print(len(set(gpsab_loc[limit][0]))) 


gpsax = list(gpsa_loc.keys())
gpsay = [len(set(gpsa_loc[key][0]))for key in gpsa_loc.keys()]  

gpsbx = list(gpsb_loc.keys())
gpsby = [len(set(gpsb_loc[key][0]))for key in gpsb_loc.keys()] 

gpsabx = list(gpsb_loc.keys())
gpsaby = [len(set(gpsab_loc[key][0]))for key in gpsab_loc.keys()] 

plt.plot(gpsax, gpsay)
plt.plot(gpsbx, gpsby)
plt.plot(gpsabx, gpsaby)
plt.title(f"number of days with grid points exceeding threshold")
plt.ylabel("total day count 2010-2015")
plt.xlabel("Threshold (mm)")
plt.ylim(0,1000)
plt.xlim(0, 650)
plt.legend(['AWAP', 'BARRA', 'B-A'])
plt.show()

"""
This plot above shows that when you subtract the AWAP amoun from the BARRA amounts, gris by grid, the remaining difference for each day is larger than the AWAP extremes. The outliers in BARRA don't line up with the extremes in AWAP (grid to grid)  
""" 

land_mask = (np.nansum(prcp_data['AWAP_ann'],0) > 1)

# calculated indices
indices = {}
keys = list(prcp_data.keys())
for key in keys:
    data = prcp_data[key]*land_mask
    for fn in single_input_functions:
        indices[f'{key}_{fn.__name__}'] = fn(data)
    for fn in double_input_functions:
        indices[f'{key}_{fn.__name__}'] = fn(data, data)



seasons = ['DJF', 'MAM', 'JJA', 'SON']
diff = {}
for seas in seasons:
    season = []
    for threshold in range(0, 51):
        if seas == 'DJF':
            A = rr1(prcp_data[f'AWAP_{seas}'][3:], threshold)
            B = rr1(prcp_data[f'BARRA_{seas}'][:-1], threshold)
        else:
            A = rr1(prcp_data[f'AWAP_{seas}'], threshold)
            B = rr1(prcp_data[f'BARRA_{seas}'], threshold)  
        B = B*land_mask     
        season.append(np.nanmean(B-A))
        diff[f'{seas}'] = season

for seas in seasons:
    plt.plot(diff[seas])
plt.plot([0 for i in range(51)], color = 'k')
plt.ylim(-1,1)
plt.xlim(0, 51)
plt.legend(seasons)
plt.xlabel("(mm)")
plt.title("BARRA - AWAP difference between frequency of exceedance\nSE Australia 2010-2015")
plt.show()


