"""
Export Utilities

Functions for exporting extracted data to various formats.
Supports Excel (XLSX), CSV, and JSON exports.
"""

import json
from typing import List, Dict, Any
from datetime import date, datetime

import pandas as pd


def export_to_excel(data: List[Dict[str, Any]], output_path: str) -> None:
    """
    Export extracted data to an Excel file.
    
    Creates a well-formatted Excel file with:
    - Auto-adjusted column widths
    - Header formatting
    - Proper data types
    
    Args:
        data: List of extracted data dictionaries
        output_path: Path for the output Excel file
    """
    if not data:
        raise ValueError("No data to export")
    
    # Flatten nested structures for Excel
    flat_data = [flatten_dict(item) for item in data]
    
    # Create DataFrame
    df = pd.DataFrame(flat_data)
    
    # Reorder columns to put important ones first
    priority_columns = [
        'source_file', 'document_type', 'invoice_number', 'date',
        'vendor_name', 'store_name', 'employee_name',
        'total_amount', 'total', 'net_salary'
    ]
    
    # Get columns in priority order, then remaining columns
    ordered_cols = [col for col in priority_columns if col in df.columns]
    remaining_cols = [col for col in df.columns if col not in ordered_cols]
    df = df[ordered_cols + remaining_cols]
    
    # Write to Excel with formatting
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Extracted Data')
        
        # Get the worksheet
        worksheet = writer.sheets['Extracted Data']
        
        # Auto-adjust column widths
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).map(len).max(),
                len(str(col))
            ) + 2
            
            # Cap width at 50 characters
            column_width = min(max_length, 50)
            
            # Convert index to Excel column letter
            col_letter = get_column_letter(idx + 1)
            worksheet.column_dimensions[col_letter].width = column_width


def export_to_json(data: List[Dict[str, Any]], output_path: str) -> None:
    """
    Export extracted data to a JSON file.
    
    Args:
        data: List of extracted data dictionaries
        output_path: Path for the output JSON file
    """
    # Convert dates to strings for JSON serialization
    serializable_data = make_json_serializable(data)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, indent=2, ensure_ascii=False)


def export_to_csv(data: List[Dict[str, Any]], output_path: str) -> None:
    """
    Export extracted data to a CSV file.
    
    Args:
        data: List of extracted data dictionaries
        output_path: Path for the output CSV file
    """
    if not data:
        raise ValueError("No data to export")
    
    # Flatten nested structures
    flat_data = [flatten_dict(item) for item in data]
    
    # Create DataFrame and export
    df = pd.DataFrame(flat_data)
    df.to_csv(output_path, index=False, encoding='utf-8')


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.
    
    Converts nested structures like:
    {'line_items': [{'name': 'A', 'price': 10}]}
    
    To flat structures like:
    {'line_items_0_name': 'A', 'line_items_0_price': 10}
    
    Args:
        d: Dictionary to flatten
        parent_key: Prefix for keys (used in recursion)
        sep: Separator between key levels
        
    Returns:
        Flattened dictionary
    """
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        elif isinstance(v, list):
            # For lists, either join simple values or flatten dicts
            if not v:
                items.append((new_key, None))
            elif isinstance(v[0], dict):
                # Flatten each item in the list
                for i, item in enumerate(v):
                    items.extend(flatten_dict(item, f"{new_key}_{i}", sep).items())
            else:
                # Join simple values
                items.append((new_key, ', '.join(str(x) for x in v)))
        else:
            items.append((new_key, v))
    
    return dict(items)


def make_json_serializable(data: Any) -> Any:
    """
    Convert data to JSON-serializable format.
    
    Handles dates, datetimes, and other non-serializable types.
    
    Args:
        data: Data to convert
        
    Returns:
        JSON-serializable version of the data
    """
    if isinstance(data, dict):
        return {k: make_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_serializable(item) for item in data]
    elif isinstance(data, (date, datetime)):
        return data.isoformat()
    elif isinstance(data, (int, float, str, bool, type(None))):
        return data
    else:
        return str(data)


def get_column_letter(col_num: int) -> str:
    """
    Convert a column number to Excel column letter.
    
    Args:
        col_num: Column number (1-indexed)
        
    Returns:
        Column letter (A, B, ..., Z, AA, AB, ...)
    """
    result = ""
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        result = chr(65 + remainder) + result
    return result
