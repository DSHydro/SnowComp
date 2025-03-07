"""
Utility functions for the Skagit Snow Analysis package.
"""

import os
import logging


def setup_logging(level=logging.INFO, log_file=None):
    """
    Sets up logging configuration.
    
    Parameters:
    -----------
    level : int, optional
        Logging level (default: logging.INFO)
    log_file : str, optional
        Path to log file, if None, log to console only (default: None)
        
    Returns:
    --------
    logging.Logger
        Configured logger
    """
    logger = logging.getLogger("snow_analysis")
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log_file is specified
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def ensure_directory(directory_path):
    """
    Ensures that a directory exists, creating it if necessary.
    
    Parameters:
    -----------
    directory_path : str
        Path to the directory
        
    Returns:
    --------
    str
        Absolute path to the directory
    """
    if not directory_path:
        return os.getcwd()
    
    abs_path = os.path.abspath(directory_path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path