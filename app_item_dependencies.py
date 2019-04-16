import json
import os
import time
import datetime
from arcgis.gis import GIS
from urllib.parse import urlparse

# Get Script Directory
this_dir = r'C:\path\to\directory'

# Get Start Time - UTC Seconds
start_time = time.time()

# Extract Operational Layers from a Web Map
def mapSearch(map_itemId, item_list):
    # Get Web Map item
    print("     Web Map found: " + map_itemId + ". Retrieving operational layers.")
    map_item = gis.content.get(map_itemId)

    if map_item:
        if map_item.type == "Web Map" or map_item.type == "Web Scene":

            # Build Dictionary for Web Map
            map_item_details = {'name': map_item.title, 'type': map_item.type, 'id': map_item.id,
                                'url': map_item.homepage, 'children': None}

            # Get Web Map as JSON
            wm_json = map_item.get_data()

            # Build List of Dictionaries for Web Map Op Layers
            wm_children = [
                {'name': op['title'], 'type': op['layerType'], 'id': [op['itemId'] if 'itemId' in op.keys() else ''][0],
                 'url': [value for key, value in op.items() if 'url' in key.lower()][0]} for op in
                wm_json['operationalLayers']]

            # Add Web Map Op Layers Dictionary to List
            map_item_details['children'] = wm_children

            # Append each Web Map as a child to the item
            if map_item_details not in item_list:
                return item_list.append(map_item_details)


# Extract Apps from Webpages
def webpageSearch(webpage, item_list):

    # Parse Webpage URL for item ID
    parsed = urlparse(webpage)
    app_url_id = parsed.query[6:]

    # Confirm the ID
    if app_url_id.isalnum() == True and len(app_url_id) == 32:

        # Get Web App item
        print("     Web App found: " + app_url_id)
        app_url_item = gis.content.get(app_url_id)

        # Build Dictionary for Web App
        app_item_details = {"name": app_url_item.title, "type": app_url_item.type, "id": app_url_item.id,
                            "url": app_url_item.homepage, "children": []}

        # Search through JSON of embedded apps
        print("     Searching through the JSON of the embedded web app.......")
        webappSearch(app_url_item, app_item_details['children'])

        # Append each Web App as a child to the app item
        if app_item_details not in item_list:
            return item_list.append(app_item_details)


# Helper function to get all nested values in a dict
def get_values_recurs(dict_):
    output = []
    if isinstance(dict_, dict):
        for value in dict_.values():
            if isinstance(value, dict):
                output += get_values_recurs(value)
            elif isinstance(value, list):
                for entry in value:
                    output += get_values_recurs({"_":entry})
            else:
                output += [value,]
    return output


# Search through Web App JSON values for Item IDs and URLs
def webappSearch(item, item_list):
    # Get all values in JSON of app item
    all_values = get_values_recurs(item.get_data())

    # Search through values for Webmaps and Webpages
    for value in all_values:
        if str(value).isalnum() == True and len(str(value)) == 32:
            mapSearch(value, item_list)
        elif str(value).startswith("http"):
            webpageSearch(value, item_list)


if __name__ == "__main__":

    # Set Logger Time
    logger_date = datetime.datetime.fromtimestamp(start_time).strftime('%Y_%m_%d')
    logger_time = datetime.datetime.fromtimestamp(start_time).strftime('%H_%M_%S')
    print('Script Started: {} - {}\n'.format(logger_date, logger_time))
    print('Executing process.........')

    # Connect to Portal
    print("Connecting to Portal....")
    gis = GIS('https://my.portal.com/portal', username, password, verify_cert=False)

    # Search through user's content
    print("Searching through user's applications....")
    search_result = gis.content.search(query='owner:admin', item_type='application', max_items=10000)

    # Create the master dictionary
    item_dict = {'name': 'admin', 'children': []}

    # Search through Web App items
    for app_item in search_result:
        # Create entry for Web App item
        item_details = {'name': app_item.title, 'type': app_item.type, 'id': app_item.id, 'url': app_item.homepage,
                        'children': []}

        # Append entry to master dictionary
        item_dict['children'].append(item_details)

        # Call web app JSON function
        print("Searching through " + app_item.title + " JSON.......")
        webappSearch(app_item, item_details['children'])

    # Write result to text file
    dependencies_file = os.path.join(this_dir, 'dependencies.txt')
    with open(dependencies_file, 'w') as outfile:
        outfile.write(json.dumps(item_dict, indent=4))

    print("Process completed.")
    print("\nProgram Run Time: %.2f Seconds" % (time.time() - start_time))