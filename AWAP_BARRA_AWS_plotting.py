# run all_functions.py before using this script


# Build 2 lists. xticks_locs for the location of the first of the months and
# xticks_labels for the three letter month labels "Jan", "Feb", etc
xticks_locs = []
xticks_labels = []
for i in range(1,13):
    xticks_locs.append(date(2012, i, 1))
    xticks_labels.append(date(2012, i, 1).strftime('     %b'))


start_date = date(2012,1, 1)
end_date = date(2012, 12,31)
station_coords = (-37.6655, 144.8321)

BARRA_dates, BARRA_data = BARRA_daily_square(start_date, end_date, station_coords, n = 5, filename_stub = "/g/data3/w42/gt3409/accum_prcp-BARRA_R-v1-")

AWAP, AWAP_lats, AWAP_lons, AWAP_dates = get_AWAP(filename = "/home/563/gt3409/Documents/AWAP_PRCP_2012-2013_0.5deg_land.nc")

AWAP_dates, AWAP_data  = AWAP_daily_square(data = AWAP,
                               lats = AWAP_lats,
                               lons = AWAP_lons,
                               times = AWAP_dates,
                               start_date=start_date,
                               end_date=end_date,
                               station_coords = station_coords,
                               n = 1)

fig = plt.figure(figsize=(10,3))
ax1 = fig.add_subplot(111)
plt.grid(axis = 'y')
ax1.plot(AWAP_dates, AWAP_data, label = "AWAP nine")
ax1.plot(BARRA_dates, BARRA_data, label = "BARRA 121")
ax1.plot(np.arange(date(2012,1,1), date(2013,1,1)), station['prcp'], label = "Station")
plt.legend()
plt.title("2012 Melbourne Precipitation")
plt.xlabel("Date")
plt.xticks(xticks_locs, xticks_labels)
plt.ylabel("Daily Precipitation (mm)")
plt.savefig("/home/563/gt3409/Documents/images/AWAP_BARRA_AWS_2012_timeseries.png")
plt.show()

spearmanr(station['prcp'], BARRA_121) # BARRA data for 2012, Centred on Melbourne for 121 grid boxes has a Spearman rank correltaion with the AWS at melbourne airport of SpearmanrResult(correlation=0.77248407603347624, pvalue=8.9235347620197711e-74)

spearmanr(station['prcp'], AWAP_data) # AWAP data for 2012, centred on Melbourne for 9 gridboxes has a spearman rank correlation with the AWS at melbourne airport of SpearmanrResult(correlation=0.8212888199971663, pvalue=9.6957962226628948e-91)


"""The following are results for BARRA and melbourne airport aws"""
#spearmanr(station['prcp'], BARRA)


n=0
BARRA_single=[]
BARRA_nine=[]
BARRA_25=[]
BARRA_49=[]
BARRA_121=[]
for BARRA in [BARRA_single, BARRA_nine, BARRA_25, BARRA_49, BARRA_121]:
    _, BARRA = BARRA_daily_square(start_date=date(2012,1,1), end_date=date(2012,12,31), station_coords= (-37.6655, 144.8321), n=n, filename_stub = "/g/data3/w42/gt3409/accum_prcp-BARRA_R-v1-")
    print(f"for n = {n}, linregress = {linregress(station['prcp'], BARRA)}")
    n+=1

#for n = 0, correlation = SpearmanrResult(correlation=0.70107590944416698, pvalue=2.0792471258555171e-55)
#for n = 1, correlation = SpearmanrResult(correlation=0.71650275167585475, pvalue=6.8225331139784191e-59)
#for n = 2, correlation = SpearmanrResult(correlation=0.73304922484076029, pvalue=6.7453062525451973e-63)
#for n = 3, correlation = SpearmanrResult(correlation=0.75157974549611706, pvalue=9.3861088164207956e-68)
#for n = 4, correlation = SpearmanrResult(correlation=0.76483735376986806, pvalue=1.6825766663700728e-71)
#for n = 5, correlation = SpearmanrResult(correlation=0.77248407603347624, pvalue=8.9235347620197711e-74)
#for n = 6, correlation = SpearmanrResult(correlation=0.77567621765798556, pvalue=9.4220242385444488e-75)
#for n = 7, correlation = SpearmanrResult(correlation=0.77591563861751622, pvalue=7.9480745636591210e-75)


#for n = 0, linregress = LinregressResult(slope=0.87920118128890001, intercept=0.39513272809145783, rvalue=0.75333041080787511, pvalue=3.1006472986790332e-68, stderr=0.040229233651984504)
#for n = 1, linregress = LinregressResult(slope=1.0878308779585817, intercept=0.19274913037059216, rvalue=0.75341416634170411, pvalue=2.9399331402493376e-68, stderr=0.049762618549263164)
#for n = 2, linregress = LinregressResult(slope=1.1129881199104512, intercept=0.26246299857923572, rvalue=0.75927758952607582, pvalue=6.7094335878558021e-70, stderr=0.049999389577561851)
#for n = 3, linregress = LinregressResult(slope=1.0661064868617545, intercept=0.43685256636464898, rvalue=0.78287718852164379, pvalue=5.1421383727536473e-77, stderr=0.044408867329012253)
#for n = 4, linregress = LinregressResult(slope=1.0241882597345000, intercept=0.55750041623692836, rvalue=0.79264747733155261, pvalue=3.1512249768908491e-80, stderr=0.041290593794725217)
#for n = 5, linregress = LinregressResult(slope=0.99781463529634995, intercept=0.62952949708641559, rvalue=0.78983967951343792, pvalue=2.7494320658061915e-79, stderr=0.040610903994729615)
#for n = 6, linregress = LinregressResult(slope=0.98141512015773957, intercept=0.6760090724979797, rvalue=0.78520377933541163, pvalue=9.1495695147629397e-78, stderr=0.040567373275644934)
#for n = 7, linregress = LinregressResult(slope=0.95921659440428686, intercept=0.73131713241228846, rvalue=0.78118483850865872, pvalue=1.7811789276798574e-76, stderr=0.040179579376690581),

#for awap:

In [230]: n=0
AWAP_single=[]
AWAP_nine=[]
AWAP_25=[]
AWAP_49=[]
AWAP_121=[]
for AWAP_grid in [AWAP_single, AWAP_nine, AWAP_25, AWAP_49, AWAP
_121]:
    _, AWAP_grid = AWAP_daily_square(AWAP, AWAP_lats, AWAP_lons, AWAP_times, start_date=date(2012,1,1), end_date=date(2012,12,31), station_coords= (-37.6655, 144.8321), n=n)
    print(f"for n = {n}, correlation = {spearmanr(station['prcp'], AWAP_grid)}")
    n+=1


#for n = 0, correlation = SpearmanrResult(correlation=0.82132401332486105, pvalue=9.3869666036698279e-91)
#for n = 1, correlation = SpearmanrResult(correlation=0.8212888199971663, pvalue=9.6957962226628948e-91)
#/g/data3/hh5/public/apps/miniconda3/envs/analysis3-18.01/lib/python3.6/site-packages/numpy/lib/nanfunctions.py:66: UserWarning: Warning: converting a masked element to nan.
#  a = np.array(a)
#for n = 2, correlation = SpearmanrResult(correlation=0.80283379547424694, pvalue=9.104578933260777e-84)
#for n = 3, correlation = SpearmanrResult(correlation=0.7834062169153071, pvalue=3.4792071821630029e-77)
#for n = 4, correlation = SpearmanrResult(correlation=0.76200007302993056, pvalue=1.1177456701671779e-70)


#for n = 0, correlation = LinregressResult(slope=1.0291756500505866, intercept=0.34675965838830991, rvalue=0.90220260106231143, pvalue=5.368067562250256e-135, stderr=0.025788541062839208)
#for n = 1, correlation = LinregressResult(slope=1.1687110626647212, intercept=0.54026005740516925, rvalue=0.87250698985051456, pvalue=2.8809688812089606e-115, stderr=0.034303818003696356)
#/g/data3/hh5/public/apps/miniconda3/envs/analysis3-18.01/lib/python3.6/site-packages/numpy/lib/nanfunctions.py:66: UserWarning: Warning: converting a masked element to nan.
#  a = np.array(a)
#for n = 2, correlation = LinregressResult(slope=1.0969637752877062, intercept=0.60520237987753522, rvalue=0.84447989021195469, pvalue=9.7326906489321302e-101, stderr=0.036465529296329541)
#for n = 3, correlation = LinregressResult(slope=1.0250625715362573, intercept=0.62208153467937377, rvalue=0.80315280928471455, pvalue=6.999735441995107e-84, stderr=0.039854960098396265)
#for n = 4, correlation = LinregressResult(slope=0.92619527933830104, intercept=0.63713912195643685, rvalue=0.76849467562932705, pvalue=1.4080374955727909e-72, stderr=0.040419727249984674)



qqplot(AWS_data, BARRA_data)
plt.title("QQ BARRA vs AWS")
plt.xlabel("AWS")
plt.ylabel("BARRA")
plt.show()

qqplot(AWS_data, AWAP_data)
plt.title("QQ AWAP vs AWS")
plt.xlabel("AWAP")
plt.ylabel("AWS")
plt.show()

qqplot(AWAP_data, BARRA_data)
plt.title("QQ BARRA vs AWAP")
plt.xlabel("AWAP")
plt.ylabel("BARRA")
plt.show()


# Make maps of exceedence frequencies. 
# Start with mapping the number of wet days
threshold = 1.0 #mm                                          
# Load the 3D data (time, lats, lons) 
AWAP_3d, AWAP_lats, AWAP_lons, AWAP_times = get_AWAP()[0:366]
AWAP_times = AWAP_times[:366]
AWAP_3d = AWAP_3d[0:366,:,:]
# create a zeros array for each grid cell
AWAP_counts = np.zeros(AWAP_3d[0].shape)
# for each day
for day in range(len(AWAP_times)):
# for each lon
# for each lat
# if the value of the cell exceeds the threshold (and is less than an upper unrealistic amount), then update the cell count by one.
    AWAP_counts += (AWAP_3d[day] > threshold)&(AWAP_3d[day] < 900)

start_date = date(2012,1,1)
end_date = date(2012,12,31)
BARRA_2012 = []
i = 0
date_range = date_range(start_date, end_date)
for day in date_range:
    filename = f"/g/data3/w42/gt3409/BARRA_R/daily_prcp/accum_prcp-BARRA_R-v1-daily-{day.strftime('%Y%m%d')}.nc"
    BARRA_day_data = Dataset(filename, 'r')
    BARRA_2012.append(BARRA_day_data['prcp'])
BARRA_2012 = np.array(BARRA_2012) #this conversion is very slow

BARRA_counts = np.zeros(BARRA_2012[0].shape)
for day in range(len(date_range)):
    BARRA_counts += (BARRA_2012[day] > threshold)&(BARRA_2012[day] < 900)
map_BARRA(BARRA_counts, BARRA_day_data['lats'], BARRA_day_data['lons'], levels=levels['day']) 
plt.show()

