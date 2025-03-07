"""
Skagit Snow Analysis

A package for downloading, analyzing, and visualizing snow data for the Skagit River Basin.
"""

__version__ = "0.1.0"

from .core import (
    get_bounds,
    create_map,
    search_earth_data,
    filter_snow_data,
    download_earth_data,
)
from .data_processing import (
    preprocess_dataset,
    load_dataset,
    extract_variables,
)
from .visualization import (
    plot_skagit_basin_data,
)
