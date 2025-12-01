# Traffic Data Cleaning for Simulation Model Calibration

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive data cleaning pipeline for multi-source traffic data to prepare it for traffic simulation model calibration. This project implements **Part 2: Data Cleaning** within the Architecture Alphabet framework for transportation modeling, focusing on the I-95 Corridor in Northern Virginia.

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Data Sources](#data-sources)
- [Methodology](#methodology)
- [Results](#results)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## 🎯 Overview

This project provides a reproducible pipeline for cleaning and validating multi-source traffic data from GPS waypoints, trip trajectories, loop detectors, Traffic Message Channel (TMC) data, and origin-destination matrices. The pipeline follows FHWA guidelines and produces high-quality datasets ready for integration into the Architecture Alphabet framework.

### Key Results

- **Data Quality**: 100% completeness in final corridor datasets for all critical columns
- **Network Alignment**: 100% of final data aligned with I-95 corridor network
- **Cross-Source Validation**: R² = 0.67, RMSE = 5.78 mph between waypoint and trip path data
- **Final Datasets**: 6.3 million map-matched waypoint records and 377K trip path records
- **Processing Efficiency**: Chunked processing enabled handling datasets 10x larger than available RAM

## ✨ Key Features

- **Six-Step Cleaning Pipeline**: Timestamp standardization, duplicate removal, outlier detection, error removal, map matching, and filtered export
- **Memory-Efficient Processing**: Chunked processing for large datasets (27.8M+ records)
- **Corridor-Specific Filtering**: Network-aligned data for focused study area analysis
- **Cross-Source Validation**: Systematic comparison and validation across data sources
- **Comprehensive Quality Metrics**: Completeness, accuracy, consistency, and spatial alignment
- **Reproducible Workflow**: Well-documented Jupyter notebooks with step-by-step explanations

## 🚀 Installation

### Prerequisites

- **Python**: 3.11 or higher
- **Anaconda/Miniconda**: For environment management (recommended)
- **Git**: For cloning the repository

### Option 1: Using Conda (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd Project

# Create conda environment
conda env create -f config/environment.yml
conda activate data_cleaning

# Register Jupyter kernel
python -m ipykernel install --user --name data_cleaning --display-name "Python (data_cleaning)"

# Verify installation
python -c "import pandas, numpy, sqlite3, geopandas; print('✅ All packages installed')"
```

### Option 2: Using pip

```bash
# Clone the repository
git clone <repository-url>
cd Project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import pandas, numpy, sqlite3, geopandas; print('✅ All packages installed')"
```

### Option 3: Using Docker (Optional)

```bash
# Build Docker image
docker build -t traffic-data-cleaning .

# Run container
docker run -p 8888:8888 -v $(pwd):/workspace traffic-data-cleaning
```

## 🏃 Quick Start

### 1. Prepare Data

Download or place your data files in the `data_cleaning_fusion_datasets/` directory following this structure:

```
data_cleaning_fusion_datasets/
├── waypoint/
│   └── waypoint.csv
├── trip path/
│   ├── trajs.csv
│   └── TripBulkReportTrajectoriesHeaders.csv
├── network/
│   ├── node.csv
│   ├── link.csv
│   ├── SegmentId_to_link.csv
│   └── shp/  (shapefiles)
├── sensor/
│   └── lane_readings.csv
├── tmc_speed/
│   └── Readings.csv
└── od/ (if available)
```

**Note**: For large datasets, use the download scripts in `scripts/download_data.sh` or see [Data Dictionary](docs/DATA_DICTIONARY.md) for data requirements.

### 2. Run Data Cleaning Pipeline

```bash
# Start Jupyter
jupyter notebook

# Open and run:
# notebooks/Data_Cleaning_Pipeline.ipynb
```

**Expected Runtime**: 2-4 hours depending on data size and hardware

### 3. Run Analysis and Visualization

```bash
# Open and run:
# notebooks/Data_Cleaning_Analysis_Visualization.ipynb
```

**Expected Runtime**: 30-60 minutes

### 4. View Results

All outputs are saved to `data/output/`:
- **Cleaned Data**: `data/output/cleaned_data/`
- **Quality Metrics**: `data/output/quality_metrics/`
- **Visualizations**: `data/output/figures/`
- **Database**: `data/output/database/unified_database.db`

## 📁 Project Structure

```
Project/
├── notebooks/                          # Jupyter notebooks
│   ├── Data_Cleaning_Pipeline.ipynb    # Main cleaning pipeline
│   └── Data_Cleaning_Analysis_Visualization.ipynb  # Analysis and visualization
│
├── src/                                # Source code modules
│   ├── basic_data_cleaning/            # Core cleaning modules
│   │   ├── unified_database.py        # Database creation
│   │   ├── time_standardization.py    # Timestamp conversion
│   │   └── basic_data_cleaning.py    # Basic cleaning operations
│   ├── map_matching/                   # Map matching modules
│   │   └── mapmatching.py             # gotrackit integration
│   └── utils.py                        # Utility functions
│
├── data/                               # Data directory
│   ├── output/                         # Generated outputs (gitignored)
│   │   ├── cleaned_data/              # Final cleaned datasets
│   │   ├── database/                   # SQLite database
│   │   ├── figures/                    # Visualization figures
│   │   └── quality_metrics/            # Quality assessment metrics
│   └── sample/                         # Sample datasets (for testing)
│
├── data_cleaning_fusion_datasets/      # Input data (gitignored)
│   ├── waypoint/
│   ├── trip path/
│   ├── network/
│   ├── sensor/
│   └── tmc_speed/
│
├── scripts/                            # Utility scripts
│   ├── download_data.sh               # Data download script
│   └── validate_outputs.py            # Output validation
│
├── tests/                              # Unit tests
│   ├── test_unified_database.py
│   ├── test_time_standardization.py
│   └── test_map_matching.py
│
├── docs/                               # Documentation
│   ├── DATA_DICTIONARY.md             # Data schema and variables
│   ├── API_DOCUMENTATION.md           # API reference
│   └── TROUBLESHOOTING.md             # Common issues and solutions
│
├── config/                             # Configuration files
│   ├── environment.yml                # Conda environment
│   └── requirements.txt               # pip requirements
│
├── .gitignore                         # Git ignore rules
├── README.md                          # This file
├── LICENSE                            # License file
└── FINAL_REPORT.md                    # Comprehensive report
```

## 📊 Data Sources

The pipeline processes five distinct data sources:

1. **Waypoint Data** (Vendor A): GPS tracking points from connected vehicles
   - Input: 19.5M records
   - Final: 6.3M map-matched records
   - Attributes: journey_id, latitude, longitude, speed_mph, capture_time

2. **Trip Path Data** (Vendor B): Trajectory segments from connected vehicles
   - Input: 8.4M records
   - Final: 377K records (corridor-filtered)
   - Attributes: TripId, SegmentId, CrossingSpeedKph, timestamps

3. **Sensor Data**: Loop detector readings
   - Records: 895K readings
   - Attributes: zone_id, lane_number, speed, volume, occupancy

4. **TMC Speed Data**: Traffic Message Channel speed reports
   - Records: 958K measurements
   - Attributes: tmc_code, speed, travel_time_seconds

5. **Network Data**: GMNS-formatted road network
   - Nodes: 113 nodes
   - Links: 132 links
   - Study Area: I-95 Corridor, Northern Virginia

See [Data Dictionary](docs/DATA_DICTIONARY.md) for detailed schema.

## 🔬 Methodology

### Data Cleaning Pipeline

The pipeline implements six sequential steps following FHWA guidelines:

1. **Step 0: Initial Data Quality Check and Formatting**
   - Scan data directory structure
   - Create unified SQLite database
   - Handle encoding issues automatically

2. **Step 1: Timestamp Standardization**
   - Convert all timestamps to local time (America/New_York)
   - Handle multiple formats (ISO 8601, Unix timestamps)
   - Standardize speed units (kph → mph)

3. **Step 2: Duplicate Removal**
   - Remove duplicate waypoint records (journey_id, capture_time)
   - Remove duplicate trip path segments (TripId, SegmentId, timestamp)

4. **Step 3: Outlier Removal**
   - Rule-based filtering: Remove invalid speeds (≤0 or >100 mph)
   - Statistical outlier detection: IQR method with domain constraints

5. **Step 4: Error Data Removal**
   - Filter trip path by corridor SegmentIds (SegmentId_to_link.csv)
   - Remove records with missing required fields
   - Validate network alignment

6. **Step 5: Waypoint Based Map Matching**
   - Align GPS coordinates to road network using `gotrackit`
   - Export map-matched waypoints to `waypoint_cleaned_mapmatched.csv`

### Statistical Methods

- **Completeness**: $C = \frac{N_{\text{non-missing}}}{N_{\text{total}}} \times 100\%$
- **Outlier Detection**: IQR method with bounds: $[Q_1 - 1.5 \times \text{IQR}, Q_3 + 1.5 \times \text{IQR}]$
- **Cross-Source Validation**: RMSE, MAPE, R², MAE metrics

## 📈 Results

### Data Quality Metrics

| Data Source | Input Records | Final Records | Completeness | Retention Rate |
|-------------|---------------|---------------|--------------|----------------|
| Waypoint | 19,471,725 | 6,288,904 | 100% | 32.30% |
| Trip Path | 8,356,493 | 377,563 | 100% | 4.52% |

### Speed Statistics (Final Corridor Datasets)

| Data Source | Mean (mph) | Median (mph) | Std Dev (mph) |
|-------------|------------|--------------|---------------|
| Waypoint Map-Matched | 47.53 | 52.00 | 23.00 |
| Trajs (cleaned + mapped) | 54.98 | 58.58 | 16.23 |

### Cross-Source Validation

| Metric | Value | Interpretation |
|--------|-------|----------------|
| RMSE | 5.78 mph | Acceptable for traffic speed data |
| MAPE | 940.40% | High due to low-speed waypoint values |
| R² | 0.67 | Moderate positive correlation |
| MAE | 4.10 mph | Reasonable cross-source difference |

See [FINAL_REPORT.md](FINAL_REPORT.md) for comprehensive results and analysis.

## 📚 Documentation

- **[Data Dictionary](docs/DATA_DICTIONARY.md)**: Complete schema and variable descriptions
- **[API Documentation](docs/API_DOCUMENTATION.md)**: Function and class reference
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)**: Common issues and solutions
- **[Comprehensive Report](FINAL_REPORT.md)**: Full methodology, results, and analysis

## 🧪 Testing

Run unit tests to verify installation and functionality:

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_unified_database.py

# Run with coverage
pytest --cov=src tests/
```

## 🏗️ Architecture Alphabet Integration

The cleaned datasets are ready for integration into all Architecture Alphabet classes:

- **Class A (Arc-based)**: Network-aligned data for time-space network models
- **Class B (Backpropagation)**: High-quality data for deep learning training
- **Class C (Column-based)**: Validated trajectories for path flow representation
- **Class E (Eigen/Tensor)**: Consistent multi-dimensional data for tensor construction

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 style guide
- Include docstrings for all functions and classes
- Add unit tests for new features
- Update documentation as needed

## 📝 License

This project is part of a research course assignment. See [LICENSE](LICENSE) for details.

## 👤 Contact

**Author**: Fawzan Alfawzan  
**Course**: Traffic Simulation Modelling and Applications  
**Date**: December 2025

For questions or issues:
- Open an issue on GitHub
- Refer to [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- Check [Comprehensive Report](FINAL_REPORT.md) for detailed methodology

## 🙏 Acknowledgments

- Federal Highway Administration (FHWA) for data cleaning framework
- Architecture Alphabet framework by Zhou et al.
- `gotrackit` library for map matching capabilities
- USDOT JPO CodeHub for data cleaning and fusion tool

---

**Last Updated**: December 2025  
**Status**: Production Ready
