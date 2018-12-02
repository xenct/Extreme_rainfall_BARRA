## Rain indices:
# RR
# Precipitation sum (mm) of rain above 1mm in a day
import numpy as np

def rr(data, threshold = 1):
    """Precipitation sum (mm)
sets rainfall totals less than 1mm to NaN, then sums the total rainfall from these wet days"""
    wet_days = data
    wet_days[data < threshold] = np.nan
    data_rr = np.nansum(wet_days, 0)
    return data_rr

def rr1(data, threshold = 1):
    """Wet days count (RR ≥ 1 mm) (days)
Sets rainfall totals less than 1mm to NaN, then counts the wet days"""
    data_rr1 = np.nansum(data > threshold, 0)
    return data_rr1

def sdii(data, threshold = 1):
    """Simple daily intensity index (mm/wet day)"""
    data_rr1 = rr1(data)
    data_rr = rr(data)
    data_sdii = data_rr / data_rr1
    return data_sdii

def cwd(data, threshold = 1):
    """Maximum number of consecutive wet days (RR ≥ 1 mm) (days)"""
    wet_data = data
    wet_days = 1*(wet_data > threshold) # yes/no is the day wet??
    cwd = wet_days[0] #start at the first days to count the cumulative days
    cwd_max = cwd
    for n in range(len(wet_days)-1):
        # is n day wet AND n+1 day wet?
        t0 = wet_days[n]
        t1 = wet_days[n+1]
        # Add the consecutive wet days
        cwd = (cwd + 1)* t0*(t0==t1)
        # When this wet spell exceeds the max historical wet spell, update the maximum record 
        cwd_max[cwd_max<cwd] = cwd[cwd_max<cwd]
    return cwd_max

def cdd(data, threshold = 1):
    """Maximum number of consecutive wet days (RR ≥ 1 mm) (days)"""
    dry_data = data
    np.isnan(dry_data)
    dry_days = 1*(dry_data < threshold) # yes/no is the day wet??
    cdd = dry_days[0] #start at the first days to count the cumulative days
    cdd_max = cdd
    for n in range(len(dry_days)-1):
        # is n day wet AND n+1 day wet?
        t0 = dry_days[n]
        t1 = dry_days[n+1]
        # Add the consecutive wet days
        cdd = (cdd + 1)* t0*(t0==t1)
        # When this wet spell exceeds the max historical wet spell, update the maximum record 
        cdd_max[cdd_max<cdd] = cdd[cdd_max<cdd]
    return cdd_max


def r10mm(data):
    """Heavy precipitation days (precipitation ≥ 10 mm) (days)"""
    data_r10mm = np.nansum(data >= 10, 0)
    return data_r10mm

def r20mm(data):
    """Very heavy precipitation days (precipitation ≥ 20 mm) (days)"""
    data_r20mm = np.nansum(data >= 20, 0)
    return data_r20mm

def rnnmm(data, nn = 50):
    """Precipitation days above threshold (precipitation ≥ nn mm) (days)"""
    data_rnnmm = np.nansum(data >= nn, 0)
    return data_rnnmm

def rx1day(data):
    """Highest 1-day precipitation amount (mm)"""
    return np.nanmax(data, 0)

import xarray as xr
def rx5day(data):
    """Highest 5-day precipitation amount (mm)"""
    # make the data into an xarray    
    da = xr.DataArray(data, dims=['time', 'lats', 'lons']).fillna(0)
    # cumulative 5 day totals centred
    r5day = da.rolling(time = 5).sum()
    data_rx5day = np.nanmax(r5day,0) #sum the 5 frame rolling window
    return data_rx5day

def prcptot(data, threshold = 1):
    """Total precipitation amount from precipitation days above 1mm (mm)"""
    data[data < threshold] = 0
    prcptot = np.nansum(data, 0)
    return prcptot

def r75p(data, ref_data, threshold = 1):
    """Days with RR > 75th percentile of daily amounts (moderate wet days)
(days)
    ie count of days with rainfall exceeding the reference period 75th percentile rainfall for wet days, where a wet day has at least 1mm of precipitation"""
    ref_wet_days = ref_data
    ref_wet_days[ref_data < threshold] = np.nan # don't count the dry days 
    ref_75p = np.nanpercentile(ref_wet_days, 75, 0) # this array is the valuse of the 75th percentile on wet days
    data_r75p = np.sum(data > ref_75p, 0)
    return data_r75p

def r75ptot(data, ref_data, threshold = 1):
    """Precipitation fraction due to moderate wet days (> 75th percentile) (%)"""
    ref_wet_days = ref_data
    ref_wet_days[ref_data < threshold] = np.nan # don't count the dry days 
    ref_75p = np.nanpercentile(ref_wet_days, 75, 0) # this array is the value of the 75th percentile on wet days
    data_r75ptot = np.nansum((data*[data > ref_75p])[0], 0)
    data_r75ptot[data_r75ptot < 1] = 0.001 # avoid division by zero, set zero to 0.1
    data_prcptot = prcptot(data)
    data_prcptot[data_prcptot < 1] = 0.1 # avoid division by zero, set zero to 0.1
    data_r75pprop = 100 * data_r75ptot / data_prcptot
    return data_r75pprop

def r95p(data, ref_data, threshold = 1):
    """Days with RR > 95th percentile of daily amounts (moderate wet days)
(days)
    ie count of days with rainfall exceeding the reference period 95th percentile rainfall for wet days, where a wet day has at least 1mm of precipitation"""
    ref_wet_days = ref_data
    ref_wet_days[ref_data < threshold] = np.nan # don't count the dry days 
    ref_95p = np.nanpercentile(ref_wet_days, 95, 0) # this array is the value of the 95th percentile on wet days
    data_r95p = np.sum(data > ref_95p, 0)
    return data_r95p

def r95ptot(data, ref_data, threshold = 1):
    """Precipitation fraction due to moderate wet days (> 95th percentile) (%)"""
    ref_wet_days = ref_data
    ref_wet_days[ref_data < threshold] = np.nan # don't count the dry days 
    ref_95p = np.nanpercentile(ref_wet_days, 95, 0) # this array is the value of the 95th percentile on wet days
    data_r95ptot = np.nansum((data*[data > ref_95p])[0], 0)
    data_r95ptot[data_r95ptot < 1] = 0.001 # avoid division by zero, set zero to 0.1
    data_prcptot = prcptot(data)
    data_prcptot[data_prcptot < 1] = 0.1 # avoid division by zero, set zero to 0.1
    data_r95pprop = 100 * data_r95ptot / data_prcptot
    return data_r95pprop

def r99p(data, ref_data, threshold = 1):
    """Days with RR > 99th percentile of daily amounts (moderate wet days)
(days)
    ie count of days with rainfall exceeding the reference period 99th percentile rainfall for wet days, where a wet day has at least 1mm of precipitation"""
    ref_wet_days = ref_data
    ref_wet_days[ref_data < threshold] = np.nan # don't count the dry days 
    ref_99p = np.nanpercentile(ref_wet_days, 99, 0) # this array is the valuse of the 99th percentile on wet days
    data_r99p = np.sum(data > ref_99p, 0)
    return data_r99p

def r99ptot(data, ref_data, threshold = 1):
    """Precipitation fraction due to moderate wet days (> 99th percentile) (%)"""
    ref_wet_days = ref_data
    ref_wet_days[ref_data < threshold] = np.nan # don't count the dry days 
    ref_99p = np.nanpercentile(ref_wet_days, 99, 0) # this array is the value of the 99th percentile on wet days
    data_r99ptot = np.nansum((data*[data > ref_99p])[0], 0)
    data_r99ptot[data_r99ptot < 1] = 0.001 # avoid division by zero, set zero to 0.1
    data_prcptot = prcptot(data)
    data_prcptot[data_prcptot < 1] = 0.1 # avoid division by zero, set zero to 0.1
    data_r99pprop = 100 * data_r99ptot / data_prcptot
    return data_r99pprop



