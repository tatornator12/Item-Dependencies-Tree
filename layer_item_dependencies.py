import json
import os
import time
import datetime
from arcgis.gis import GIS

# Get Script Directory
this_dir = r'C:\path\to\directory'

# Get Start Time - UTC Seconds
start_time = time.time()


# Search for all web maps for user
def get_maps_to_check():

    webmap_list = []
    map_query = "owner:username (type:(\"Web Map\" OR \"Web Scene\") -type:(\"Web Mapping Application\"))"
    for webmap in gis.content.search(query=map_query, max_items=10000):
        webmap_list.append(webmap)

    return webmap_list


# Search for all layers for user
def get_layers_to_check():

    layer_query = "owner:username ('type:\"Scene Service\" OR type:\"Feature Collection\" OR type:\"Layer\" OR type:\"Feature Service\" OR type:\"Map Service\" OR type:\"Vector Tile Service\" OR type:\"Image Service\"')"
    for layer in gis.content.search(query=layer_query, max_items=10000):
        yield layer


# Search for layers within web maps
def layerSearch(layer, item_list):

    for map_item in get_maps_to_check():

        wm_json = map_item.get_data()

        # Build List of Dictionaries for Web Maps that use the layer
        if 'operationalLayers' in wm_json.keys():
            for op in wm_json['operationalLayers']:
                if layer.id == [op['itemId'] if 'itemId' in op.keys() else ''][0]:
                    map_item_details = {'name': map_item.title, 'type': map_item.type, 'id': map_item.id, 'url':
                        map_item.homepage, 'children': None}

                    # Append each Web Map as a child to the layer item
                    if map_item_details not in item_list:
                        return item_list.append(map_item_details)

                elif layer.url == [value for key, value in op.items() if 'url' in key.lower()][0]:
                    map_item_details = {'name': map_item.title, 'type': map_item.type, 'id': map_item.id, 'url':
                        map_item.homepage, 'children': None}

                    # Append each Web Map as a child to the layer item
                    if map_item_details not in item_list:
                        return item_list.append(map_item_details)


if __name__ == "__main__":

    # Set Logger Time
    logger_date = datetime.datetime.fromtimestamp(start_time).strftime('%Y_%m_%d')
    logger_time = datetime.datetime.fromtimestamp(start_time).strftime('%H_%M_%S')
    print('Script Started: {} - {}\n'.format(logger_date, logger_time))
    print('Executing process.........')

    # Connect to Portal
    print("Connecting to Portal to begin search for layers....")
    gis = GIS('https://my.portal.com/portal', username, password, verify_cert=False)

    # Create the master dictionary
    item_dict = {'name': username, 'children': []}

    # Search through Web App items
    for layer_item in get_layers_to_check():

        # Create entry for Web App item
        item_details = {'name': layer_item.title, 'type': layer_item.type, 'id': layer_item.id, 'url': layer_item.url,
                        'children': []}

        # Append entry to master dictionary
        item_dict['children'].append(item_details)

        # Call web app JSON function
        print("Searching for all web maps where " + layer_item.title + " is used.......")
        layerSearch(layer_item, item_details['children'])

    # Write result to text file
    dependencies_file = os.path.join(this_dir, 'dependencies.txt')
    with open(dependencies_file, 'w') as outfile:
        outfile.write(json.dumps(item_dict, indent=4))

    print("Process completed.")
    print("\nProgram Run Time: %.2f Seconds" % (time.time() - start_time))
