"""
Visualization functionality for snow data analysis.
"""

import os
import matplotlib.pyplot as plt
import geopandas as gpd


def plot_skagit_basin_data(dataset, variable_name="SWE_Post", sub_variable="mean", 
                           time_index=0, boundary_gdf=None, output_dir="."):
    """
    Plots the spatial data for the Skagit River Basin using a GeoDataFrame boundary.
    
    Parameters:
    -----------
    dataset : xarray.Dataset
        The dataset containing the variables to plot
    variable_name : str, optional
        Name of the variable to plot (default: "SWE_Post")
    sub_variable : str, optional
        Sub-variable to select if the variable has a 'stats' dimension (default: "mean")
    time_index : int, optional
        Time index to select for plotting (default: 0)
    boundary_gdf : geopandas.GeoDataFrame, optional
        GeoDataFrame containing the Skagit Basin boundary
    output_dir : str, optional
        Directory where plots will be saved (default: current directory)
        
    Returns:
    --------
    xarray.DataArray or None
        Basin mean time series if successfully calculated, otherwise None
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    if variable_name not in dataset:
        print(f"Variable '{variable_name}' not found in dataset.")
        return None

    var_data = dataset[variable_name]

    # If a sub-variable is specified and supported, select it.
    if sub_variable and 'stats' in var_data.dims:
        if sub_variable not in dataset['stats'].values:
            print(f"Sub-variable '{sub_variable}' not found in 'stats' dimension.")
            return None
        sub_var_index = list(dataset['stats'].values).index(sub_variable)
        var_data = var_data.isel(stats=sub_var_index)

    # Select the data at the specified time index if a 'time' dimension exists.
    if 'time' in var_data.dims:
        data_for_plot = var_data.isel(time=time_index)
    else:
        data_for_plot = var_data

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(15, 8))
    
    if boundary_gdf is not None and not boundary_gdf.empty:
        try:
            # Set spatial dimensions
            data_for_plot = data_for_plot.rio.set_spatial_dims(x_dim='x', y_dim='y')
            data_for_plot = data_for_plot.rio.write_crs("epsg:4326")
            
            # Get the list of geometries from the GeoDataFrame
            poly = boundary_gdf.geometry.to_list()
            
            # Clip the data to the basin boundary
            clipped_data = data_for_plot.rio.clip(poly, crs="epsg:4326")
            
            # Plot the clipped data
            clipped_data.plot(ax=ax, cmap='viridis')
            
            # Plot the basin boundary on top for reference
            boundary_gdf.plot(ax=ax, edgecolor='blue', linestyle='--', facecolor='none')
            
            plt.title(f"Skagit River Basin - {variable_name} ({sub_variable}) at time index {time_index}")
        except Exception as e:
            print(f"Error during clipping: {e}")
            print("Falling back to unclipped data plot")
            data_for_plot.plot(ax=ax, cmap='viridis')
            plt.title(f"{variable_name} ({sub_variable}) at time index {time_index} (Unclipped)")
    else:
        # No boundary provided, plot the unclipped data
        data_for_plot.plot(ax=ax, cmap='viridis')
        plt.title(f"{variable_name} ({sub_variable}) at time index {time_index}")
    
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    ax.set_aspect(1)  # Equal aspect ratio
    
    output_path = os.path.join(output_dir, f"{variable_name}_{sub_variable}_skagit_basin.png")
    plt.savefig(output_path)
    plt.show()
    
    # Calculate and plot basin mean
    if boundary_gdf is not None and 'time' in var_data.dims:
        try:
            # Set spatial dimensions for the full time series
            var_data_spatial = var_data.rio.set_spatial_dims(x_dim='x', y_dim='y')
            var_data_spatial = var_data_spatial.rio.write_crs("epsg:4326")
            
            # Get the list of geometries from the GeoDataFrame
            poly = boundary_gdf.geometry.to_list()
            
            # Clip the data to the basin boundary
            basin_data = var_data_spatial.rio.clip(poly, crs="epsg:4326")
            
            # Calculate basin mean
            basin_mean = basin_data.mean(dim=('x', 'y'))
            
            # Plot time series of basin mean
            plt.figure(figsize=(15, 5))
            basin_mean.plot()
            plt.title(f"Skagit Basin Mean {variable_name} ({sub_variable})")
            plt.xlabel("Time")
            plt.ylabel(f"{variable_name} ({var_data.attrs.get('Units', 'unknown units')})")
            
            timeseries_path = os.path.join(
                output_dir, 
                f"{variable_name}_{sub_variable}_skagit_basin_mean_timeseries.png"
            )
            plt.savefig(timeseries_path)
            plt.show()
            
            return basin_mean
        except Exception as e:
            print(f"Error calculating basin mean: {e}")
    
    return None


def plot_comparison(data_arrays, labels, title, output_path):
    """
    Plots multiple time series on the same figure for comparison.
    
    Parameters:
    -----------
    data_arrays : list
        List of xarray.DataArray objects to plot
    labels : list
        List of labels for each data array
    title : str
        Title for the plot
    output_path : str
        Path where the plot will be saved
        
    Returns:
    --------
    None
    """
    plt.figure(figsize=(15, 5))
    
    for data, label in zip(data_arrays, labels):
        if data is not None:
            data.plot(label=label)
    
    plt.legend()
    plt.title(title)
    plt.savefig(output_path)
    plt.show()