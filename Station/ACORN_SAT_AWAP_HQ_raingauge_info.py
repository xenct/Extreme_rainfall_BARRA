# get the site location for the HQ raingauge network
# download .json file from http://lab.environment.data.gov.au/data/acorn/climate/slice.json

import json 

# read in and view the file
from pprint import pprint
with open('Documents/Project/ACORN_SAT_locations.json') as f:  
    data = json.load(f)
pprint(data)                                                    

# store the info in a sensible format
hq_stations = {}
for site in range(112): 
     site_number = data['result']['items'][site]['observedBy']['currentSite']['_about'][-6:]
     site_lat = float(data['result']['items'][site]['observedBy']['currentSite']['lat'])
     site_lon = float(data['result']['items'][site]['observedBy']['currentSite']['long'])
     hq_stations[site_number] = (site_lat, site_lon)

# write to csv
import csv
w = csv.writer(open('Documents/Project/ACORN_SAT_site_locations.csv', 'w'))
w.writerow(['ID','lat','lon']) # write the header
for key, val in hq_stations.items():
    w.writerow([str(key),val[0], val[1]])

