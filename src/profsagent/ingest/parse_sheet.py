import csv
import json
import os
import glob
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PARSED_DIR = BASE_DIR / "data" / "parsed"

def determine_section(row_str):
    """
    Given the first cell of a row, determine if it starts a new section.
    Returns the section name, or None if it's not a section header.
    """
    row_str = row_str.strip().lower()
    if not row_str:
        return None
    
    if "pre-requisite" in row_str or "prerequisite" in row_str:
        return "prerequisites"
    elif "post condition" in row_str or "course outcome" in row_str:
        return "outcomes"
    elif "weekly lecture" in row_str:
        return "lecture_plan"
    elif "weekly lab" in row_str:
        return "lab_plan"
    elif "assessment plan" in row_str:
        return "assessment_plan"
    elif "resource material" in row_str:
        return "resources"
        
    return None

def parse_csv(csv_path):
    """
    Parses a syllabus CSV and returns sections with cell coordinates.
    Format: { "sections": { "section_name": { "cells": [[r, c, "text"]] } }, "template_version": "v1" }
    """
    sections_data = {
        "header": {"cells": []},
        "prerequisites": {"cells": []},
        "outcomes": {"cells": []},
        "lecture_plan": {"cells": []},
        "lab_plan": {"cells": []},
        "assessment_plan": {"cells": []},
        "resources": {"cells": []}
    }
    
    current_section = "header"
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for r_idx, row in enumerate(reader):
            if not row:
                continue
                
            # Check if this row starts a new section
            first_cell = row[0]
            new_section = determine_section(first_cell)
            if new_section:
                current_section = new_section
                
            # Add all non-empty cells in the row to the current section
            for c_idx, cell in enumerate(row):
                cell_val = cell.strip()
                if cell_val:
                    sections_data[current_section]["cells"].append([r_idx, c_idx, cell_val])
                    
    # Clean up empty sections
    sections_data = {k: v for k, v in sections_data.items() if len(v["cells"]) > 0}
    
    return {
        "sections": sections_data,
        "template_version": "v1"  # Simplified for now, can be deduced from headers
    }

def main():
    DATA_PARSED_DIR.mkdir(parents=True, exist_ok=True)
    
    csv_files = glob.glob(str(DATA_RAW_DIR / "*.csv"))
    print(f"Found {len(csv_files)} CSV files to parse.")
    
    success_count = 0
    
    for csv_file in csv_files:
        code = Path(csv_file).stem
        try:
            parsed_data = parse_csv(csv_file)
            
            # Save parsed JSON
            out_path = DATA_PARSED_DIR / f"{code}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(parsed_data, f, indent=4)
                
            success_count += 1
        except Exception as e:
            print(f"Failed to parse {code}: {e}")
            
    print(f"Parsed {success_count} / {len(csv_files)} files successfully.")

if __name__ == "__main__":
    main()
