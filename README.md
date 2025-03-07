# Snow Analysis

A Python package for downloading, analyzing, and visualizing snow data.

## Installation

```bash
pip install comparator
```

Or install directly from the source:

```bash
git clone https://github.com/yourusername/comparator.git
cd comparator
pip install -e .
```

## Usage

### Command line interface

```bash
# Basic usage with default parameters
comparator

# Specify custom parameters
comparator --lat 48.6 --lon -121.4 --south 46.6 --west -121.4 --doi 10.5067/PP7T2GBI52I2 --data-dir data --output-dir output --boundary-file SkagitBoundary.json --variables SWE_Post:mean,SCA_Post:mean
```

### Python API

```python
import os
from dotenv import load_dotenv
import geopandas as gpd
from comparator import core, data_processing, visualization

# Load environment variables (for Earthdata credentials)
load_dotenv()

# Set parameters
lat = 48.6
lon = -121.4
south = 46.6
west = -121.4
doi = "10.5067/PP7T2GBI52I2"
data_dir = "data"
output_dir = "output"

# Create a map
map_path = core.create_map(lat, lon, south, west, False, os.path.join(output_dir, "map.html"))

# Search for data
results = core.search_earth_data(doi, lon, lat)
subset, files, years = core.filter_snow_data(results)

# Download data
downloaded_files = core.download_earth_data(subset, data_dir)

# Load the dataset
dataset = data_processing.load_dataset(downloaded_files)

# Load the Skagit boundary
try:
    boundary_gdf = gpd.read_file("SkagitBoundary.json")
except Exception as e:
    print(f"Error loading boundary: {e}")
    boundary_gdf = None

# Extract variables
variable_dict = {"SWE_Post": "mean", "SCA_Post": "mean"}
extracted_data = data_processing.extract_variables(dataset, variable_dict, output_dir)

# Plot data
swe_mean = visualization.plot_skagit_basin_data(
    dataset, "SWE_Post", "mean", 0, boundary_gdf, output_dir
)
sca_mean = visualization.plot_skagit_basin_data(
    dataset, "SCA_Post", "mean", 0, boundary_gdf, output_dir
)

# Plot comparison
if swe_mean is not None and sca_mean is not None:
    visualization.plot_comparison(
        [swe_mean, sca_mean],
        ["SWE", "SCA"],
        "Skagit Basin Mean SWE and SCA",
        os.path.join(output_dir, "skagit_basin_swe_sca_comparison.png")
    )
```

## Requirements

- Python 3.8+
- NASA Earthdata account (set credentials in `.env` file)

## Environment Variables

Create a `.env` file with your Earthdata credentials:

```
EARTHDATA_USERNAME=your_username
EARTHDATA_PASSWORD=your_password
```

## Open source licensing

Statement from Schmidt Sciences:

_Schmidt Sciences expects that any code from projects funded by Schmidt Sciences
be released as open source under an
[OSI](https://opensource.org/licenses)-approved permissive license (such as
[Apache v2.0](https://choosealicense.com/licenses/apache-2.0/) or
[MIT](https://choosealicense.com/licenses/mit/)). We recommend that projects
avoid using GPL due to known complexities associated with it. We encourage
projects to publish data used for peer-reviewed scientific articles along with
the code used to produce the results. Additionally, we recommend avoiding any
license modifications for simplicity, and alignment with standard practices._
