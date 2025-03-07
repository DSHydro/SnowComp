"""
Command-line interface for the Skagit Snow Analysis package.
"""

import os
import sys
import argparse
import geopandas as gpd
import watermark
import logging

from dotenv import load_dotenv
from . import core, data_processing, visualization
from .utils import setup_logging, ensure_directory


def main():
    """
    Main function for the command-line interface.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Snow Analysis Tool')
    
    parser.add_argument('--lat', type=float, default=48.6,
                        help='Latitude (default: 48.6)')
    parser.add_argument('--lon', type=float, default=-121.4,
                        help='Longitude (default: -121.4)')
    parser.add_argument('--south', type=float, default=46.6,
                        help='Southern latitude boundary (default: 46.6)')
    parser.add_argument('--west', type=float, default=-121.4,
                        help='Western longitude boundary (default: -121.4)')
    parser.add_argument('--doi', type=str, default='10.5067/PP7T2GBI52I2',
                        help='Digital Object Identifier (default: 10.5067/PP7T2GBI52I2)')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Directory for data download (default: data)')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory for output files (default: output)')
    parser.add_argument('--log-file', type=str, default=None,
                        help='Path to log file (default: None, log to console only)')
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Logging level (default: INFO)')
    parser.add_argument('--open-browser', action='store_true',
                        help='Open map in browser')
    parser.add_argument('--boundary-file', type=str, default='SkagitBoundary.json',
                        help='Path to Skagit boundary GeoJSON file (default: SkagitBoundary.json)')
    parser.add_argument('--variables', type=str, default='SWE_Post:mean,SCA_Post:mean',
                        help='Variables to extract in format var1:subvar1,var2:subvar2 (default: SWE_Post:mean,SCA_Post:mean)')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = getattr(logging, args.log_level)
    logger = setup_logging(level=log_level, log_file=args.log_file)
    
    # Ensure directories exist
    data_dir = ensure_directory(args.data_dir)
    output_dir = ensure_directory(args.output_dir)
    
    try:
        logger.info("Starting Snow Analysis")
        logger.info(f"Using coordinates: {args.lat}, {args.lon}")
        logger.info(f"Boundary box: S={args.south}, W={args.west}")
        
        # Generate and display the map
        map_path = core.create_map(
            args.lat, args.lon, args.south, args.west, 
            args.open_browser, 
            os.path.join(output_dir, "map.html")
        )
        logger.info(f"Map created at: {map_path}")

        # Get Earthdata API results
        logger.info(f"Searching for data with DOI: {args.doi}")
        results = core.search_earth_data(args.doi, args.lon, args.lat)
        
        if not results:
            logger.error("No data found. Exiting.")
            return 1
        
        logger.info(f"Found {len(results)} results")
        
        # Filter results for snow data
        subset, files, years = core.filter_snow_data(results)
        
        if not subset:
            logger.error("No snow data found after filtering. Exiting.")
            return 1
        
        logger.info(f"Filtered to {len(subset)} files for years: {', '.join(set(years))}")
        
        # Download the files
        logger.info(f"Downloading data to: {data_dir}")
        downloaded_files = core.download_earth_data(subset, data_dir)
        logger.info(f"Downloaded {len(downloaded_files)} files")
        
        # Load the dataset
        logger.info("Loading dataset")
        dataset = data_processing.load_dataset(downloaded_files)
        logger.info(f"Available variables: {list(dataset.variables)}")
        
        # Load the Skagit boundary
        boundary_gdf = None
        try:
            logger.info(f"Loading Skagit Basin boundary from: {args.boundary_file}")
            boundary_gdf = gpd.read_file(args.boundary_file)
            logger.info("Successfully loaded Skagit Basin boundary.")
        except Exception as e:
            logger.warning(f"Error loading Skagit boundary: {e}")
            logger.warning("Will proceed without basin clipping.")
        
        # Parse variables argument
        variable_dict = {}
        for var_pair in args.variables.split(','):
            if ':' in var_pair:
                var_name, subvar = var_pair.split(':')
                variable_dict[var_name] = subvar
            else:
                variable_dict[var_pair] = None
        
        # Extract variables
        logger.info(f"Extracting variables: {variable_dict}")
        extracted_data = data_processing.extract_variables(
            dataset, variable_dict, output_dir
        )
        
        # Plot data for each variable
        basin_means = {}
        for var_name, subvar in variable_dict.items():
            if var_name in dataset:
                logger.info(f"Plotting {var_name} data")
                basin_mean = visualization.plot_skagit_basin_data(
                    dataset, var_name, subvar, 0, boundary_gdf, output_dir
                )
                basin_means[var_name] = basin_mean
        
        # Compare SWE and SCA if both are available
        if "SWE_Post" in basin_means and "SCA_Post" in basin_means:
            logger.info("Plotting SWE and SCA comparison")
            visualization.plot_comparison(
                [basin_means["SWE_Post"], basin_means["SCA_Post"]],
                ["SWE", "SCA"],
                "Skagit Basin Mean SWE and SCA",
                os.path.join(output_dir, "skagit_basin_swe_sca_comparison.png")
            )
        
        logger.info("Process completed successfully.")
        logger.info(watermark.watermark())
        return 0
        
    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())