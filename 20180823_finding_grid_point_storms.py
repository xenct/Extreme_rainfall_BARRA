AWAP_rx1day = rx1day(AWAP_data)

for threshold in [0, 25, 50, 75, 100]:
    freq_above_filter = np.sum((BARRA_data>(AWAP_max+threshold)),0)
    map_prcp(freq_above_filter*(AWAP_ann>1), AWAP_lats, AWAP_lons, title = f"Count of exceeding filter\nAWAP record + {threshold}mm", levels = freq_levels['very low'], cmap=freq_colormap)

for factor in [1, 1.25, 1.5, 1.75, 2]:
    freq_above_filter = np.sum((BARRA_data>(AWAP_max*factor)),0)
    map_prcp(freq_above_filter*(AWAP_ann>1), AWAP_lats, AWAP_lons, title = f"Count of exceeding filter\n{factor} * AWAP record", levels = freq_levels['very low'], cmap=freq_colormap)
plt.show()

BARRA_filtered_rx1day = {}

for factor in [1, 1.25, 1.5, 1.75, 2]:
    masked = np.zeros(BARRA_data.shape)
    for i in range(len(BARRA_data)):
        masked[i] = BARRA_data[i]*(BARRA_ann>1)*((BARRA_data[i]<(factor*AWAP_max)))[0]
    BARRA_filtered_rx1day[f'factor {factor}'] = rx1day(masked)
    map_prcp(BARRA_filtered_rx1day[f'factor {factor}'], AWAP_lats, AWAP_lons, title = f"BARRA filtered Rx1day\n{factor} times over record", levels = levels['day'])

for threshold in [0, 25, 50, 75, 100]:
    masked = np.zeros(BARRA_data.shape)
    for i in range(len(BARRA_data)):
        masked[i] = BARRA_data[i]*(BARRA_ann>1)*((BARRA_data[i]<(threshold+AWAP_max)))[0]
    BARRA_filtered_rx1day[f'{threshold}mm'] = rx1day(masked)
    map_prcp(BARRA_filtered_rx1day[f'{threshold}mm'], AWAP_lats, AWAP_lons, title = f"BARRA filtered Rx1day\n{threshold}mm above record", levels = levels['day'])
plt.show()

for factor in [1, 1.25, 1.5, 1.75, 2]:
    data = BARRA_filtered_rx1day[f'factor {factor}'] - AWAP_rx1day
    map_prcp(data, AWAP_lats, AWAP_lons, title = "BARRA_filtered - AWAP rx1day difference",cmap =cmap_custom_RdBu,  levels = np.arange(-200, 200, 20), cmap_extend = 'both', cmap_label = 'difference (mm)')

for threshold in [0, 25, 50, 75, 100]:
    data = BARRA_filtered_rx1day[f'{threshold}mm'] - AWAP_rx1day
    map_prcp(data, AWAP_lats, AWAP_lons, title = f"BARRA_filtered - AWAP rx1day difference\n{threshold}mm",cmap =cmap_custom_RdBu,  levels = np.arange(-200, 200, 20), cmap_extend = 'both', cmap_label = 'difference (mm)')

BARRA_25mm_150p_masked = np.zeros(BARRA_data.shape)
for i in range(len(BARRA_data)):
    BARRA_25mm_150p_masked[i] = BARRA_data[i]*(BARRA_ann>1)*((BARRA_data[i]<(1.5*AWAP_max))&(BARRA_data[i]<(AWAP_max+25)))[0]
BARRA_25mm_150p_rx1day = rx1day(BARRA_25mm_150p_masked)

data = BARRA_25mm_150p_rx1day - AWAP_rx1day
map_prcp(data, AWAP_lats, AWAP_lons, title = f"BARRA_filtered - AWAP rx1day difference\n{threshold}mm",cmap =cmap_custom_RdBu,  levels = np.arange(-200, 200, 20), cmap_extend = 'both', cmap_label = 'difference (mm)')

map_prcp(BARRA_25mm_150p_rx1day, AWAP_lats, AWAP_lons, title = f"BARRA_filtered 25mm and 1.5*AWAP max",  levels = levels['day'], cmap_extend = 'both', cmap_label = '24h rainfall (mm)')




BARRA_75mm_175p_masked = np.zeros(BARRA_data.shape)
for i in range(len(BARRA_data)):
    BARRA_75mm_175p_masked[i] = BARRA_data[i]*(BARRA_ann>1)*((BARRA_data[i]<(1.75*AWAP_max))&(BARRA_data[i]<(AWAP_max+75)))[0]
BARRA_75mm_175p_rx1day = rx1day(BARRA_75mm_175p_masked)

data = BARRA_75mm_175p_rx1day - AWAP_rx1day
map_prcp(data, AWAP_lats, AWAP_lons, title = f"BARRA_filtered - AWAP rx1day difference\n75mm and 1.75 times",cmap =cmap_custom_RdBu,  levels = np.arange(-200, 200, 20), cmap_extend = 'both', cmap_label = 'difference (mm)')

map_prcp(BARRA_75mm_175p_rx1day, AWAP_lats, AWAP_lons, title = f"BARRA_filtered 75mm and 1.75*AWAP max",  levels = levels['day'], cmap_extend = 'both', cmap_label = '24h rainfall (mm)')
plt.show()

BARRA_100mm_200p_masked = np.zeros(BARRA_data.shape)
for i in range(len(BARRA_data)):
    BARRA_100mm_200p_masked[i] = BARRA_data[i]*(BARRA_ann>1)*((BARRA_data[i]<(2*AWAP_max))&(BARRA_data[i]<(AWAP_max+100)))[0]
BARRA_100mm_200p_rx5day = rx5day(BARRA_100mm_200p_masked)


BARRA_rx5day = rx5day(BARRA_data)


map_prcp(AWAP_rx5day, AWAP_lats, AWAP_lons, title = f"AWAP rx5day difference",  levels = levels['week'], cmap_extend = 'max', cmap_label = 'prcp (mm)')
map_prcp(BARRA_100mm_200p_rx5day, AWAP_lats, AWAP_lons, title = f"BARRA_filtered rx5day difference",  levels = levels['week'], cmap_extend = 'max', cmap_label = '5 day prcp (mm)')
map_prcp(BARRA_100mm_200p_rx5day - AWAP_rx5day, AWAP_lats, AWAP_lons, title = f"AWAP rx5day difference",cmap =cmap_custom_RdBu,  levels = np.arange(-200, 200, 20), cmap_extend = 'both', cmap_label = 'difference (mm)')
map_prcp(BARRA_rx5day - AWAP_rx5day, AWAP_lats, AWAP_lons, title = f"AWAP rx5day difference",cmap =cmap_custom_RdBu,  levels = np.arange(-200, 200, 20), cmap_extend = 'both', cmap_label = 'difference (mm)')


AWAP_plot = AWAP_rx5day
BARRA_plot = BARRA_75mm_175p_rx5day
map_prcp(AWAP_plot, AWAP_lats, AWAP_lons, title = f"AWAP rx5day",  levels = levels['week'], cmap_extend = 'max', cmap_label = 'prcp (mm)')
map_prcp(BARRA_plot, AWAP_lats, AWAP_lons, title = f"BARRA_filtered rx5day",  levels = levels['week'], cmap_extend = 'max', cmap_label = '5 day prcp (mm)')
map_prcp(BARRA_rx5day - AWAP_plot, AWAP_lats, AWAP_lons, title = f"AWAP rx5day difference",cmap =cmap_custom_RdBu,  levels = np.arange(-200, 200, 20), cmap_extend = 'both', cmap_label = 'difference (mm)')
map_prcp(BARRA_plot - AWAP_plot, AWAP_lats, AWAP_lons, title = f"AWAP rx5day difference",cmap =cmap_custom_RdBu,  levels = np.arange(-200, 200, 20), cmap_extend = 'both', cmap_label = 'difference (mm)')



threshold = 75
factor = 1.75
BARRA_masked = {}
for threshold, factor in [(0, 1), (25, 1.25), (50, 1.5), (75, 1.75), (100, 2.0)]:
    BARRA_masked[f't{threshold}f{factor}']  = (BARRA_data>(AWAP_max+threshold))*(BARRA_data>(AWAP_max*factor))
    freq_above_filter = np.sum(BARRA_masked[f't{threshold}f{factor}'],0)
    map_prcp(freq_above_filter*(AWAP_ann>1), AWAP_lats, AWAP_lons, title = f"Count of exceeding filter\nAWAP record + {threshold}mm and factor {factor}", levels = freq_levels['very low'], cmap=freq_colormap)
    


plt.plot((np.mean(BARRA_data*(1-BARRA_masked['t100f2.0']),(1,2))))
plt.plot((np.mean(BARRA_data*(AWAP_ann>1),(1,2))))
plt.show()


data = BARRA_data*(AWAP_ann>1)

plt.plot((np.nanpercentile(BARRA_data*(1-BARRA_masked['t100f2.0']),axis = (1,2), q=99)))
plt.plot((np.nanpercentile(BARRA_data*(AWAP_ann>1),axis = (1,2), q=99)))
plt.show()


plt.plot(np.nanmax(BARRA_data*(1-BARRA_masked['t100f2.0']),axis = (1,2)))
plt.plot(np.nanmax(BARRA_data*(AWAP_ann>1),axis = (1,2)))
plt.show()













