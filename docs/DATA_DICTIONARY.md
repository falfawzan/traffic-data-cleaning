# Data Dictionary

This document describes the schema and variables for all data sources used in the traffic data cleaning pipeline.

## Table of Contents

- [Waypoint Data](#waypoint-data)
- [Trip Path Data](#trip-path-data)
- [Sensor Data](#sensor-data)
- [TMC Speed Data](#tmc-speed-data)
- [Network Data](#network-data)
- [Output Data](#output-data)

## Waypoint Data

**Source**: Vendor A - Connected Vehicle Waypoints  
**File**: `data_cleaning_fusion_datasets/waypoint/waypoint.csv`  
**Input Records**: 19,471,725  
**Final Records**: 6,288,904 (map-matched)

### Schema

| Column Name | Type | Description | Units | Required |
|-------------|------|-------------|-------|----------|
| `journey_id` | String | Unique identifier for vehicle journey | - | Yes |
| `capture_time` | Integer | Unix timestamp of GPS capture | seconds | Yes |
| `latitude` | Float | GPS latitude coordinate | degrees | Yes |
| `longitude` | Float | GPS longitude coordinate | degrees | Yes |
| `speed_mph` | Float | Vehicle speed at capture time | mph | Yes |
| `fuzzed_point` | Boolean | Privacy-protected location flag | - | No |
| `ignition_status` | String | Vehicle ignition state | - | No |
| `heading_deg_north` | Float | Vehicle heading direction | degrees | No |
| `elevation_ft` | Float | Elevation above sea level | feet | No |
| `local_time` | String | Standardized local timestamp | ISO format | Generated |

### Notes

- **Collection Frequency**: Expected 3-second intervals
- **Coordinate System**: WGS84 (EPSG:4326)
- **Speed Unit**: Miles per hour (mph)
- **Timezone**: Converted to America/New_York (local time)

## Trip Path Data

**Source**: Vendor B - Trip Trajectories  
**File**: `data_cleaning_fusion_datasets/trip path/trajs.csv`  
**Input Records**: 8,356,493  
**Final Records**: 377,563 (corridor-filtered)

### Schema

| Column Name | Type | Description | Units | Required |
|-------------|------|-------------|-------|----------|
| `TripId` | String | Unique trip identifier | - | Yes |
| `DeviceId` | String | Device identifier | - | No |
| `ProviderId` | String | Data provider identifier | - | No |
| `TripTimezone` | String | Timezone for trip | - | Yes |
| `TrajIdx` | Integer | Trajectory segment index | - | No |
| `TrajRawDistanceM` | Float | Raw trajectory distance | meters | No |
| `TrajRawDurationMillis` | Integer | Raw trajectory duration | milliseconds | No |
| `SegmentId` | String | Road segment identifier | - | Yes |
| `SegmentIdx` | Integer | Segment index within trip | - | No |
| `LengthM` | Float | Segment length | meters | No |
| `CrossingStartOffsetM` | Float | Start offset within segment | meters | No |
| `CrossingEndOffsetM` | Float | End offset within segment | meters | No |
| `CrossingStartDateUtc` | String | Segment start time (UTC) | ISO 8601 | Yes |
| `CrossingEndDateUtc` | String | Segment end time (UTC) | ISO 8601 | Yes |
| `CrossingSpeedKph` | Float | Average speed through segment | km/h | Yes |
| `OnRoadNetworkSnapCount` | Integer | Network snap count | - | No |
| `ErrorCodes` | String | Error code flags | - | No |
| `CrossingStartDateLocal` | String | Standardized local start time | ISO format | Generated |
| `CrossingEndDateLocal` | String | Standardized local end time | ISO format | Generated |
| `CrossingSpeedMph` | Float | Speed converted to mph | mph | Generated |

### Notes

- **Speed Conversion**: Kph → Mph (multiply by 0.621371)
- **SegmentId Mapping**: Must map to GMNS links via `SegmentId_to_link.csv`
- **Corridor Filtering**: Only SegmentIds in corridor mapping are retained
- **Timezone**: Converted from UTC to local time (America/New_York)

## Sensor Data

**Source**: Loop Detector Sensors  
**File**: `data_cleaning_fusion_datasets/sensor/lane_readings.csv`  
**Records**: 895,982

### Schema

| Column Name | Type | Description | Units | Required |
|-------------|------|-------------|-------|----------|
| `zone_id` | String | Sensor zone identifier | - | Yes |
| `lane_number` | Integer | Lane number | - | Yes |
| `lane_id` | String | Unique lane identifier | - | Yes |
| `measurement_start` | String | Measurement start time | ISO format | Yes |
| `speed` | Float | Average speed | mph | Yes |
| `volume` | Integer | Vehicle count | vehicles | Yes |
| `occupancy` | Float | Lane occupancy | percent | Yes |
| `quality` | String | Data quality flag | - | No |

### Notes

- **Processing**: Timestamp standardization only (data already cleaned)
- **Use Case**: Validation and cross-source comparison

## TMC Speed Data

**Source**: Traffic Message Channel  
**File**: `data_cleaning_fusion_datasets/tmc_speed/Readings.csv`  
**Records**: 958,934

### Schema

| Column Name | Type | Description | Units | Required |
|-------------|------|-------------|-------|----------|
| `tmc_code` | String | TMC segment code | - | Yes |
| `measurement_tstamp` | String | Measurement timestamp | ISO format | Yes |
| `speed` | Float | Travel speed | mph | Yes |
| `historical_average_speed` | Float | Historical average | mph | No |
| `reference_speed` | Float | Reference speed | mph | No |
| `travel_time_seconds` | Float | Travel time | seconds | No |
| `confidence_score` | Float | Data confidence | 0-1 | No |
| `cvalue` | Float | C-value metric | - | No |

### Notes

- **Processing**: Timestamp standardization only (data already cleaned)
- **Use Case**: Validation and cross-source comparison

## Network Data

**Source**: GMNS-formatted Road Network  
**Study Area**: I-95 Corridor, Northern Virginia

### Node Data

**File**: `data_cleaning_fusion_datasets/network/node.csv`  
**Records**: 113 nodes

| Column Name | Type | Description | Required |
|-------------|------|-------------|----------|
| `node_id` | String | Unique node identifier | Yes |
| `x_coord` | Float | X coordinate (longitude) | Yes |
| `y_coord` | Float | Y coordinate (latitude) | Yes |
| `ctrl_type` | Integer | Control type (signal, stop, etc.) | No |
| `geometry` | WKT | Point geometry | Generated |

### Link Data

**File**: `data_cleaning_fusion_datasets/network/link.csv`  
**Records**: 132 links

| Column Name | Type | Description | Required |
|-------------|------|-------------|----------|
| `link_id` | String | Unique link identifier | Yes |
| `from_node_id` | String | Origin node ID | Yes |
| `to_node_id` | String | Destination node ID | Yes |
| `length` | Float | Link length | meters | No |
| `free_speed` | Float | Free-flow speed | mph | No |
| `lanes` | Integer | Number of lanes | No |
| `capacity` | Integer | Link capacity | vehicles/hour | No |
| `geometry` | WKT | Linestring geometry | Generated |

### SegmentId Mapping

**File**: `data_cleaning_fusion_datasets/network/SegmentId_to_link.csv`  
**Records**: 116 unique SegmentIds

| Column Name | Type | Description |
|-------------|------|-------------|
| `SegmentId` | String | Vendor SegmentId |
| `link_id` | String | GMNS link identifier |

**Note**: This mapping defines the study corridor. Only trip path records with SegmentIds in this file are retained.

## Output Data

### Cleaned Waypoint Data

**File**: `data/output/cleaned_data/waypoint_cleaned_mapmatched.csv`  
**Records**: 6,288,904

Contains all original waypoint columns plus:
- `link_id`: Assigned network link
- `from_node`: Link origin node
- `to_node`: Link destination node

### Cleaned Trip Path Data

**File**: `data/output/cleaned_data/trajs_cleaned.csv`  
**Records**: 377,563

Contains all original trip path columns with:
- Standardized timestamps (`CrossingStartDateLocal`, `CrossingEndDateLocal`)
- Converted speeds (`CrossingSpeedMph`)
- Only corridor SegmentIds (filtered)

### Quality Metrics

**Directory**: `data/output/quality_metrics/`

- `cleaning_impact_summary.csv`: Record counts and removal percentages
- `completeness_metrics.csv`: Completeness rates by column
- `speed_statistics.csv`: Speed distribution statistics
- `performance_metrics.csv`: Cross-source validation metrics (RMSE, MAPE, R², MAE)

### Visualizations

**Directory**: `data/output/figures/`

- `input_vs_cleaned_comparison.png`: Data volume comparison
- `speed_distribution_analysis.png`: Speed distribution analysis
- `cross_source_validation.png`: Cross-source validation scatter plot
- `completeness_analysis.png`: Completeness visualization

## Data Requirements

### Minimum Data Requirements

For the pipeline to run successfully, you need:

1. **Waypoint Data**: At least `journey_id`, `capture_time`, `latitude`, `longitude`
2. **Trip Path Data**: At least `TripId`, `SegmentId`, `CrossingStartDateUtc`, `CrossingSpeedKph`
3. **Network Data**: `node.csv` and `link.csv` with required fields
4. **SegmentId Mapping**: `SegmentId_to_link.csv` for corridor filtering

### Data Size Considerations

- **Large Datasets**: Use chunked processing (default: 100,000 rows per batch)
- **Memory Requirements**: ~2-3 GB RAM for processing
- **Storage**: ~4 GB for input data, ~1 GB for outputs

## Data Download

For large datasets, use the download script:

```bash
bash scripts/download_data.sh
```

Or manually download from the data source and place in `data_cleaning_fusion_datasets/` directory.

---

**Last Updated**: December 2025

