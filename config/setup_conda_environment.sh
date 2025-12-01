#!/bin/bash
# Setup Anaconda Environment for Data Cleaning Project

echo "============================================================"
echo "Setting up Anaconda Environment"
echo "============================================================"

# Navigate to project directory
cd "/Users/fawzanalfawzan/Documents/PhD/ASU/Cources/Traffic Simulation Modelling and Applications/Project"

# Create conda environment with Python 3.11 (more stable than 3.13)
echo ""
echo "📦 Creating conda environment 'data_cleaning'..."
conda create -n data_cleaning python=3.11 -y

# Activate environment
echo ""
echo "🔄 Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate data_cleaning

# Install core packages
echo ""
echo "📥 Installing packages..."
pip install pandas==2.2.3
pip install numpy==2.2.3
pip install matplotlib==3.10.1
pip install scipy==1.15.2
pip install seaborn==0.13.2
pip install pytz==2024.2
pip install Shapely==2.0.7
pip install geopy==2.4.1
pip install Pillow==11.1.0
pip install networkx==3.4.2
pip install chardet
pip install geopandas

# Install Jupyter
echo ""
echo "📓 Installing Jupyter..."
pip install jupyter ipython ipykernel

# Register kernel with Jupyter
echo ""
echo "🔧 Registering kernel with Jupyter..."
python -m ipykernel install --user --name data_cleaning --display-name "Python (data_cleaning)"

echo ""
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "To use this environment:"
echo "  1. conda activate data_cleaning"
echo "  2. jupyter notebook"
echo "  3. Select kernel: 'Python (data_cleaning)'"
echo ""

