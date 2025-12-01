# Troubleshooting Guide

Common issues and solutions for the traffic data cleaning pipeline.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Data Loading Issues](#data-loading-issues)
- [Memory Issues](#memory-issues)
- [Map Matching Issues](#map-matching-issues)
- [Database Issues](#database-issues)
- [Jupyter Notebook Issues](#jupyter-notebook-issues)

## Installation Issues

### Issue: Package Installation Fails

**Symptoms**: `pip install` or `conda install` fails with dependency conflicts.

**Solutions**:
1. Use conda environment (recommended):
   ```bash
   conda env create -f config/environment.yml
   conda activate data_cleaning
   ```

2. If using pip, upgrade pip first:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. For geopandas issues, install via conda:
   ```bash
   conda install -c conda-forge geopandas
   ```

### Issue: gotrackit Installation Fails

**Symptoms**: `ImportError: No module named 'gotrackit'`

**Solutions**:
1. Install via pip:
   ```bash
   pip install gotrackit==0.3.17
   ```

2. If still fails, check Python version (requires 3.8+):
   ```bash
   python --version
   ```

## Data Loading Issues

### Issue: File Not Found Errors

**Symptoms**: `FileNotFoundError` when running pipeline.

**Solutions**:
1. Verify data directory structure:
   ```bash
   ls -la data_cleaning_fusion_datasets/
   ```

2. Check file paths in notebook Cell 1 (Setup and Configuration)

3. Use absolute paths if relative paths fail:
   ```python
   DATA_PATH = Path("/absolute/path/to/data_cleaning_fusion_datasets")
   ```

### Issue: Encoding Errors

**Symptoms**: `UnicodeDecodeError` when reading CSV files.

**Solutions**:
1. The pipeline automatically detects encoding using `chardet`
2. If issues persist, manually specify encoding:
   ```python
   df = pd.read_csv(filepath, encoding='utf-8')  # or 'latin-1', 'cp1252'
   ```

### Issue: Missing Column Headers

**Symptoms**: Data loads but columns are numbered (0, 1, 2, ...) instead of named.

**Solutions**:
1. For trip path data, ensure `TripBulkReportTrajectoriesHeaders.csv` is present
2. Check that header file is in the same directory as `trajs.csv`
3. Verify header file format matches data file

## Memory Issues

### Issue: Memory Exhaustion During Processing

**Symptoms**: `MemoryError` or system becomes unresponsive.

**Solutions**:
1. The pipeline uses chunked processing (100,000 rows per batch) by default
2. Reduce batch size if needed:
   ```python
   CHUNK_SIZE = 50000  # Reduce from 100000
   ```

3. Process one data source at a time
4. Close other applications to free memory
5. Use a machine with more RAM (recommended: 8GB+)

### Issue: Slow Processing

**Symptoms**: Pipeline takes very long to run.

**Solutions**:
1. This is normal for large datasets (27.8M+ records)
2. Expected runtime: 2-4 hours for full pipeline
3. Use SSD storage for faster I/O
4. Close unnecessary applications

## Map Matching Issues

### Issue: Map Matching Fails with KeyError

**Symptoms**: `KeyError: 'from_node_id'` or similar field errors.

**Solutions**:
1. This is handled automatically in the code (CSV-based column restoration)
2. Ensure network CSV files have required columns:
   - `node.csv`: `node_id`, `x_coord`, `y_coord`
   - `link.csv`: `link_id`, `from_node_id`, `to_node_id`

3. Check shapefile column truncation (code handles this automatically)

### Issue: Low Map Matching Rate

**Symptoms**: Only small percentage of waypoints matched.

**Solutions**:
1. This is expected - typical match rates are 50-60%
2. Unmatched points may be:
   - Outside network buffer (beyond 50m from links)
   - In parking lots or driveways
   - GPS errors or signal loss

3. Increase GPS buffer if needed (default: 50m):
   ```python
   gps_buffer=75.0  # Increase from 50.0
   ```

### Issue: gotrackit AssertionError

**Symptoms**: `AssertionError: the Link layer lacks the following fields`

**Solutions**:
1. Code automatically renames fields to match gotrackit requirements
2. Verify network files are in GMNS format
3. Check that all referenced nodes exist in node layer

## Database Issues

### Issue: Database Locked Error

**Symptoms**: `sqlite3.OperationalError: database is locked`

**Solutions**:
1. Close other connections to the database
2. Restart Jupyter kernel
3. Check for database journal files and remove if corrupted:
   ```bash
   rm data/output/database/*.db-journal
   rm data/output/database/*.db-wal
   ```

### Issue: Database File Too Large

**Symptoms**: Database file grows very large (>5GB).

**Solutions**:
1. This is normal for large datasets
2. Database is gitignored (won't be committed)
3. Use `VACUUM` to reclaim space:
   ```python
   conn.execute("VACUUM;")
   ```

## Jupyter Notebook Issues

### Issue: Kernel Not Found

**Symptoms**: Jupyter shows "No kernel available" or kernel dies.

**Solutions**:
1. Register kernel:
   ```bash
   python -m ipykernel install --user --name data_cleaning --display-name "Python (data_cleaning)"
   ```

2. Select correct kernel in notebook: Kernel → Change Kernel → Python (data_cleaning)

3. Restart kernel: Kernel → Restart Kernel

### Issue: Import Errors in Notebook

**Symptoms**: `ModuleNotFoundError` when running notebook cells.

**Solutions**:
1. Verify environment is activated:
   ```bash
   conda activate data_cleaning
   ```

2. Check that `sys.path` includes source code directory (Cell 1 should handle this)

3. Verify source code structure:
   ```bash
   ls -la data-cleaning-and-fusion-tool/Code/src/
   ```

### Issue: Notebook Cells Hang

**Symptoms**: Cell execution never completes.

**Solutions**:
1. Check if process is actually running (CPU usage)
2. For map matching, this is normal - can take hours
3. Use progress bars (`tqdm`) to monitor progress
4. Interrupt and restart if truly hung

## General Issues

### Issue: Path Errors on Windows

**Symptoms**: Path-related errors on Windows.

**Solutions**:
1. Use `Path` from `pathlib` (already in code)
2. Use forward slashes or `os.path.join()`
3. Avoid spaces in directory names

### Issue: Permission Errors

**Symptoms**: `PermissionError` when writing files.

**Solutions**:
1. Check file/directory permissions
2. Run with appropriate user permissions
3. Ensure output directories are writable

## Getting Help

If issues persist:

1. Check [Data Dictionary](DATA_DICTIONARY.md) for data requirements
2. Review [Comprehensive Report](../FINAL_REPORT.md) for methodology details
3. Verify all prerequisites are installed
4. Check error messages carefully - they often indicate the issue
5. Review notebook cell outputs for specific error details

---

**Last Updated**: December 2025

