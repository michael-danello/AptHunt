import json
import time

import overpy
from osmQueries import BUILDINGS, BUILDINGS_BY_SUBWAY
from landmarks import L_LINE

api = overpy.Overpass()
building_dict = {}

def get_buildings_by_subway(subway_name, subway_loc):
    query = BUILDINGS_BY_SUBWAY.format(subway_loc[0],subway_loc[1],subway_loc[0],subway_loc[1])
    result = api.query(query).ways
    return result

def update_building_dict(building_dict, buildings, subway_stop):
    """
    generate addresses from the lowest to the highest address
    """

    street_dict = {}
    start = time.time()

    for building in [building.tags for building in buildings]:

        street = building.get('addr:street')
        address = building.get('addr:housenumber')

        if address != None and street != None:

            try:
                address = int(address)

            except ValueError:
                continue

            if street_dict.get(street) == None:
                street_dict[street] = [address]

            else:
                street_dict[street].append(address)

    # OSM may not record all buildings in a street. generate addresses from
    # minimum to maximum address on a given street
    for building in street_dict:

        min_add = min(street_dict[building])
        max_add = max(street_dict[building]) + 1
        street_dict[building] = list(range(min_add,max_add))

        for address in street_dict[building]:

            address = str(address) + " " + building

            # create building object if it does not already exist
            if building_dict.get(address) == None:

                url_address = address.replace(" ","-")
                street_easy_url = "https://streeteasy.com/building/"
                borough = "-brooklyn"
                url = f"{street_easy_url}{url_address}{borough}"

                building_dict[address] = {
                    'address':address,
                    'url':url,
                    'scraped':False,
                    'subwayStop':subway_stop
                }


    # Add all these addresses to
    end = time.time()
    print(f"{len(building_dict)} buildings returned in {round(end-start,3)} seconds")


def add_buildings_by_stop(stop, location):
    buildings_by_stop = get_buildings_by_subway(stop, location)
    update_building_dict(building_dict, buildings_by_stop, stop)

for stop, location in L_LINE.items():
    add_buildings_by_stop(stop, location)

with open("building.json", "w") as buildings:
    json.dump(building_dict, buildings)
