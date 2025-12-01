import os
import sqlite3
import platform
import sys
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
from shapely.geometry import Point, LineString
from shapely.wkt import loads
from gotrackit.map.Net import Net
from gotrackit.MapMatch import MapMatch
from basic_data_cleaning.unified_database import CSVToSQLiteProcessor


class MapMatchingProcessor:
    def __init__(self, input_folder, output_folder, stop_event=None, progress_callback=None, progress_output=None):
        """Initializes paths for input and output folders."""
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.database_path = os.path.join(output_folder, "database", "unified_database.db")

        # Paths for network files
        self.node_csv_path = os.path.join(input_folder, "network", "node.csv")
        self.link_csv_path = os.path.join(input_folder, "network", "link.csv")
        self.node_shp_path = os.path.join(input_folder, "network", "shp", "node.shp")
        self.link_shp_path = os.path.join(input_folder, "network", "shp", "link.shp")

        os.makedirs(os.path.dirname(self.node_shp_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.link_shp_path), exist_ok=True)

        if stop_event is None:
            print("WARNING: stop_event is None, stopping may not work!")
        self.stop_event = stop_event
        self.progress_callback = progress_callback
        # self.progress_output = progress_output
        self.progress_output = progress_output if progress_output else sys.stdout

    def process_network(self):
        """
        Converts node/link CSV files into Shapefiles for map matching.
        
        According to gotrackit documentation:
        - Node layer: Must have node_id and geometry (POINT), coordinate system EPSG:4326
        - Link layer: Must have link_id, from_node_id, to_node_id, and geometry (LINESTRING), coordinate system EPSG:4326
        - Reference: https://gotrackitdocs.readthedocs.io/en/latest/HowToUse.html#relationship-between-node-layer-and-link-layer
        """
        print("Processing network data...")

        # Process Node Data
        nodes_df = pd.read_csv(self.node_csv_path)

        # Verify required columns exist
        if "node_id" not in nodes_df.columns:
            raise ValueError("Node CSV must contain 'node_id' column")
        if "x_coord" not in nodes_df.columns or "y_coord" not in nodes_df.columns:
            raise ValueError("Node CSV must contain 'x_coord' and 'y_coord' columns")

        # Create GeoDataFrame for nodes with POINT geometry
        # Note: gotrackit expects node_id and geometry fields
        nodes_gdf = gpd.GeoDataFrame(
            nodes_df,
            geometry=[Point(xy) for xy in zip(nodes_df["x_coord"], nodes_df["y_coord"])],
            crs="EPSG:4326"  # Required by gotrackit
        )
        
        # Ensure node_id is preserved (gotrackit requirement)
        if "node_id" not in nodes_gdf.columns:
            nodes_gdf["node_id"] = nodes_df["node_id"]

        # Save nodes to a Shapefile
        nodes_gdf.to_file(self.node_shp_path, driver="ESRI Shapefile")
        print(f"   ✅ Node shapefile created: {len(nodes_gdf)} nodes")

        # Process Link Data
        links_df = pd.read_csv(self.link_csv_path)

        # Verify required columns exist
        if "link_id" not in links_df.columns:
            raise ValueError("Link CSV must contain 'link_id' column")
        if "from_node_id" not in links_df.columns or "to_node_id" not in links_df.columns:
            raise ValueError("Link CSV must contain 'from_node_id' and 'to_node_id' columns")

        # gotrackit expects from_node_id and to_node_id (not from_node/to_node)
        # Keep original field names as gotrackit's Net class handles them correctly

        # Create a dictionary mapping node_id to (longitude, latitude) for fallback
        node_dict = nodes_df.set_index("node_id")[["x_coord", "y_coord"]].to_dict("index")

        # Function to create a LineString from from_node_id and to_node_id (fallback only)
        def create_linestring_fallback(row):
            from_node_id = row.get("from_node_id")
            to_node_id = row.get("to_node_id")
            if from_node_id and to_node_id:
                from_node = node_dict.get(from_node_id)
                to_node = node_dict.get(to_node_id)
            if from_node and to_node:
                    return LineString([(from_node["x_coord"], from_node["y_coord"]), 
                                      (to_node["x_coord"], to_node["y_coord"])])
            return None

        # Process geometry: prioritize existing LINESTRING geometry from CSV
        if "geometry" in links_df.columns:
            try:
                # Try to load WKT geometry (most accurate)
                links_df["geometry"] = links_df["geometry"].apply(loads)
                print("   ✅ Using existing LINESTRING geometry from CSV")
            except Exception as e:
                print(f"   ⚠️  Could not parse geometry column, creating from nodes: {e}")
                # Fallback: create LineString from node coordinates
                links_df["geometry"] = links_df.apply(create_linestring_fallback, axis=1)
        else:
            # No geometry column: create LineString from node coordinates
            print("   ⚠️  No geometry column found, creating LineString from node coordinates")
            links_df["geometry"] = links_df.apply(create_linestring_fallback, axis=1)

        # Remove links with invalid geometry
        links_df = links_df.dropna(subset=["geometry"])
        
        # Verify geometry types are LINESTRING
        invalid_geom = links_df[~links_df["geometry"].apply(lambda x: isinstance(x, LineString))]
        if len(invalid_geom) > 0:
            print(f"   ⚠️  Warning: {len(invalid_geom)} links have non-LINESTRING geometry, removing them")
            links_df = links_df[links_df["geometry"].apply(lambda x: isinstance(x, LineString))]

        # Create GeoDataFrame for links
        # gotrackit expects: link_id, from_node_id, to_node_id, geometry
        links_gdf = gpd.GeoDataFrame(
            links_df,
            geometry="geometry",
            crs="EPSG:4326"  # Required by gotrackit
        )
        
        # Ensure required fields are preserved
        required_link_fields = ["link_id", "from_node_id", "to_node_id"]
        for field in required_link_fields:
            if field not in links_gdf.columns:
                raise ValueError(f"Link GeoDataFrame must contain '{field}' column after processing")

        # Save links to a Shapefile
        links_gdf.to_file(self.link_shp_path, driver="ESRI Shapefile")
        print(f"   ✅ Link shapefile created: {len(links_gdf)} links")
        print("Network processing completed")

    def load_gps_data(self):
        """
        Loads GPS data from the SQLite database.
        
        According to gotrackit documentation:
        - Required fields: agent_id, time, lng, lat (NOT longitude/latitude)
        - Time column must be sortable and unique (no duplicate timestamps for same agent)
        - Coordinate system should be EPSG:4326 (WGS84)
        - Reference: https://gotrackitdocs.readthedocs.io/en/latest/HowToUse.html#relationship-between-node-layer-and-link-layer
        """
        print("Loading Waypoint Data from SQLite database...")
        conn = sqlite3.connect(self.database_path)
        
        # Load GPS data with gotrackit-required field names: agent_id, time, lng, lat
        # gotrackit specifically requires 'lng' and 'lat' (not 'longitude' and 'latitude')
        gps_df = pd.read_sql(
            "SELECT journey_id AS agent_id, longitude AS lng, latitude AS lat, local_time AS time FROM waypoint",
            conn
        )
        conn.close()
        
        # Verify required fields (gotrackit expects: agent_id, time, lng, lat)
        required_fields = ["agent_id", "lng", "lat", "time"]
        missing_fields = [f for f in required_fields if f not in gps_df.columns]
        if missing_fields:
            raise ValueError(f"GPS data missing required fields: {missing_fields}")
        
        # Remove rows with missing coordinates or time
        before = len(gps_df)
        gps_df = gps_df.dropna(subset=["agent_id", "lng", "lat", "time"])
        after = len(gps_df)
        if before != after:
            print(f"   ⚠️  Removed {before - after} rows with missing GPS data")
        
        # Sort by agent_id and time (required by gotrackit)
        gps_df = gps_df.sort_values(["agent_id", "time"]).reset_index(drop=True)
        
        # Check for duplicate timestamps per agent (gotrackit warning)
        duplicates = gps_df.groupby(["agent_id", "time"]).size()
        duplicate_count = (duplicates > 1).sum()
        if duplicate_count > 0:
            print(f"   ⚠️  Warning: {duplicate_count} agent-time combinations have duplicate timestamps")
            print(f"      This may cause matching issues. Consider removing duplicates.")
        
        print(f"   ✅ Waypoint Data loaded: {len(gps_df):,} points from {gps_df['agent_id'].nunique():,} agents")
        print(f"   ✅ GPS data columns: {list(gps_df.columns)} (gotrackit format: agent_id, time, lng, lat)")
        return gps_df

    def update_progress(self, message, progress=None):
        """Updates the GUI progress bar if a callback is provided."""
        if self.progress_callback:
            self.progress_callback(message, progress)

    def perform_map_matching(self):
        """Runs the map matching process using the processed network and GPS data."""
        print("Performing Map Matching...")

        # Read CSV files first (source of truth for column names)
        # Shapefiles truncate field names to 10 characters, so we rebuild from CSV
        print("   📋 Reading network data from CSV (avoiding shapefile truncation issues)...")
        links_df = pd.read_csv(self.link_csv_path)
        nodes_df = pd.read_csv(self.node_csv_path)
        
        # Verify node-link relationship
        # gotrackit automatically establishes the relationship between node and link layers
        # based on from_node_id and to_node_id in links matching node_id in nodes
        # Reference: https://gotrackitdocs.readthedocs.io/en/latest/HowToUse.html#relationship-between-node-layer-and-link-layer
        link_node_ids = set(links_df["from_node_id"].unique()) | set(links_df["to_node_id"].unique())
        node_ids = set(nodes_df["node_id"].unique())
        missing_nodes = link_node_ids - node_ids
        
        if missing_nodes:
            print(f"   ⚠️  Warning: {len(missing_nodes)} node IDs referenced in links but not found in node layer")
            print(f"      This may cause network connectivity issues")
        else:
            print(f"   ✅ All {len(link_node_ids)} referenced nodes found in node layer")
        
        # Read shapefiles to get geometry
        link_shp = gpd.read_file(self.link_shp_path)
        node_shp = gpd.read_file(self.node_shp_path)
        
        print(f"   📋 Link shapefile columns: {list(link_shp.columns)}")
        print(f"   📋 Node shapefile columns: {list(node_shp.columns)}")
        
        # Rebuild GeoDataFrames by combining CSV data (correct column names) with shapefile geometry
        # This ensures we have all required columns with correct names
        print("   🔧 Rebuilding GeoDataFrames with correct column names...")
        
        # For links: merge CSV data with shapefile geometry
        # Match by index (shapefiles should be in same order as CSV)
        link = link_shp.copy()
        link = link.reset_index(drop=True)
        links_df = links_df.reset_index(drop=True)
        
        # Ensure we have the same number of rows
        if len(link) != len(links_df):
            print(f"   ⚠️  Warning: Shapefile has {len(link)} links, CSV has {len(links_df)} links")
            # Take the minimum
            min_len = min(len(link), len(links_df))
            link = link.iloc[:min_len].copy()
            links_df = links_df.iloc[:min_len].copy()
        
        # Add required columns from CSV
        link["link_id"] = links_df["link_id"].values
        link["from_node_id"] = links_df["from_node_id"].values
        link["to_node_id"] = links_df["to_node_id"].values
        
        # For nodes: merge CSV data with shapefile geometry
        node = node_shp.copy()
        node = node.reset_index(drop=True)
        nodes_df = nodes_df.reset_index(drop=True)
        
        # Ensure we have the same number of rows
        if len(node) != len(nodes_df):
            print(f"   ⚠️  Warning: Shapefile has {len(node)} nodes, CSV has {len(nodes_df)} nodes")
            # Take the minimum
            min_len = min(len(node), len(nodes_df))
            node = node.iloc[:min_len].copy()
            nodes_df = nodes_df.iloc[:min_len].copy()
        
        # Add required column from CSV
        node["node_id"] = nodes_df["node_id"].values
        
        # Final validation - ensure required columns exist
        required_link_cols = ["link_id", "from_node_id", "to_node_id"]
        missing_link_cols = [col for col in required_link_cols if col not in link.columns]
        if missing_link_cols:
            raise ValueError(f"Required link columns missing: {missing_link_cols}")
        
        if "node_id" not in node.columns:
            raise ValueError("Required column 'node_id' not found in node GeoDataFrame")
        
        print("   ✅ All required columns restored successfully")
        
        # gotrackit expects specific column names: from_node, to_node, dir (not from_node_id, to_node_id, directed)
        # Rename columns to match gotrackit requirements
        print("   🔧 Renaming columns to match gotrackit requirements...")
        
        # Rename link columns
        if "from_node_id" in link.columns:
            link = link.rename(columns={"from_node_id": "from_node"})
            print("   ✅ Renamed 'from_node_id' to 'from_node'")
        
        if "to_node_id" in link.columns:
            link = link.rename(columns={"to_node_id": "to_node"})
            print("   ✅ Renamed 'to_node_id' to 'to_node'")
        
        # Handle 'dir' column (gotrackit expects 'dir', not 'directed')
        if "directed" in link.columns:
            link = link.rename(columns={"directed": "dir"})
            print("   ✅ Renamed 'directed' to 'dir'")
        elif "dir" not in link.columns:
            # If neither exists, create 'dir' column (default to 1 for directed)
            link["dir"] = 1
            print("   ✅ Created 'dir' column (default=1)")
        
        # Final check for gotrackit required columns
        required_gotrackit_cols = ["from_node", "to_node", "dir"]
        missing_cols = [col for col in required_gotrackit_cols if col not in link.columns]
        if missing_cols:
            raise ValueError(f"gotrackit requires these link columns: {missing_cols}")
        
        print(f"   ✅ Link GeoDataFrame: {len(link)} links with required columns {required_gotrackit_cols}")
        print(f"   ✅ Node GeoDataFrame: {len(node)} nodes with node_id column")

        # Initialize the network for map matching
        # not_conn_cost: penalty for path discontinuity (higher = greater penalty)
        # Default is reasonable, but can be adjusted based on network characteristics
        my_net = Net(link_gdf=link, node_gdf=node, not_conn_cost=2400)
        my_net.init_net()
        print("   ✅ Network initialized and topology built")

        if self.stop_event and self.stop_event.is_set():
            print("Stopping before loading waypoint data...")
            return

        # Load GPS data
        gps_df = self.load_gps_data()

        # Count the total number of agents (for progress tracking)
        total_agents = gps_df["agent_id"].nunique()

        print(f"Total agents to process: {total_agents}")

        # Initialize MapMatching with parameters
        # Parameters aligned with gotrackit documentation recommendations
        # Reference: https://gotrackitdocs.readthedocs.io/en/latest/HowToUse.html
        mpm = MapMatch(
            net=my_net, 
            flag_name='agent',  # Group by agent_id
            time_format='%Y-%m-%d %H:%M:%S',  # Match local_time format
            gps_buffer=50,  # Buffer distance (meters) for candidate link search - increased from 12 for better coverage
            top_k=10,  # Number of candidate links to consider
            dense_gps=False,  # GPS data is not pre-densified
            use_heading_inf=True,  # Use heading information for better matching
            omitted_l=6.0,  # Minimum link length to consider (meters)
            del_dwell=True,  # Remove dwell points (stops)
            dwell_l_length=5.0,  # Dwell point length threshold (meters)
            dwell_n=2,  # Minimum number of points for dwell detection
            export_html=False,  # Disable HTML visualization (faster)
            export_geo_res=False,  # Disable GeoJSON export (faster)
            use_gps_source=False,  # Don't use original GPS as fallback
            gps_radius=15.0,  # GPS point radius for matching (meters)
            export_all_agents=False,  # Only export matched results
            out_fldr=os.path.join(self.output_folder, "mapmatching")
        )
        print("   ✅ MapMatch initialized with recommended parameters")

        match_results = []

        with tqdm(
                total=total_agents,
                desc="Processing agents",
                file=self.progress_output,
                dynamic_ncols=True,
                ascii=True,
                bar_format="{desc}: {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        ) as pbar:
            for _, (agent_id, agent_data) in enumerate(gps_df.groupby("agent_id")):
                if self.stop_event and self.stop_event.is_set():
                    self.progress_output.write("Stopping Map Matching process...")
                    return

                match_res, _, _ = mpm.execute(gps_df=agent_data)

                match_results.append(match_res)

                pbar.update(1)

        self.progress_output.write("Map Matching Completed")

        # Save results
        final_match_res = pd.concat(match_results, ignore_index=True)

        output_mapmatching_dir = os.path.join(self.output_folder, "mapmatching")
        os.makedirs(output_mapmatching_dir, exist_ok=True)

        output_mapmatching_path = os.path.join(self.output_folder, "mapmatching", "mapmatching.csv")
        final_match_res.to_csv(output_mapmatching_path, encoding='utf_8_sig', index=False)

    def insert_map_matching_results(self):
        """Reads mapmatching.csv and inserts it into the SQLite database."""
        output_mapmatching_path = os.path.join(self.output_folder, "mapmatching", "mapmatching.csv")

        # Read the CSV file
        df = pd.read_csv(output_mapmatching_path)

        # Infer column types using CSVToSQLiteProcessor
        column_types = CSVToSQLiteProcessor._infer_column_types(self, df)

        # Connect to SQLite
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        table_name = "map_matching"
        columns_sql = ", ".join([f"{col} {col_type}" for col, col_type in column_types.items()])
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
        cursor.execute(create_table_query)

        # Insert data
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        # Commit and close connection
        conn.commit()
        conn.close()

    def run(self):
        """Runs the full pipeline for processing network data and map matching."""
        self.process_network()
        self.perform_map_matching()
        self.insert_map_matching_results()


class MapMatchingAnalyzer:
    def __init__(self, database_path):
        """Initializes database path."""
        self.database_path = database_path
        self.conn = sqlite3.connect(database_path)


    # def analyze_matching_coverage(self):
    #     """Analyzes the percentage of matched journeys and data coverage."""
    #     # Load data
    #     waypoint_df = pd.read_sql("SELECT journey_id FROM waypoint", self.conn)
    #     map_matching_df = pd.read_sql("SELECT agent_id FROM map_matching", self.conn)
    #
    #     # Compute percentages
    #     total_journeys = waypoint_df["journey_id"].nunique()
    #     matched_agents = map_matching_df["agent_id"].nunique()
    #
    #     total_waypoint_rows = len(waypoint_df)
    #     total_mapmatching_rows = len(map_matching_df)
    #
    #     journey_match_percentage = (matched_agents / total_journeys) * 100 if total_journeys > 0 else 0
    #     data_match_percentage = (total_mapmatching_rows / total_waypoint_rows) * 100 if total_waypoint_rows > 0 else 0
    #
    #     print(f"{matched_agents}/{total_journeys} ({journey_match_percentage:.2f}%) agents matched")
    #     print(f"{total_mapmatching_rows}/{total_waypoint_rows} ({data_match_percentage:.2f}%) waypoint matched")

    def analyze_matching_coverage(self):
        """Analyzes the percentage of matched journeys and data coverage."""
        # Load data
        waypoint_df = pd.read_sql("SELECT journey_id FROM waypoint", self.conn)
        map_matching_df = pd.read_sql("SELECT DISTINCT agent_id FROM map_matching", self.conn)

        # Find matched journey_ids from waypoint using agent_id
        matched_journeys = pd.read_sql(
            "SELECT DISTINCT journey_id FROM waypoint WHERE journey_id IN (SELECT agent_id FROM map_matching)",
            self.conn
        )

        # Total number of journey_ids in waypoint
        total_journeys = waypoint_df["journey_id"].nunique()

        # Number of matched journey_ids
        matched_journey_count = matched_journeys["journey_id"].nunique()

        # Compute total data points in waypoint for matched journeys
        matched_waypoint_count = pd.read_sql(
            f"SELECT COUNT(*) AS count FROM waypoint WHERE journey_id IN (SELECT agent_id FROM map_matching)",
            self.conn
        )["count"].iloc[0]

        # Total map_matching rows
        total_mapmatching_rows = pd.read_sql(
            "SELECT COUNT(*) AS count FROM map_matching",
            self.conn
        )["count"].iloc[0]

        # Compute percentages
        journey_match_percentage = (matched_journey_count / total_journeys) * 100 if total_journeys > 0 else 0
        data_match_percentage = (total_mapmatching_rows / matched_waypoint_count) * 100 if matched_waypoint_count > 0 else 0

        print(f"{matched_journey_count}/{total_journeys} ({journey_match_percentage:.2f}%) journeys matched")
        print(f"{total_mapmatching_rows}/{matched_waypoint_count} ({data_match_percentage:.2f}%) waypoint matched")

    def run(self):
        """Runs the full pipeline for processing network data and map matching."""
        self.analyze_matching_coverage()

        self.conn.close()


if __name__ == "__main__":
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    DEFAULT_INPUT_FOLDER = os.path.join(PROJECT_ROOT, "data", "input")
    DEFAULT_OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, "data", "output")
    DEFAULT_DATABASE_PATH = os.path.join(DEFAULT_OUTPUT_FOLDER, "database", "unified_database.db")


    mapmatching_processor = MapMatchingProcessor(DEFAULT_INPUT_FOLDER, DEFAULT_OUTPUT_FOLDER)
    mapmatching_processor.run()

    # mapmatching_analyzer = MapMatchingAnalyzer(DEFAULT_DATABASE_PATH)
    # mapmatching_analyzer.run()