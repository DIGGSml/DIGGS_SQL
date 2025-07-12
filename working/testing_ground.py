import pandas as pd
import openpyxl

def generate_headings_diagram(excel_file_path):
    # Load the Excel file
    excel_data = pd.ExcelFile('working/Geotechnical_Schema.xlsx')
    
    # Iterate over each sheet name
    for sheet_name in excel_data.sheet_names:
        # Read the sheet data into a DataFrame
        df = excel_data.parse(sheet_name)
        
        # Get the column headers
        headers = df.columns.tolist()
        
        # Generate a text diagram
        print(f"Sheet: {sheet_name}")
        print("Headings:")
        print(" + " + " + ".join(["-" * len(header) for header in headers]) + " + ")
        print(" | " + " | ".join([header.center(len(header)) for header in headers]) + " | ")
        print(" + " + " + ".join(["-" * len(header) for header in headers]) + " + ")
        print("\n")

# Example usage:
excel_file_path = 'path/to/your/excel_file.xlsx'
generate_headings_diagram(excel_file_path)