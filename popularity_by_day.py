#!/usr/bin/env python3

import math
import sys
import numpy as np
import matplotlib.pyplot as plt
from google_api import *
from matplotlib.ticker import FuncFormatter
from pathlib import Path

DAYS = [ "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday" ]
MIN_POPULARITY_THRESHOLD = 60

# Search hours after 9pm (filter out happy hours, dinner times, peaks from the night before (12-2am))
def get_peak_popularity(day_data):
    nine_o_clock = 9
    pm_offset = 12
    begin_time = nine_o_clock + pm_offset
    return max(day_data[begin_time:])

# Display human readable am/pm times on x-axis
def reformat_military_time(x, pos):
    hour_map = {
        0: "12am",
        23: "11pm",
        8: "8am",
        15: "3pm"
    }
    if x in hour_map:
        return hour_map[x]
    else:
        return ""

if __name__ == "__main__":
    # Collect command line arguments
    try:
        # Get path to place id's file
        argumentList = sys.argv[1:]
        input_path = Path(argumentList[0])
    except err:
        print(f"Failed while parsing arguments: {str(err)}")
        sys.exit(0)

    # Read place_id's from file
    place_ids = []
    with open(input_path) as input_file:
        place_ids = [ line.rstrip() for line in input_file ]

    # Build map from place_id to { popular_times, name }
    popularity_map = {}
    api = GoogleAPI()
    for place_id in place_ids:
        result = api.get_popular_times(place_id)
        if "populartimes" in result and "name" in result:
            # Show progress for long runtimes
            print(f"received popular times data for {result['name']}")

            popularity_map[place_id] = {
                "popular_times": result["populartimes"],
                "name": result["name"]
            }

    top_bars_per_day = {}
    for day in DAYS:
        top_bars_per_day[day] = []
    
    # todo: add more print statements denoting progress?

    # For each bar, find peak occupancy for each day, add tuple to list for the day
    for (place_id, data) in popularity_map.items():
        week_data = data["popular_times"]
        place_name = data["name"]
        for day_data in week_data:
            day_name = day_data["name"]
            peak_popularity = get_peak_popularity(day_data["data"])
            if peak_popularity > MIN_POPULARITY_THRESHOLD:
                top_bars_per_day[day_name].append({ 
                    "place": place_name,
                    "peak_popularity": peak_popularity,
                    "hourly_popularity": day_data["data"]
                })

    # Sort day's bars, highest first
    for day in top_bars_per_day:
        popular_bars = top_bars_per_day[day]
        day_sorted = sorted(popular_bars, reverse=True, key=lambda obj: obj["peak_popularity"])
        top_bars_per_day[day] = day_sorted

    # Create sub-directory for plots
    dir_name = f"{str(input_path.parent)}/top_daily"
    Path(dir_name).mkdir(parents=True, exist_ok=True)
    print(f"Drawing plots to {dir_name} ...")

    # Plot the top bars for each day
    for day in top_bars_per_day:
        # Determine number of plots to be placed in grid, max 36
        num_daily_bars = len(top_bars_per_day[day])
        if num_daily_bars > 36:
            num_daily_bars = 36
        plot_side_length = math.ceil(math.sqrt(num_daily_bars))

        formatter = FuncFormatter(reformat_military_time)
        fig, ax = plt.subplots(figsize=(14,10))
        ax.xaxis.set_major_formatter(formatter)

        index = 1
        for bar in top_bars_per_day[day][:num_daily_bars]:
            ax = plt.subplot(plot_side_length, plot_side_length, index)
            ax.xaxis.set_major_formatter(formatter)

            # Set boundaries for bar chart
            x_axis_begin = 0
            x_axis_end = 24

            # Set y-axis to range of [0, 100]
            axes = plt.gca()
            axes.set_ylim([0, 100])

            plt.bar(np.arange(x_axis_begin, x_axis_end), bar["hourly_popularity"][x_axis_begin:x_axis_end])
            plt.xticks(np.arange(x_axis_begin, x_axis_end, 1))
            plt.title(bar["place"])

            index += 1

        plt.subplots_adjust(wspace=0.4, hspace=0.9)
        fig.suptitle(day, fontsize=16)

        print(f"saving {day}.png")
        plt.savefig(f"{dir_name}/{day}.png")

    print("Done")
