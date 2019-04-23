# Item-Dependencies-Tree

This project is a proof of concept using python and javascript to visualize item dependencies for Web Mapping Applications in ArcGIS Online or Portal.

## Python

### App Dependencies Script

The app_item_dependencies.py script gathers all of the specified user's web mapping applications and searches through each application looking for item dependencies, such as web maps, operational layers, and embedded applications. The script also searches through any embedded applications that are found. The item name, type, ID, and URL (item details pages for apps and maps and REST service for operational layers) are written out to a JSON following the [Flare visualization toolkit](https://flare.prefuse.org/) package hierarchy.

### Layer Dependencies Script (work in progress)

The layer_item_dependencies.py script gathers all of the specified user's layers and searches through each web map looking for their dependencies. The item name, type, ID, and URL (item details pages for apps and maps and REST service for operational layers) are written out to a JSON following the [Flare visualization toolkit](https://flare.prefuse.org/) package hierarchy. 

## JavaScript

The lightweight JS application visualizes the JSON using D3 as an interactive tree diagram following Mike Bostock's [Collapsible Tree](https://observablehq.com/@d3/collapsible-tree) example. There are a few enhancements that have been made, such as a legend to identify item types, a clickable button to change between different views of the dataset, and a hover-over providing more information on each item.

![alt text](https://raw.githubusercontent.com/tatornator12/Item-Dependencies-Tree/master/app.png "Screenshot of App")
