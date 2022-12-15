import pandas as pd
import geopy
import geopy.distance

from datetime import date


def stay_point_detection(data, distance_threshold, time_threshold):

    B_ = data.date_time[1:]
    B = B_.reset_index(drop=True)
    A = pd.DataFrame({'start': data.date_time})
    Data = pd.concat([A, B], axis=1)
    Data.columns = ['start', 'arrive']

    # calculate timespan
    timespan = []
    for i in range(len(Data)-1):
        t1 = Data.loc[i, 'start']
        t2 = Data.loc[i, 'arrive']
        t = t2 - t1
        timespan.append(t)

    timespan.append(0)
    Data['timespan'] = timespan

    # calculata distance between two points
    distance = []
    for i in range(len(Data)-1):
        p1 = geopy.Point(data.loc[i, 'lat'], data.loc[i, 'lon'])
        p2 = geopy.Point(data.loc[i+1, 'lat'], data.loc[i+1, 'lon'])
        dist = geopy.distance.distance(p1, p2).m
        distance.append(dist)

    distance.append(0)
    Data['distance'] = distance

    # count stay points
    count = 0
    x = []
    for i in range(len(Data)-1):
        if Data.loc[i, 'distance'] < distance_threshold:
            if Data.loc[i, 'timespan'] > pd.Timedelta(minutes = time_threshold):
                count = count + 1
                x.append(i)

    #print('count=',  count)

    # calculate stay point coordinate, arrive time, leave time
    if count == 0:
        return 0

    if count != 0:
        s_lat = []
        s_lon = []
        s_alt = []
        s_date = []
        for i in range(len(x)):
            s_lat_1 = data.loc[x[i], 'lat']
            s_lat_2 = data.loc[x[i]+1, 'lat']
            s_lon_1 = data.loc[x[i], 'lon']
            s_lon_2 = data.loc[x[i]+1, 'lon']
            s_alt_1 = data.loc[x[i], 'alt']
            s_alt_2 = data.loc[x[i]+1, 'alt']
            s_date_ = data.loc[x[i], 'date']

            s_lat.append((s_lat_1 + s_lat_2) / 2)
            s_lon.append((s_lon_1 + s_lon_2) / 2)
            s_alt.append((s_alt_1 + s_alt_2) / 2)
            s_date.append(s_date_)

        S___ = pd.DataFrame(Data.loc[x])
        S__ = S___.reset_index(drop=True)
        S_ = S__.drop('distance', axis=1)
        S = S_.rename(columns={'start': 'arrive', 'arrive': 'leave'})
        S['lat'] = s_lat
        S['lon'] = s_lon
        S['altitude'] = s_alt
        S['weekday'] = S['arrive'].dt.dayofweek
        S['date'] = s_date

    return S
