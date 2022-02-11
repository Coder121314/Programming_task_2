"""
the module creates a map
with the closest to the user locations
where films of a certain year were made
"""
import argparse
import re
from math import sqrt, sin, cos, asin, radians
from geopy.geocoders import Nominatim, ArcGIS
from geopy.extra.rate_limiter import RateLimiter
from geopy.distance import geodesic
import folium




def coordinates_def(adress:str):
    """
    function uses geocoders to find the coordinates
    of given location
    >>> int(coordinates_def('Stage 2, Warner Brothers\
         Burbank Studios - 4000 Warner Boulevard, Burbank, California, USA')[0])
    34
    >>> coordinates_def('')
    >>> int(coordinates_def('Bad Hersfeld, Hessen, Germany')[0])
    50
    >>> int(coordinates_def('Bad Hersfeld, Hessen, Germany')[1])
    9
    >>> coordinates_def('Bad Hersfeld, Hessen, Germany')
    (50.86952000000008, 9.712830000000054)

    """
    try:
        geolocator = ArcGIS(user_agent='_')
        geocode_function = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        location = geocode_function(adress)
        if location is not None:
            return (location.latitude, location.longitude)
        else:
            geolocator = Nominatim(user_agent='_')
            location = geolocator.geocode(adress)
            if location is not None:
                return (location.latitude, location.longitude)
    except Exception:
        return None



def distance_def(coord_1:tuple, coord_2:tuple):
    """
    function defines the distance between two points    # (latitude; longitude)
    >>> int(distance_def((0,15),(15,0)))
    2345
    >>> int(distance_def((0,0),(0,0)))
    0
    >>> int(distance_def((10,344),(15,98)))
    12231
    >>> int(distance_def((1,34.1),(75,8)))
    8402
    >>> distance_def((1,34.1),(75,8))
    8402.65873069945
    """
    rad_ls = []
    for coord in [coord_1, coord_2]:
        rad_ls.append((radians(coord[0]), radians(coord[1])))
    return 2*6371*asin(sqrt((sin((rad_ls[1][0] - rad_ls[0][0])/2))**2 + \
        cos(rad_ls[0][0])*cos(rad_ls[1][0])*(sin((rad_ls[1][1] - rad_ls[0][1])/2))**2 ))



def generate_map(points_ls:list, start_latitude, start_longitude, year):
    """
    function generates the map for the points given;
    there can be in range of 1-10 points on the map;
    there are 4 layers:
        --- the main one (the map itself)
        --- the mark layer (depicts points from list)
        --- the layer that shows how many times the creation of the film
            repeated in the location
        --- the layer that shows the route between the location points
    """
    def color_def(filming_attempts):
        """
        function defines the color of
        a circle marker for the map
        >>> color_def(4)
        'red'
        >>> color_def(1)
        'orange
        """
        if filming_attempts < 2:
            return "orange"
        elif 2 <= filming_attempts <= 10:
            return "red"
        else:
            return "darkred"
    the_map = folium.Map(location=[start_latitude, start_longitude], zoom_start=1.5)
    html = """<h4>Film information:</h4>
    Film name: {},<br>
    The distance : {}
    """
    fg_list = []

    fg1 = folium.FeatureGroup(name=f'mark layer for {year}')
    fg2 = folium.FeatureGroup(name='color indicators of filming attempts')
    fg3 = folium.FeatureGroup(name='the route between the filming places')
    for elem in points_ls:
        iframe = folium.IFrame(html=html.format(elem[1], elem[0]),
        width=300,
        height=100)

        fg2.add_child(folium.CircleMarker(location=[elem[3][0], elem[3][1]],
                    radius=20,
                    popup=f"{elem[1]} had {elem[2]} filming attempt(s)",
                    fill_color=color_def(elem[2]),
                    color='black',
                    fill_opacity=70))

        fg1.add_child(folium.Marker(location=[elem[3][0], elem[3][1]],
        popup=folium.Popup(iframe),
        icon=folium.Icon(color = "red")))

        fg3.add_child(folium.PolyLine(list(map(lambda x: x[3], points_ls)),
        color="darkblue", weight=2.5, opacity=1))

    fg_list.append(fg1)
    fg_list.append(fg2)
    fg_list.append(fg3)
    for fg_elem in fg_list:
        the_map.add_child(fg_elem)
    the_map.add_child(folium.LayerControl())
    the_map.save('Film_map.html')


def main():
    """
    the main part of the program
    takes 4 arguments from the user:
    1) year
    2) latitude
    3) longitude
    4) dataset path
    uses the previous functions to get the result
    """
    parser = argparse.ArgumentParser(description='The use of argparse:')
    parser.add_argument('year', type = str, help = 'A year the films were created' )
    parser.add_argument('latitude', type = float, help = 'Current latitude of the person')
    parser.add_argument('longitude', type = float, help = 'Current longitude of the person')
    parser.add_argument('dataset_path', type = str, help = 'A path to the dataset')
    args = parser.parse_args()
    year = args.year
    latitude = args.latitude
    longitude = args.longitude
    dataset_path = args.dataset_path

    data_dict = {}
    with open(dataset_path, 'r', encoding='utf-8', errors='ignore') as file:

        for line in file:
            if '\t' not in line:
                continue
            temp_ls = re.split(r'\t+', line)
            name_part = temp_ls[0].strip()
            name = name_part[:name_part.find("(")-1]
            sub_ls = name_part.split()     # define the year
            for part in sub_ls:
                if '(' in part and '{' not in part and ' ' not in part:
                    curr_year = part[1:5]
                    break
            if curr_year == year:
                curr_location = temp_ls[1].strip()
                if curr_location not in data_dict:
                    curr_coord = coordinates_def(curr_location)
                    if curr_coord is not None:
                        data_dict[curr_location] = [curr_coord, [name], 1]
                else:
                    if name not in data_dict[curr_location][1]:
                        data_dict[curr_location][1].append(name)
                    else:
                        data_dict[curr_location][2] += 1
            else:
                continue
    distance_ls = []
    for item in data_dict.items():
        for film in item[1][1]:
            point = (geodesic(item[1][0], (latitude, longitude)).km,
            film, item[1][2], item[1][0])
            if len(distance_ls) <= 9:
                distance_ls.append(point)
            else:
                max_val = max(distance_ls, key= lambda x: x[0])
                if point[0] < max_val[0]:
                    distance_ls.remove(max_val)
                    distance_ls.append(point)
    generate_map(distance_ls, latitude, longitude, year)




if __name__ == "__main__":
    main()
