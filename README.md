# Programming_task_2

The module main.py generates a map (html) of the closest to the start point film locations from the file for the mentioned year
The program takes 4 arguments: 
        --- the year
        --- the start latitude
        --- the start longitude
        --- the path to the dataset

The map contains 4 layers:
        --- the main one (the map itself)
        --- the mark layer (depicts locations)
        --- the layer that shows how many times the creation of the film
            repeated in the current location (colour indicators)
        --- the layer that shows the route between the location points

The module has been tested with a smaller file of data (the part of locations.list, - locations2.list)
Here is an example of running the module:
>>> python3 main.py 2017 60 30 'locations2.list'
![Alt text](/map_screen.png?raw=true "Optional Title")
