# Item-Dependencies-Tree

This project is a proof of concept using python and javascript to visualize item dependencies for Web Mapping Applications in ArcGIS Online or Portal.

## Python

The item_dependencies.py script gathers all of the specified user's web mapping applications and searches through each application looking for item dependencies, such as web maps, operational layers, and embedded applications. The script also searches through any embedded applications that are found. The item name, type, ID, and URL (item details pages for apps and maps and REST service for operational layers) are written out to a JSON following the [Flare visualization toolkit](https://flare.prefuse.org/) package hierarchy.

## JavaScript

The lightweight JS application visualizes the JSON using D3 as an interactive tree diagram following Mike Bostock's [Collapsible Tree](https://observablehq.com/@d3/collapsible-tree) example.
