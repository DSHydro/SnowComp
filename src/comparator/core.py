"""
Core functionality for accessing and downloading snow data.
"""

import os
import webbrowser
import folium
import earthaccess


def get_bounds(south, west):
    """
    Returns the southwest and northeast corners of a rectangle.
    
    Parameters:
    -----------
    south : float
        The southern latitude boundary
    west : float
        The western longitude boundary
        
    Returns:
    --------
    list
        A list containing the southwest and northeast coordinates
    """
    southwest = (south, west)
    northeast = (south + 1, west + 1)  # Add 1 degree to latitude and longitude
    return [southwest, northeast]


def create_map(lat, lon, south, west, open_browser=False, output_path="map.html"):
    """
    Generates a map with a bounding box and saves it as an HTML file.
    
    Parameters:
    -----------
    lat : float
        Latitude for the map center
    lon : float
        Longitude for the map center
    south : float
        The southern latitude boundary
    west : float
        The western longitude boundary
    open_browser : bool, optional
        Whether to open the map in a browser (default: False)
    output_path : str, optional
        Path where the map will be saved (default: "map.html")
        
    Returns:
    --------
    str
        Path to the saved map file
    """
    map = folium.Map(
        location=[lat, lon],
        zoom_start=8,
    )

    # Create a rectangle using the southwest and northeast bounds
    folium.Rectangle(
        bounds=get_bounds(south, west),
        color="#ff7800",
        fill=True,
        fill_color="#ffff00",
        fill_opacity=0.2,
    ).add_to(map)

    # Save and open the map in the browser
    map_path = os.path.abspath(output_path)
    map.save(map_path)
    if open_browser:
        webbrowser.open("file://" + map_path)  # Open the map in the default web browser
    
    return map_path


def search_earth_data(doi, lon, lat):
    """
    Searches for data using the Earthdata API.
    
    Parameters:
    -----------
    doi : str
        Digital Object Identifier for the dataset
    lon : float
        Longitude for the point of interest
    lat : float
        Latitude for the point of interest
        
    Returns:
    --------
    list
        List of search results from earthaccess
    """
    # Authenticating the user using environment variables
    earthaccess.login()

    results = earthaccess.search_data(
        doi=doi,
        point=(lon, lat),
    )

    return results


def filter_snow_data(results, keyword="SWE"):
    """
    Filters the data based on the keyword.
    
    Parameters:
    -----------
    results : list
        List of search results from earthaccess
    keyword : str, optional
        Keyword to filter results (default: "SWE")
        
    Returns:
    --------
    tuple
        Tuple containing filtered data links, file names, and years
    """
    links = [res.data_links()[0] for res in results]
    subset = [x for x in links if keyword in x]

    files = [x.split('/')[-1] for x in subset]
    years = [x.split('/')[-2][:4] for x in subset]

    return subset, files, years


def download_earth_data(file_links, output_dir):
    """
    Downloads the data from the Earthdata API.
    
    Parameters:
    -----------
    file_links : list
        List of file URLs to download
    output_dir : str
        Directory where files will be saved
        
    Returns:
    --------
    list
        List of paths to downloaded files
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    downloaded_files = earthaccess.download(file_links, output_dir)
    return downloaded_files
