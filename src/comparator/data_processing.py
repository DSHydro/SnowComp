"""
Data processing functionality for snow data analysis.
"""
import os
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt



def preprocess_dataset(ds):
    """
    Preprocesses a dataset by assigning full timestamps and standardizing dimension names.
    
    Parameters:
    -----------
    ds : xarray.Dataset
        The dataset to preprocess
        
    Returns:
    --------
    xarray.Dataset
        The preprocessed dataset
    """
    file_name = ds.SWE_Post.encoding['source'].split('/')[-1].strip("'>")
    year = file_name.split('_')[-5].strip('WY')

    timestamps = pd.date_range(start=f'{year}-10-01', end=f'{int(year)+1}-09-30')
    
    # Use lowercase dimension names, change 'Day' to 'time'
    ds = ds.rename(dict(Longitude='x', Latitude='y', Day='time', Stats='stats'))
    
    # Promote non-dimensional coordinates to dimensions
    ds = ds.assign_coords(dict(
        time=timestamps, 
        stats=['mean', 'std', 'median', '25%', '75%']  # Order known from dataset documentation 
    ))

    return ds


def load_dataset(file_paths, chunks=None):
    """
    Loads multiple data files into a single xarray Dataset.
    
    Parameters:
    -----------
    file_paths : list
        List of file paths to load
    chunks : dict, optional
        Chunks specification for dask (default: {'time': 100})
        
    Returns:
    --------
    xarray.Dataset
        The loaded and preprocessed dataset
    """
    if chunks is None:
        chunks = {'time': 100}
    
    dataset = xr.open_mfdataset(
        file_paths, 
        engine='netcdf4', 
        chunks=chunks, 
        preprocess=preprocess_dataset
    )
    
    return dataset


def extract_variables(dataset, variable_requests, output_dir="."):
    """
    Extracts requested variables from the dataset and creates plots.
    
    Parameters:
    -----------
    dataset : xarray.Dataset
        The dataset containing the variables
    variable_requests : dict
        Dictionary mapping variable names to sub-variables (e.g., {'SWE_Post': 'mean'})
    output_dir : str, optional
        Directory where plots will be saved (default: current directory)
        
    Returns:
    --------
    dict
        Dictionary of extracted variable data
    """
    print("Starting variable extraction...")
    print(f"Requested variables: {variable_requests}")

    extracted_data = {}

    for var_name, sub_var in variable_requests.items():
        print(f"Processing variable: {var_name}, sub-variable: {sub_var}")

        if var_name not in dataset:
            print(f"Warning: Variable '{var_name}' not found in dataset. Skipping.")
            continue

        var_data = dataset[var_name]
        print(f"Found variable '{var_name}' with dimensions: {var_data.dims}")

        # If a sub-variable is specified (e.g., 'mean' from 'stats')
        if sub_var and 'stats' in var_data.dims:
            if sub_var not in dataset['stats'].values:
                print(f"Warning: Sub-variable '{sub_var}' not found in 'stats'. Skipping {var_name}.")
                continue

            sub_var_index = list(dataset['stats'].values).index(sub_var)
            var_data = var_data.isel(stats=sub_var_index)  # Select the sub-variable
            print(f"Selected sub-variable '{sub_var}' at index {sub_var_index}")

        # Store xarray DataArray details
        extracted_data[var_name] = var_data

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{var_name}_{sub_var if sub_var else 'all'}.png")

        plt.figure()
        if 'time' in var_data.dims:
            var_data.isel(time=0).plot()  # Plot the first time slice
            plt.title(f"{var_name} - {sub_var if sub_var else 'all'} (time=0)")
        else:
            var_data.plot()
            plt.title(f"{var_name} - {sub_var if sub_var else 'all'}")
        plt.savefig(output_path)
        plt.close()
    
    print("Variable extraction completed.")
    return extracted_data