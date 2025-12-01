#!/bin/bash

# Data Download Script for Traffic Data Cleaning Pipeline
# This script helps download or prepare data for the pipeline

set -e

echo "=========================================="
echo "Data Download Script"
echo "=========================================="
echo ""

# Create data directory structure
echo "Creating data directory structure..."
mkdir -p data_cleaning_fusion_datasets/waypoint
mkdir -p data_cleaning_fusion_datasets/"trip path"
mkdir -p data_cleaning_fusion_datasets/network/shp
mkdir -p data_cleaning_fusion_datasets/sensor
mkdir -p data_cleaning_fusion_datasets/tmc_speed

echo "✅ Directory structure created"
echo ""

# Check if data files exist
echo "Checking for existing data files..."

if [ -f "data_cleaning_fusion_datasets/waypoint/waypoint.csv" ]; then
    echo "✅ Waypoint data found"
else
    echo "⚠️  Waypoint data not found"
    echo "   Please place waypoint.csv in data_cleaning_fusion_datasets/waypoint/"
fi

if [ -f "data_cleaning_fusion_datasets/trip path/trajs.csv" ]; then
    echo "✅ Trip path data found"
else
    echo "⚠️  Trip path data not found"
    echo "   Please place trajs.csv in data_cleaning_fusion_datasets/trip path/"
fi

if [ -f "data_cleaning_fusion_datasets/network/node.csv" ] && [ -f "data_cleaning_fusion_datasets/network/link.csv" ]; then
    echo "✅ Network data found"
else
    echo "⚠️  Network data not found"
    echo "   Please place node.csv and link.csv in data_cleaning_fusion_datasets/network/"
fi

if [ -f "data_cleaning_fusion_datasets/network/SegmentId_to_link.csv" ]; then
    echo "✅ SegmentId mapping found"
else
    echo "⚠️  SegmentId mapping not found"
    echo "   Please place SegmentId_to_link.csv in data_cleaning_fusion_datasets/network/"
fi

echo ""
echo "=========================================="
echo "Data Preparation Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Place your data files in the appropriate directories"
echo "2. Run the data cleaning pipeline:"
echo "   jupyter notebook notebooks/Data_Cleaning_Pipeline.ipynb"
echo ""

