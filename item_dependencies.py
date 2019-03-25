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

# Search through JSON for Webmaps
def mapJsonSearch(map_json, item_list):

    # Get Web Map ID from JSON
    map_itemId = map_json

    # Confirm the ID
    if map_itemId.isalnum() == True and len(map_itemId) == 32:

        # Get Web Map item
        print("     Web Map found: " + map_itemId + ". Retrieving operational layers.")
        map_item = gis.content.search('id: {}'.format(map_itemId), outside_org=True)[0]

        # Build Dictionary for Web Map
        map_item_details = {'name': map_item.title, 'type': map_item.type, 'id': map_item.id,
                            'url': item_settings_url + map_item.id, 'children': None}

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


# Search through JSON for Webpages
def webpageJsonSearch(webpage_json, item_list):

    # Parse Webpage URL for item ID
    parsed = urlparse(webpage_json)
    app_url_id = parsed.query[6:]

    # Confirm the ID
    if app_url_id.isalnum() == True and len(app_url_id) == 32:

        # Get Web App item
        print("     Web App found: " + app_url_id)
        app_url_item = gis.content.get(app_url_id)

        # Build Dictionary for Web App
        app_item_details = {"name": app_url_item.title, "type": app_url_item.type, "id": app_url_item.id,
                            "url": item_settings_url + app_url_item.id, "children": []}

        # Search through JSON of embedded apps
        print("     Searching through the JSON of the embedded web app.......")
        webappJsonSearch(app_url_item, app_item_details['children'])

        # Append each Web App as a child to the app item
        if app_item_details not in item_list:
            return item_list.append(app_item_details)


# Search through Web App JSON
def webappJsonSearch(item, item_list):

    # Determine App Type
    if 'Cascade' in item.typeKeywords:

        # Get Cascade Item as JSON
        print('     Web App uses Cascade template.')
        item_dep = item.get_data()

        # Parse Cascade JSON
        cascade_sections_list = item_dep['values']['sections']

        # Search through Cascade JSON for Webmaps and Webpages
        for section in cascade_sections_list:
            if 'foreground' in section and 'blocks' in section['foreground']:
                cascade_foreground_dict = dict(section['foreground'])
                cascade_blocks_list = cascade_foreground_dict['blocks']
                for section_item in cascade_blocks_list:
                    if 'webmap' in section_item['type']:

                        # Call Map JSON Search function
                        mapJsonSearch(section_item['webmap']['id'], item_list)

                    elif 'webpage' in section_item['type']:

                        # Call Webpage JSON Search function
                        webpageJsonSearch(section_item['webpage']['url'], item_list)

            elif 'views' in section and [1 for x in section['views'] if 'background' in x.keys()]:
                cascade_views_list = section['views']
                for view_item in cascade_views_list:
                    if 'webmap' in view_item['background']['type']:

                        # Call Map JSON Search function
                        mapJsonSearch(view_item['background']['webmap']['id'], item_list)

                    elif 'webpage' in view_item['background']['type']:

                        # Call Webpage JSON Search function
                        webpageJsonSearch(view_item['background']['webpage']['url'], item_list)

    elif "StoryMapBasic" in item.url:

        # Get Map Basic Item as JSON
        print('     Web App uses Story Map Basic template.')
        item_dep = item.get_data()

        # Call Map JSON Search function
        mapJsonSearch(item_dep['values']['webmap'], item_list)

    elif "mapseries" in item.typeKeywords:

        # Get Map Series Item as JSON
        print('     Web App uses Map Series template.')
        item_dep = item.get_data()

        # Parse Map Series JSON
        series_story_list = item_dep['values']['story']['entries']

        # Search through Map Series JSON for Webmaps and Webpages
        for entries_item in series_story_list:
            if 'webmap' in entries_item['media']:

                # Call Map JSON Search function
                mapJsonSearch(entries_item['media']['webmap']['id'], item_list)

            elif 'webpage' in entries_item['media']:

                # Call Webpage JSON Search function
                webpageJsonSearch(entries_item['media']['webpage']['url'], item_list)

    elif "mapjournal" in item.typeKeywords:

        # Get Map Journal Item as JSON
        print('     Web App uses Map Journal template.')
        item_dep = item.get_data()

        # Parse Map Journal JSON
        journal_story_list = item_dep['values']['story']['sections']

        # Search through Map Journal JSON for Webmaps and Webpages
        for journal_section in journal_story_list:
            if 'webmap' in journal_section['media']:

                # Call Map JSON Search function
                mapJsonSearch(journal_section['media']['webmap']['id'], item_list)

            elif 'webpage' in journal_section['media']:

                # Call Webpage JSON Search function
                webpageJsonSearch(journal_section['media']['webpage']['url'], item_list)

    elif "Map Tour" in item.typeKeywords:

        # Get Map Basic Item as JSON
        print('     Web App uses Map Tour template.')
        item_dep = item.get_data()

        # Call Map JSON Search function
        mapJsonSearch(item_dep['values']['webmap'], item_list)

    elif 'layout-swipe' in item.typeKeywords:

        # Get Map Swipe Item as JSON
        print('     Web App uses Story Map Swipe template.')
        item_dep = item.get_data()

        # Parse Map Swipe JSON
        swipe_webmaps_list = item_dep['values']['webmaps']

        for swipe_webmap in swipe_webmaps_list:

            # Call Map JSON Search function
            mapJsonSearch(swipe_webmap, item_list)

    elif 'Web AppBuilder' in item.typeKeywords:

        # Get WAB Item as JSON
        print('     Web App uses Web AppBuilder template.')
        item_dep = item.get_data()

        # Call Map JSON Search function
        mapJsonSearch(item_dep['map']['itemId'], item_list)

    elif 'Operations Dashboard' in item.typeKeywords:

        # Get Ops Dashboard Item as JSON
        print('     Web App uses Operations Dashboard template.')
        item_dep = item.get_data()

        # Parse Ops Dashboard JSON
        ops_widgets_list = item_dep['widgets']

        for ops_widget in ops_widgets_list:
            if 'mapWidget' in ops_widget['type']:

                # Call Map JSON Search function
                mapJsonSearch(ops_widget['itemId'], item_list)

            elif 'embeddedContentWidget' in ops_widget['type']:

                # Call Webpage JSON Search function
                webpageJsonSearch(ops_widget['url'], item_list)


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
    search_result = gis.content.search(query='owner:username', item_type='application', max_items=10000)

    # Create the master dictionary
    item_dict = {'name':'username', 'children': []}

    # Setup Web Map and Web App URLs
    item_settings_url = 'https://my.portal.com/portal/home/item.html?id='

    # Search through Web App items
    for app_item in search_result:

        # Create entry for Web App item
        item_details = {'name': app_item.title, 'type': app_item.type, 'id': app_item.id, 'url': item_settings_url+app_item.id, 'children': []}

        # Append entry to master dictionary
        item_dict['children'].append(item_details)

        # Call web app JSON function
        print("Searching through " + app_item.title + " JSON.......")
        webappJsonSearch(app_item, item_details['children'])

    # Write result to text file
    dependencies_file = os.path.join(this_dir, 'dependencies.txt')
    with open(dependencies_file, 'w') as outfile:
        outfile.write(json.dumps(item_dict, indent=4))

    print("Process completed.")
    print("\nProgram Run Time: %.2f Seconds" % (time.time() - start_time))
