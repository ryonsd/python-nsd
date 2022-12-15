# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import datetime
from math import sin, cos, radians, sqrt, asin

# GIS
from pyproj import Proj
from sympy.geometry import Point, Polygon
import folium
import osmnx

# matplotilib
import matplotlib as mpl
import matplotlib.pyplot as plt
import branca.colormap


#--============================================================
#++

"""
- dataframe
- datatime
- GIS
- visualization
- distance

"""





"""
description

Parameters
---------


Returns
---------


Examples
---------

"""


#--============================================================
#++
## class for pandas

#-------------------------------------------------------------------
#++
## 
def concat_from_df_paths(data_paths):
    """
    create concted dataframe from data paths

    Parameters
    --------
    data_paths : paths to data

    Return
    --------
    pandas.core.frame.DataFrame

    """
    df = pd.DataFrame()
    for p in data_paths:
        df_ = pd.read_csv(p)
        df = pd.concat([df, df_])
    return df


#--============================================================
#++
## class for datetime

#-------------------------------------------------------------------
#++
## freq の間隔でstartからendまでの時刻を生成する
def datetime_index(start, end, freq='S'):
    """
    create index of time
    
    Prameters
    --------
    start : str
    end : str
    freq : hour->'H', second->'S'
    
    Returns
    --------
    pandas.core.frame.DataFrame
        dataframe of time 
        
    Examples
    --------    
    >>> datetime_index("18:00", "22:00", freq="H")
    >>>        time
        0  18:00:00
        1  19:00:00
        2  20:00:00
        3  21:00:00
        4  22:00:00
    
    """

    dtime = pd.date_range(start=start, end=end, freq=freq)
    time = []
    for i in range(dtime.shape[0]):
        time.append(dtime[i].time())
    df = pd.DataFrame({"time":time})
    return df

#-------------------------------------------------------------------
#++
## 
def int2time(data, time):
    """
    convert 180000 to 18:00:00 for all data
    
    Prameters
    --------
    data : pandas.dataframe
    time : column's name (str)
    
    Returns
    --------
    time: datatime
    
    """
    for i in range(data.shape[0]):
        data[time][i] = datetime.datetime.strptime(str(data[time][i]), '%H%M%S').time()
        
    return data


#--============================================================
#++
## class for GIS

#-------------------------------------------------------------------
#++
## 
def get_geojson_grid(upper_right, lower_left, n=6):
    """
    Returns a grid of geojson rectangles, and computes the exposure in each section of the grid based on the vessel data.
    右上と左下の緯度経度を入れると，n個に分割されたメッシュの右上と左下および四角の緯度経度情報を算出

    Parameters
    ----------
    upper_right: array_like
        The upper right hand corner of "grid of grids" (the default is the upper right hand [lat, lon] of the USA).

    lower_left: array_like
        The lower left hand corner of "grid of grids"  (the default is the lower left hand [lat, lon] of the USA).

    n: integer
        The number of rows/columns in the (n,n) grid.

    Returns
    -------

    list
        List of "geojson style" dictionary objects   
    """

    all_boxes = []

    lat_steps = np.linspace(lower_left[0], upper_right[0], n+1)
    lon_steps = np.linspace(lower_left[1], upper_right[1], n+1)

    lat_stride = lat_steps[1] - lat_steps[0]
    lon_stride = lon_steps[1] - lon_steps[0]

    for lat in lat_steps[:-1]:
        for lon in lon_steps[:-1]:
            # Define dimensions of box in grid
            upper_left = [lon, lat + lat_stride]
            upper_right = [lon + lon_stride, lat + lat_stride]
            lower_right = [lon + lon_stride, lat]
            lower_left = [lon, lat]

            # Define json coordinates for polygon
            coordinates = [
                upper_left,
                upper_right,
                lower_right,
                lower_left,
                upper_left
            ]

            geo_json = {"type": "FeatureCollection",
                        "properties":{
                            "lower_left": lower_left,
                            "upper_right": upper_right
                        },
                        "features":[]}

            grid_feature = {
                "type":"Feature",
                "geometry":{
                    "type":"Polygon",
                    "coordinates": [coordinates],
                }
            }

            geo_json["features"].append(grid_feature)

            all_boxes.append(geo_json)

    return all_boxes

#-------------------------------------------------------------------
#++
## 
def is_point_in_area(point, area):
    """
    judge wheter a point is in area or not

    Parameters
    ---------
    point: [lat, lon]

    area: [[lat, lon], [lat, lon], ...]

    Returns
    ---------
    bool

    """

    area = Polygon(*area)
    point = Point(point)
    return area.encloses_point(point)

#-------------------------------------------------------------------
#++
## 
def count_number_of_points_on_grid(df, lat, lon, upper_right, lower_left, grid_size):
    """
    count the number of points in mesh from dataframe

    Parameters
    ---------
    df: pandas.dataframe

    lat: str
        column name of latitude of dataframe
    lon: str
        column name of loongitude of dataframe

    upper_right: array [lat, lon]
        upper right coordinates of area

    lower_left: array [lat, lon]
        lower left coordinates of area

    grid_size: int

    Returns
    ---------

    """
    
    # Creating a grid of nxn from the given cordinate corners     
    grid = get_geojson_grid(upper_right, lower_left , grid_size)
    # Holds number of points that fall in each cell & time window if provided
    counts_array = []
    
    # Adding the total number of visits to each cell
    for box in grid:
        # get the corners for each cell
        upper_right = box["properties"]["upper_right"]
        lower_left = box["properties"]["lower_left"]
        # check to make sure it's in the box and between the time window if time window is given 
        mask = ((df[lat] <= upper_right[1]) & (df[lat] >= lower_left[1]) &
            (df[lon] <= upper_right[0]) & (df[lon] >= lower_left[0]))
        # Number of points that fall in the cell and meet the condition 
        counts_array.append(len(df[mask]))
    
    return counts_array


#-------------------------------------------------------------------
#++
## 
def polygon2graph(polygon):
    """
    retrun graph of OSM of polygon area

    Parameters
    ---------
    polygon: list
        list of coordinates [[lon, lat], [lon, lat], ...]
        note*: add coordinates same as first one at last 

    Returns
    ---------
        graph

    Examples
    ---------
    """
    polygon = Polygon(polygon)
    cf = '["highway"~"trunk|primary|primary_link|secondary|tertiary|tertiary_link|unclassified|residential|service|living_street"]'
    G = osmnx.graph.graph_from_polygon(polygon, custom_filter=cf, simplify=False, network_type="drive_service")
    return G



#--============================================================
#++
## class for Folium
def plot_latlon(df, center, vis_type, zoom=10):
    """
    visualize trajectories of trajectory
    
    Prameters
    --------
    df: pandas.dataframe
        trajectory(lat, lon)
    
    center: array
        center's coordinate of map
    
    vis_type: str
        "route", "point"

    zoom: int
    
    Results
    -------

    """
    m = folium.Map(location=center, tiles='OpenStreetMap', zoom_start=zoom)

    if vis_type == "route":
        # Makers
        folium.Marker(
            location=np.array(df.loc[0,['lat', 'lon']]), 
            popup='Start',
            icon=folium.Icon(color='blue')
        ).add_to(m)

        # Route
        locations = []
        for i in range(len(df)):
            locations.append([df.iloc[i].lat, df.iloc[i].lon])
        line = folium.PolyLine(locations=locations, weight=2, color='blue')
        m.add_child(line)
        m.add_child(folium.LatLngPopup())

    elif vis_type == "point":
        for i in range(len(df)):
            folium.Marker([df.iloc[i].lat, df.iloc[i].lon]).add_to(m)

    return m

#-------------------------------------------------------------------
#++
## 
def plot_number_of_points_on_grid(df, lat, lon, center_location, upper_right, lower_left, grid_size, max_n, c="green"):
    """
    description

    Parameters
    ---------


    Returns
    ---------

    """

    m = folium.Map(location=center_location,tiles='cartodbpositron', control_scale=True, zoom_start=14)

    grid = get_geojson_grid(upper_right, lower_left , grid_size)
    counts_array = count_number_of_points_on_grid(df, lat, lon, upper_right, lower_left, grid_size)
    
    print("max number of data", max(counts_array))
    # Add GeoJson to map
    for i, geo_json in enumerate(grid):
        relativeCount = counts_array[i] / max_n
        if c == "green":
            color = plt.cm.Greens(relativeCount)
        elif c == "red":
            color = plt.cm.Reds(relativeCount)
        color = mpl.colors.to_hex(color)
        if relativeCount == 0:
            color = "white"
        gj = folium.GeoJson(geo_json,
                style_function=lambda feature, color=color: {
                    'fillColor': color,
                    'color':"gray",
                    'weight': 0.5,
                    'dashArray': '6,6',
                    'fillOpacity': 0.8,
                })
        m.add_child(gj)
    
    if c == "green":
        colormap = branca.colormap.linear.Greens_09.scale(0, max_n)
    elif c == "red":
        colormap = branca.colormap.linear.Reds_09.scale(0, max_n)
    colormap = colormap.to_step(index=np.arange(0, max_n+1, 10))
    # colormap.caption = 'Number of demand (orign)'
    
    colormap.add_to(m)
    return m

#--============================================================
#++
## class for distance

#-------------------------------------------------------------------
#++
## 
def dist_on_sphere(pos0, pos1, radius=6378.137):
    """
    description

    Parameters
    ---------


    Returns
    ---------

    """
    latang1, lngang1 = pos0
    latang2, lngang2 = pos1
    phi1, phi2 = radians(latang1), radians(latang2)
    lam1, lam2 = radians(lngang1), radians(lngang2)
    term1 = sin((phi2 - phi1) / 2.0) ** 2
    term2 = sin((lam2 - lam1) / 2.0) ** 2
    term2 = cos(phi1) * cos(phi2) * term2
    wrk = sqrt(term1 + term2)
    wrk = 2.0 * radius * asin(wrk) 
    return wrk # km

#-------------------------------------------------------------------
#++
## 
def dist_manhattan(p0, p1):
    """
    description

    Parameters
    ---------


    Returns
    ---------

    """
    pos0 = p0
    pos_ = [p0[0], p1[1]]
    pos1 = p1
    lat_dist = dist_on_sphere(pos0, pos_)
    lon_dist = dist_on_sphere(pos1, pos_)
    return lat_dist + lon_dist
