#!/bin/bash
# Jupyter Notebook Launcher for data_cleaning environment

# Set up conda path
export PATH="/opt/anaconda3/bin:$PATH"

# Source conda initialization
source /opt/anaconda3/etc/profile.d/conda.sh

# Activate the environment
conda activate data_cleaning

# Navigate to project directory
cd "/Users/fawzanalfawzan/Documents/PhD/ASU/Cources/Traffic Simulation Modelling and Applications/Project"

# Start Jupyter Notebook
echo "🚀 Starting Jupyter Notebook..."
echo "📁 Working directory: $(pwd)"
echo "🐍 Environment: data_cleaning"
echo ""
jupyter notebook

