#!/usr/bin/env python3

import folium
import math
import sys
from nearby_place import *
from circle import *
from google_api import *
from pathlib import Path

MAX_RESULTS_PER_PAGE = 20
MAX_RESULTS_PER_QUERY = 60
FOLIUM_COLORS = ["red", "blue", "green", "purple", "orange", "darkred", "lightred", "beige",
                 "darkblue", "darkgreen", "cadetblue", "darkpurple", "white", "pink", "lightblue",
                 "lightgreen", "gray", "black", "lightgray"]

'''
Computes coordinate with offset (source: https://stackoverflow.com/questions/7477003/calculating-new-longitude-latitude-from-old-n-meters)
'''
def move_lat_long_by_distance(center_y, center_x, dy, dx):
    r_earth = 6378100.0
    new_latitude  = center_y + (dy / r_earth) * (180 / math.pi);
    new_longitude = center_x + (dx / r_earth) * (180 / math.pi) / math.cos(center_y * math.pi/180);
    return (new_latitude, new_longitude)

'''
Return four intersecting circles covering the area of the input circle
'''
def get_subcircles(center_x, center_y, radius):
    circles = []

    first_quadrant_center = move_lat_long_by_distance(center_y, center_x, (radius / 2), (radius / 2))
    circles.append(Circle(first_quadrant_center[1], first_quadrant_center[0], radius / math.sqrt(2)))

    second_quadrant_center = move_lat_long_by_distance(center_y, center_x, (radius / 2), -(radius / 2))
    circles.append(Circle(second_quadrant_center[1], second_quadrant_center[0], radius / math.sqrt(2)))

    third_quadrant_center = move_lat_long_by_distance(center_y, center_x, -(radius / 2), -(radius / 2))
    circles.append(Circle(third_quadrant_center[1], third_quadrant_center[0], radius / math.sqrt(2)))

    fourth_quadrant_center = move_lat_long_by_distance(center_y, center_x, -(radius / 2), (radius / 2))
    circles.append(Circle(fourth_quadrant_center[1], fourth_quadrant_center[0], radius / math.sqrt(2)))

    return circles

'''
Returns a function used to return Google Place search results while plotting searches on a map
'''
def query_nearby_places(folium_map=None, uber_radius=None):
    api = GoogleAPI()
    def execute_and_map(r, lat, long):
        results = api.get_valid_results("bar", r, lat, long)

        # Show progress for long execution times
        print(f"found: {str(len(results))} results with radius of {str(r)} meters")

        if folium_map:
            # For each recursive level, associate a unqiue color with the circle and bar markers
            nested_color = "cadetblue"
            if uber_radius:
                nested_level = int(math.log(uber_radius / r, math.sqrt(2)))
                nested_color = FOLIUM_COLORS[nested_level % len(FOLIUM_COLORS)]

            # Plot search circle and bar markers (markers only when space has been exhausted)
            circle = folium.Circle(radius=r, location=[lat, long], color=nested_color, fill=True).add_to(folium_map)
            if len(results) < MAX_RESULTS_PER_QUERY:
                for entry in results:
                    coordinate = entry.coordinate
                    folium.Marker( # todo: this is also excessive and repeatedly plots certain places
                        location=[coordinate.latitude, coordinate.longitude], 
                        popup=entry.name,
                        icon=folium.Icon(color=nested_color, icon="none")
                    ).add_to(folium_map)

        return results

    return execute_and_map

'''
Recursively searches the physical space until all locations are uncovered
params: initial circle, function to extract places from circle, function to compute sub-problems
'''
def search_area(center_x, center_y, radius, get_results, compute_subproblems):
    discovered_places = {}

    initial_results = get_results(radius, center_y, center_x)
    if len(initial_results) < MAX_RESULTS_PER_QUERY:
        for elem in initial_results:
            discovered_places[elem.place_id] = elem
    elif len(initial_results) == MAX_RESULTS_PER_QUERY:
        sub_circles = compute_subproblems(center_x, center_y, radius)
        for circle in sub_circles:
            results = search_area(circle.center_x, circle.center_y, circle.radius, get_results, compute_subproblems)
            discovered_places.update(results)

    return discovered_places


if __name__ == "__main__":
    # Collect command line arguments
    try:
        argumentList = sys.argv[1:]
        latitude = float(argumentList[0])
        longitude = float(argumentList[1])
        radius = float(argumentList[2])
        center = (latitude, longitude)
    except err:
        print(f"Failed while parsing arguments: {str(err)}")
        sys.exit(0)

    map = folium.Map(
        location=[center[0], center[1]],
        zoom_start=13
    )

    results = search_area(center[1], center[0], radius, query_nearby_places(map, radius), get_subcircles)
    print(f"Total places found: {str(len(results))}")

    # Create directory containing map.html & place_ids.txt for this run
    dir_name = f"out/Bars_{center[0]}_{center[1]}_{int(radius)}m"
    Path(dir_name).mkdir(parents=True, exist_ok=True)

    # Write place_id's for input to popular times
    with open(f"{dir_name}/place_ids.txt", "w") as place_ids:
        for entry in results:
            print(results[entry].name)
            place_ids.write(f"{results[entry].place_id}\n")

    # Write map for visualization of bars found
    print(f"Writing {dir_name}/map.html to disk ...")
    map.save(f"{dir_name}/map.html")
    print("Done")
