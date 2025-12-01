# API Documentation

API reference for the traffic data cleaning pipeline modules.

## Table of Contents

- [Basic Data Cleaning](#basic-data-cleaning)
- [Map Matching](#map-matching)
- [Utilities](#utilities)

## Basic Data Cleaning

### CSVToSQLiteProcessor

**Location**: `src/basic_data_cleaning/unified_database.py`

Converts CSV files to unified SQLite database.

#### Methods

##### `__init__(input_folder, output_folder, stop_event=None)`

Initialize the processor.

**Parameters**:
- `input_folder` (str): Path to input data directory
- `output_folder` (str): Path to output directory
- `stop_event` (optional): Event for stopping processing

**Returns**: None

##### `detect_encoding(file_path)`

Detects file encoding using chardet.

**Parameters**:
- `file_path` (str): Path to file

**Returns**: str - Detected encoding

##### `run()`

Main processing method. Scans input folder and converts all CSV files to database tables.

**Returns**: None

---

### TimeStandardizationProcessor

**Location**: `src/basic_data_cleaning/time_standardization.py`

Standardizes timestamps across all data sources.

#### Methods

##### `__init__(database_path, timezone='America/New_York')`

Initialize the processor.

**Parameters**:
- `database_path` (str): Path to SQLite database
- `timezone` (str): Target timezone (default: 'America/New_York')

**Returns**: None

##### `run()`

Converts all timestamps to standardized local time format.

**Returns**: None

---

### BasicDataCleaner

**Location**: `src/basic_data_cleaning/basic_data_cleaning.py`

Performs basic data cleaning operations (duplicate removal, outlier detection).

#### Methods

##### `__init__(database_path)`

Initialize the cleaner.

**Parameters**:
- `database_path` (str): Path to SQLite database

**Returns**: None

##### `remove_duplicates(table_name, key_columns)`

Remove duplicate records.

**Parameters**:
- `table_name` (str): Table name
- `key_columns` (list): Columns to use for duplicate detection

**Returns**: int - Number of duplicates removed

##### `detect_outliers(table_name, speed_column, min_speed=0, max_speed=100)`

Detect and remove speed outliers using IQR method.

**Parameters**:
- `table_name` (str): Table name
- `speed_column` (str): Speed column name
- `min_speed` (float): Minimum valid speed (default: 0)
- `max_speed` (float): Maximum valid speed (default: 100)

**Returns**: int - Number of outliers removed

---

## Map Matching

### MapMatchingProcessor

**Location**: `src/map_matching/mapmatching.py`

Performs map matching of GPS waypoints to road network using gotrackit.

#### Methods

##### `__init__(input_folder, output_folder, stop_event=None, progress_callback=None, progress_output=None)`

Initialize the processor.

**Parameters**:
- `input_folder` (str): Path to input data directory
- `output_folder` (str): Path to output directory
- `stop_event` (optional): Event for stopping processing
- `progress_callback` (optional): Callback function for progress updates
- `progress_output` (optional): Output stream for progress (default: sys.stdout)

**Returns**: None

##### `process_network()`

Processes network files (node.csv, link.csv) and creates shapefiles for map matching.

**Returns**: None

**Raises**:
- `FileNotFoundError`: If network files are missing
- `ValueError`: If network data is invalid

##### `load_gps_data()`

Loads waypoint GPS data from database with proper field names for gotrackit.

**Returns**: pd.DataFrame - GPS data with columns: agent_id, time, lng, lat

##### `perform_map_matching(gps_buffer=50.0)`

Performs map matching using gotrackit library.

**Parameters**:
- `gps_buffer` (float): GPS buffer radius in meters (default: 50.0)

**Returns**: None

**Raises**:
- `AssertionError`: If network or GPS data format is incorrect

##### `run()`

Main processing method. Executes full map matching pipeline.

**Returns**: None

---

### MapMatchingAnalyzer

**Location**: `src/map_matching/mapmatching.py`

Analyzes map matching results and coverage.

#### Methods

##### `__init__(database_path)`

Initialize the analyzer.

**Parameters**:
- `database_path` (str): Path to SQLite database

**Returns**: None

##### `run()`

Analyzes map matching coverage and generates statistics.

**Returns**: dict - Analysis results with match rates and statistics

---

## Utilities

### Utility Functions

**Location**: `src/utils.py`

Common utility functions used across the pipeline.

#### Functions

##### `validate_data_path(path)`

Validates that a data path exists and is accessible.

**Parameters**:
- `path` (str or Path): Path to validate

**Returns**: Path - Validated path object

**Raises**:
- `FileNotFoundError`: If path does not exist

##### `get_file_size(filepath)`

Gets file size in human-readable format.

**Parameters**:
- `filepath` (str or Path): File path

**Returns**: str - Formatted file size (e.g., "1.5 GB")

---

## Usage Examples

### Example 1: Database Creation

```python
from basic_data_cleaning.unified_database import CSVToSQLiteProcessor

processor = CSVToSQLiteProcessor(
    input_folder="data_cleaning_fusion_datasets",
    output_folder="data/output"
)
processor.run()
```

### Example 2: Timestamp Standardization

```python
from basic_data_cleaning.time_standardization import TimeStandardizationProcessor

processor = TimeStandardizationProcessor(
    database_path="data/output/database/unified_database.db",
    timezone="America/New_York"
)
processor.run()
```

### Example 3: Map Matching

```python
from map_matching.mapmatching import MapMatchingProcessor

processor = MapMatchingProcessor(
    input_folder="data_cleaning_fusion_datasets",
    output_folder="data/output"
)
processor.run()
```

---

**Last Updated**: December 2025

