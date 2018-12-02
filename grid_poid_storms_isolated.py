import numpy as np
from scipy import ndimage


# green et al 2012 isolated storms, edited for high decrepancies, not interested in lower amounts
# calculate the mean of the neighbours for each point
# mask if this difference (value from mean) is greater than 25mm in magnitude
# find if at least 2 neighbours are close to the same difference from the neighbour mean:
# function for filtering: func(matrix) = sum((np.abs(mean-value)>25) & ((matrix-value) / ((mean-value)/2)>1) # or less than -1)

def filter_green(array):
    array = np.reshape(array, (3,3))
    # The central value
    value = array[1,1]
    # if the value isn't very high, don't bother with the checks
    if value < 25:
        return False
    # The neighbours
    neighbours = np.copy(array)
    neighbours[1,1] = np.nan
    # the mean value of the neighbours
    neighbour_mean = np.nanmean(neighbours)
    # is the value more than 25 more than the neighbour mean? T/F
    mean_diff_25 = (value - neighbour_mean)>25
    # for each neighbour, is its difference from value greater than half of the mean error?
    value_to_neighbour_diff = (value - neighbours) < (0.5 * (value - neighbour_mean))
    # Are there less than two also oddly big neighbours?
    less_than_2_big_neighbours = np.nansum(value_to_neighbour_diff)<2
    # is the value both 25mm more than neighbours mean and less than two friends
    grid_point_storm = mean_diff_25 * less_than_2_big_neighbours
    # returns 'True' if grid point strom is detected, 'False' if not
    return grid_point_storm

# Use
#data_set = prcp_data['BARRA_ann'][:]
#grid_point_storm_green = np.empty(data_set.shape)
#for i, data in enumerate(data_set):
#    grid_point_storm_green[i] = ndimage.generic_filter(data, filter_green, size = (3,3), mode = 'constant', cval = np.NaN)
    

def filter_green_modified(array):
    array = np.reshape(array, (3,3))
    # The central value
    value = array[1,1]
    # if the value isn't very high, don't bother with the checks
    if value < 50:
        return False
    # The neighbours
    neighbours = np.copy(array)
    neighbours[1,1] = 0
    # The max of the neighbours
    neighbour_max = np.nanmax(neighbours)
    # is the value more than 50 more than the neighbour max? T/F
    max_diff_50 = (value - neighbour_max)>50
    return max_diff_50











