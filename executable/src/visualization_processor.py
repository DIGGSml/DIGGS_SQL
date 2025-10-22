import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from .processor_interfaces import DataProcessor
import os

# Skip seaborn import to avoid pyzmq dependency in executable
# Use matplotlib styling instead
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
sns = None

class DatabaseVisualizationProcessor(DataProcessor):
    """Interactive visualization tool for SQLite geotechnical databases"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.db_path = None
        self.connection = None
        self.table_data = {}
        
    def get_processor_type(self) -> str:
        return "visualization"
    
    def validate_input(self, input_path: str) -> bool:
        """Validate SQLite database file"""
        if not os.path.exists(input_path):
            return False
        
        try:
            conn = sqlite3.connect(input_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            return len(tables) > 0
        except sqlite3.Error:
            return False
    
    def process(self, input_path: str, output_path: str = None, **kwargs) -> bool:
        """Launch interactive visualization interface"""
        if not self.validate_input(input_path):
            return False
        
        self.db_path = input_path
        self.launch_visualization_interface()
        return True
    
    def connect_to_database(self) -> bool:
        """Connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not connect to database: {e}")
            return False
    
    def get_table_list(self) -> List[str]:
        """Get list of all tables in database"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        return [table[0] for table in cursor.fetchall()]
    
    def get_table_data(self, table_name: str, limit: int = 1000) -> pd.DataFrame:
        """Get data from specified table"""
        if not self.connection:
            return pd.DataFrame()
        
        try:
            query = f"SELECT * FROM `{table_name}` LIMIT {limit}"
            return pd.read_sql_query(query, self.connection)
        except Exception as e:
            messagebox.showerror("Query Error", f"Error loading table {table_name}: {e}")
            return pd.DataFrame()
    
    def get_table_info(self, table_name: str) -> List[Tuple[str, str]]:
        """Get column information for specified table"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA table_info(`{table_name}`)")
        return [(col[1], col[2]) for col in cursor.fetchall()]
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for specified table"""
        if not self.connection:
            return 0
        
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
        return cursor.fetchone()[0]
    
    def create_summary_visualization(self, ax) -> None:
        """Create database summary visualization"""
        tables = self.get_table_list()
        if not tables:
            ax.text(0.5, 0.5, 'No tables found in database', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Get row counts for each table
        table_counts = []
        table_names = []
        
        for table in tables[:20]:  # Limit to top 20 tables
            count = self.get_table_count(table)
            if count > 0:
                table_counts.append(count)
                table_names.append(table)
        
        if table_counts:
            # Create horizontal bar chart
            y_pos = np.arange(len(table_names))
            ax.barh(y_pos, table_counts, color='skyblue', alpha=0.7)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(table_names)
            ax.set_xlabel('Number of Records')
            ax.set_title('Database Table Summary')
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'No data found in database tables', 
                   ha='center', va='center', transform=ax.transAxes)
    
    def create_borehole_map(self, ax) -> None:
        """Create borehole location map if coordinate data exists"""
        try:
            query = """
            SELECT holeName, topLatitude, topLongitude, bottomDepth 
            FROM _HoleInfo 
            WHERE topLatitude IS NOT NULL AND topLongitude IS NOT NULL
            """
            df = pd.read_sql_query(query, self.connection)
            
            if df.empty:
                ax.text(0.5, 0.5, 'No borehole location data available', 
                       ha='center', va='center', transform=ax.transAxes)
                return
            
            # Create scatter plot
            scatter = ax.scatter(df['topLongitude'], df['topLatitude'], 
                               c=df['bottomDepth'], cmap='viridis', 
                               s=50, alpha=0.7)
            
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.set_title('Borehole Locations')
            ax.grid(True, alpha=0.3)
            
            # Add colorbar for depth
            plt.colorbar(scatter, ax=ax, label='Depth (ft)')
            
            # Add labels for boreholes
            for idx, row in df.iterrows():
                if pd.notna(row['holeName']):
                    ax.annotate(row['holeName'], 
                               (row['topLongitude'], row['topLatitude']),
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=8, alpha=0.8)
        
        except Exception as e:
            ax.text(0.5, 0.5, f'Error creating borehole map: {str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
    
    def create_spt_analysis(self, ax) -> None:
        """Create SPT blow count analysis"""
        try:
            query = """
            SELECT s._Sample_ID, s.pos_topDepth, s.pos_bottomDepth,
                   spt.blowCount_index1, spt.blowCount_index2, spt.blowCount_index3,
                   spt.totalPenetration, h.holeName
            FROM _Samples s
            JOIN _SPT spt ON s._Sample_ID = spt._Sample_ID
            JOIN _HoleInfo h ON s._holeID = h._holeID
            WHERE spt.blowCount_index1 >= 0 AND spt.blowCount_index2 >= 0 AND spt.blowCount_index3 >= 0
            """
            df = pd.read_sql_query(query, self.connection)
            
            if df.empty:
                ax.text(0.5, 0.5, 'No SPT data available', 
                       ha='center', va='center', transform=ax.transAxes)
                return
            
            # Calculate N-values (sum of last two increments)
            df['N_value'] = df['blowCount_index2'] + df['blowCount_index3']
            df['avg_depth'] = (df['pos_topDepth'] + df['pos_bottomDepth']) / 2
            
            # Create scatter plot
            ax.scatter(df['N_value'], df['avg_depth'], alpha=0.6, s=30)
            ax.set_xlabel('SPT N-Value')
            ax.set_ylabel('Depth (ft)')
            ax.set_title('SPT Blow Count vs Depth')
            ax.invert_yaxis()  # Depth increases downward
            ax.grid(True, alpha=0.3)
            
            # Add trend line
            if len(df) > 1:
                z = np.polyfit(df['N_value'], df['avg_depth'], 1)
                p = np.poly1d(z)
                ax.plot(sorted(df['N_value']), p(sorted(df['N_value'])), 
                       "r--", alpha=0.8, linewidth=1)
        
        except Exception as e:
            ax.text(0.5, 0.5, f'Error creating SPT analysis: {str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
    
    def create_atterberg_plot(self, ax) -> None:
        """Create Atterberg limits plasticity chart"""
        try:
            query = """
            SELECT plasticLimit, liquidLimit, plasticityIndex
            FROM AtterbergLimits
            WHERE plasticLimit IS NOT NULL AND liquidLimit IS NOT NULL 
            AND plasticityIndex IS NOT NULL
            """
            df = pd.read_sql_query(query, self.connection)
            
            if df.empty:
                ax.text(0.5, 0.5, 'No Atterberg Limits data available', 
                       ha='center', va='center', transform=ax.transAxes)
                return
            
            # Create plasticity chart
            ax.scatter(df['liquidLimit'], df['plasticityIndex'], alpha=0.6, s=40)
            ax.set_xlabel('Liquid Limit (%)')
            ax.set_ylabel('Plasticity Index (%)')
            ax.set_title('Plasticity Chart (Atterberg Limits)')
            ax.grid(True, alpha=0.3)
            
            # Add A-line (plasticity chart boundary)
            ll_range = np.linspace(0, max(df['liquidLimit']) * 1.1, 100)
            a_line = 0.73 * (ll_range - 20)
            ax.plot(ll_range, a_line, 'r-', label='A-line', alpha=0.8)
            
            # Add U-line
            u_line = 0.9 * (ll_range - 8)
            ax.plot(ll_range, u_line, 'b--', label='U-line', alpha=0.8)
            
            ax.legend()
            ax.set_xlim(0, max(df['liquidLimit']) * 1.1)
            ax.set_ylim(0, max(df['plasticityIndex']) * 1.1)
        
        except Exception as e:
            ax.text(0.5, 0.5, f'Error creating Atterberg plot: {str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
    
    def launch_visualization_interface(self) -> None:
        """Launch the main visualization interface"""
        if not self.connect_to_database():
            return
        
        # Create main window
        root = tk.Tk()
        root.title(f"DIGGS Database Visualization - {os.path.basename(self.db_path)}")
        root.geometry("1200x800")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Database Overview
        self.create_overview_tab(notebook)
        
        # Tab 2: Table Browser
        self.create_table_browser_tab(notebook)
        
        # Tab 3: Visualizations
        self.create_visualization_tab(notebook)
        
        # Tab 4: Query Tool
        self.create_query_tab(notebook)
        
        # Cleanup on close
        def on_closing():
            if self.connection:
                self.connection.close()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
    
    def create_overview_tab(self, notebook) -> None:
        """Create database overview tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Database Overview")
        
        # Create matplotlib figure
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Database Overview', fontsize=16)
        
        # Create visualizations
        self.create_summary_visualization(ax1)
        self.create_borehole_map(ax2)
        self.create_spt_analysis(ax3)
        self.create_atterberg_plot(ax4)
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_table_browser_tab(self, notebook) -> None:
        """Create table browser tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Table Browser")
        
        # Create paned window
        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - table list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Database Tables:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
        
        # Table listbox
        table_listbox = tk.Listbox(left_frame, height=15)
        table_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=table_listbox.yview)
        table_listbox.config(yscrollcommand=table_scrollbar.set)
        
        tables = self.get_table_list()
        for table in tables:
            count = self.get_table_count(table)
            table_listbox.insert(tk.END, f"{table} ({count} rows)")
        
        table_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right panel - table details
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        
        # Table info text area
        info_text = tk.Text(right_frame, height=8, wrap=tk.WORD)
        info_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=info_text.yview)
        info_text.config(yscrollcommand=info_scrollbar.set)
        
        # Table data treeview
        columns = ('Column', 'Type', 'Value')
        tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        tree_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.config(yscrollcommand=tree_scrollbar.set)
        
        # Pack right panel widgets
        ttk.Label(right_frame, text="Table Information:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, pady=5)
        info_text.pack(side=tk.LEFT, fill=tk.X, expand=True, in_=info_frame)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, in_=info_frame)
        
        ttk.Label(right_frame, text="Sample Data:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10,5))
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, in_=tree_frame)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, in_=tree_frame)
        
        # Table selection handler
        def on_table_select(event):
            selection = table_listbox.curselection()
            if selection:
                table_name = tables[selection[0]]
                
                # Update info text
                info_text.delete(1.0, tk.END)
                columns_info = self.get_table_info(table_name)
                count = self.get_table_count(table_name)
                
                info_text.insert(tk.END, f"Table: {table_name}\n")
                info_text.insert(tk.END, f"Rows: {count}\n")
                info_text.insert(tk.END, f"Columns: {len(columns_info)}\n\n")
                info_text.insert(tk.END, "Column Details:\n")
                for col_name, col_type in columns_info:
                    info_text.insert(tk.END, f"  {col_name}: {col_type}\n")
                
                # Update tree with sample data
                tree.delete(*tree.get_children())
                if count > 0:
                    df = self.get_table_data(table_name, limit=100)
                    for idx, row in df.head(20).iterrows():
                        values = []
                        for col in df.columns:
                            val = row[col]
                            if pd.isna(val):
                                val = "NULL"
                            elif isinstance(val, float):
                                val = f"{val:.3f}"
                            values.append(str(val))
                        tree.insert('', tk.END, values=values[:3])  # Show first 3 columns
        
        table_listbox.bind('<<ListboxSelect>>', on_table_select)
    
    def create_visualization_tab(self, notebook) -> None:
        """Create custom visualization tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Custom Visualizations")
        
        # Control panel
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(control_frame, text="Visualization Type:").pack(side=tk.LEFT, padx=5)
        
        viz_var = tk.StringVar(value="Borehole Map")
        viz_combo = ttk.Combobox(control_frame, textvariable=viz_var, 
                                values=["Borehole Map", "SPT Analysis", "Atterberg Chart", "Depth Profile"])
        viz_combo.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(control_frame, text="Generate Visualization")
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        # Matplotlib canvas
        fig, ax = plt.subplots(figsize=(10, 6))
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        def update_visualization():
            ax.clear()
            viz_type = viz_var.get()
            
            if viz_type == "Borehole Map":
                self.create_borehole_map(ax)
            elif viz_type == "SPT Analysis":
                self.create_spt_analysis(ax)
            elif viz_type == "Atterberg Chart":
                self.create_atterberg_plot(ax)
            elif viz_type == "Depth Profile":
                self.create_depth_profile(ax)
            
            canvas.draw()
        
        refresh_btn.config(command=update_visualization)
        update_visualization()  # Initial visualization
    
    def create_depth_profile(self, ax) -> None:
        """Create soil profile with depth"""
        try:
            query = """
            SELECT fs.pos_topDepth, fs.pos_bottomDepth, fs.primaryComp, 
                   fs.color, h.holeName
            FROM Field_Strata fs
            JOIN _HoleInfo h ON fs._holeID = h._holeID
            ORDER BY h.holeName, fs.pos_topDepth
            """
            df = pd.read_sql_query(query, self.connection)
            
            if df.empty:
                ax.text(0.5, 0.5, 'No stratigraphy data available', 
                       ha='center', va='center', transform=ax.transAxes)
                return
            
            # Color mapping for soil types
            soil_colors = {
                'CLAY': 'brown', 'SILT': 'tan', 'SAND': 'yellow', 
                'GRAVEL': 'gray', 'ROCK': 'darkgray', 'FILL': 'lightblue'
            }
            
            x_offset = 0
            hole_names = df['holeName'].unique()
            
            for hole in hole_names[:5]:  # Limit to 5 boreholes
                hole_data = df[df['holeName'] == hole]
                
                for _, row in hole_data.iterrows():
                    top = row['pos_topDepth']
                    bottom = row['pos_bottomDepth']
                    soil_type = str(row['primaryComp']).upper()
                    
                    # Find matching color
                    color = 'lightgray'  # default
                    for soil, soil_color in soil_colors.items():
                        if soil in soil_type:
                            color = soil_color
                            break
                    
                    # Draw soil layer
                    ax.barh(x_offset, 1, height=bottom-top, bottom=top, 
                           color=color, alpha=0.7, edgecolor='black', linewidth=0.5)
                    
                    # Add text label
                    ax.text(x_offset + 0.5, (top + bottom) / 2, 
                           soil_type[:4], ha='center', va='center', 
                           fontsize=8, rotation=90)
                
                # Add borehole name
                ax.text(x_offset + 0.5, 0, hole[:8], ha='center', va='bottom', 
                       fontsize=10, weight='bold')
                
                x_offset += 1.2
            
            ax.set_xlabel('Boreholes')
            ax.set_ylabel('Depth (ft)')
            ax.set_title('Soil Profile by Borehole')
            ax.invert_yaxis()
            ax.grid(True, alpha=0.3)
        
        except Exception as e:
            ax.text(0.5, 0.5, f'Error creating depth profile: {str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
    
    def create_query_tab(self, notebook) -> None:
        """Create SQL query tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="SQL Query Tool")
        
        # Query input
        query_frame = ttk.Frame(frame)
        query_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(query_frame, text="SQL Query:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        query_text = tk.Text(query_frame, height=6, wrap=tk.WORD)
        query_scrollbar = ttk.Scrollbar(query_frame, orient=tk.VERTICAL, command=query_text.yview)
        query_text.config(yscrollcommand=query_scrollbar.set)
        
        query_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        query_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sample query
        sample_query = """SELECT h.holeName, h.topLatitude, h.topLongitude, h.bottomDepth,
       COUNT(s._Sample_ID) as sample_count
FROM _HoleInfo h
LEFT JOIN _Samples s ON h._holeID = s._holeID
GROUP BY h._holeID
ORDER BY h.holeName;"""
        
        query_text.insert(tk.END, sample_query)
        
        # Execute button
        execute_btn = ttk.Button(frame, text="Execute Query")
        execute_btn.pack(pady=5)
        
        # Results area
        results_frame = ttk.Frame(frame)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(results_frame, text="Query Results:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # Results tree
        results_tree = ttk.Treeview(results_frame, show='headings')
        results_scrollbar_v = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=results_tree.yview)
        results_scrollbar_h = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=results_tree.xview)
        results_tree.config(yscrollcommand=results_scrollbar_v.set, xscrollcommand=results_scrollbar_h.set)
        
        results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        results_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        def execute_query():
            query = query_text.get(1.0, tk.END).strip()
            if not query:
                return
            
            try:
                df = pd.read_sql_query(query, self.connection)
                
                # Clear previous results
                results_tree.delete(*results_tree.get_children())
                
                # Configure columns
                results_tree["columns"] = list(df.columns)
                for col in df.columns:
                    results_tree.heading(col, text=col)
                    results_tree.column(col, width=100)
                
                # Insert data
                for _, row in df.iterrows():
                    values = [str(val) if pd.notna(val) else "NULL" for val in row]
                    results_tree.insert('', tk.END, values=values)
                
                messagebox.showinfo("Success", f"Query executed successfully. {len(df)} rows returned.")
                
            except Exception as e:
                messagebox.showerror("Query Error", f"Error executing query: {e}")
        
        execute_btn.config(command=execute_query)