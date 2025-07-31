from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from typing import List, Optional, Dict, Any
import csv
import io
import os
import json
from datetime import datetime
import pandas as pd

router = APIRouter(prefix="/csv", tags=["csv"])

# @router.post("/readcsv")
# async def read_csv(
#     file: UploadFile = File(...),
#     delimiter: str = Form(",", description="CSV delimiter (e.g., comma, tab, semicolon)"),
#     has_header: bool = Form(True, description="Whether the CSV has a header row"),
#     skip_rows: int = Form(0, description="Number of rows to skip from the beginning"),
#     max_rows: Optional[int] = Form(None, description="Maximum number of rows to read (None for all)"),
#     infer_types: bool = Form(True, description="Try to infer data types automatically")
# ):
#     """
#     Read and parse a CSV file dynamically with configurable options.
#     Returns the parsed data as a structured JSON response.
#     """
#     if not file.filename.lower().endswith(('.csv', '.txt')):
#         raise HTTPException(status_code=400, detail="File must be a CSV or TXT file")
    
#     try:
#         # Read file content
#         contents = await file.read()
        
#         # Handle different delimiter inputs
#         if delimiter.lower() in ["tab", "\\t", "t"]:
#             delimiter = "\t"
#         elif delimiter.lower() in ["semicolon", ";"]:
#             delimiter = ";"
#         elif delimiter.lower() in ["comma", ","]:
#             delimiter = ","
#         elif delimiter.lower() in ["pipe", "|"]:
#             delimiter = "|"
#         elif delimiter.lower() in ["space", " "]:
#             delimiter = " "
        
#         # Use pandas for more powerful CSV parsing
#         try:
#             # Create a file-like object from the contents
#             csv_file = io.StringIO(contents.decode('utf-8'))
            
#             # Parse with pandas
#             df = pd.read_csv(
#                 csv_file,
#                 delimiter=delimiter,
#                 header=0 if has_header else None,
#                 skiprows=skip_rows,
#                 nrows=max_rows,
#                 dtype=None if infer_types else str,
#                 na_values=['NA', 'N/A', ''],
#                 keep_default_na=True,
#                 engine='python'  # More flexible engine
#             )
            
#             # Get column statistics if there's enough data
#             stats = {}
#             if len(df) > 0 and infer_types:
#                 for col in df.columns:
#                     if pd.api.types.is_numeric_dtype(df[col]):
#                         stats[col] = {
#                             "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
#                             "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
#                             "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
#                             "type": str(df[col].dtype)
#                         }
#                     else:
#                         # For non-numeric columns, count unique values
#                         stats[col] = {
#                             "unique_values": df[col].nunique(),
#                             "type": str(df[col].dtype)
#                         }
            
#             # Convert to records for JSON serialization
#             records = df.fillna("").to_dict(orient='records')
            
#             # Get schema information (column names and types)
#             schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
            
#             return {
#                 "success": True,
#                 "filename": file.filename,
#                 "total_rows": len(df),
#                 "total_columns": len(df.columns),
#                 "columns": list(df.columns) if has_header else [f"Column_{i}" for i in range(len(df.columns))],
#                 "schema": schema,
#                 "statistics": stats if infer_types else {},
#                 "data": records[:100],  # Limit initial response to 100 rows
#                 "preview": True if len(records) > 100 else False
#             }
            
#         except Exception as e:
#             # Fall back to basic CSV reader if pandas fails
#             csv_file = io.StringIO(contents.decode('utf-8'))
            
#             # Determine if we should use the first row as headers
#             csv_reader = csv.reader(csv_file, delimiter=delimiter)
            
#             # Skip rows if needed
#             for _ in range(skip_rows):
#                 next(csv_reader, None)
            
#             # Read header if applicable
#             headers = next(csv_reader, []) if has_header else None
            
#             # If no headers provided, generate column names
#             if not headers:
#                 # Read one row to determine column count
#                 first_row = next(csv_reader, [])
#                 column_count = len(first_row)
#                 headers = [f"Column_{i}" for i in range(column_count)]
#                 # Reset to beginning to re-read this row as data
#                 csv_file.seek(0)
#                 csv_reader = csv.reader(csv_file, delimiter=delimiter)
#                 # Skip rows again
#                 for _ in range(skip_rows):
#                     next(csv_reader, None)
#                 if has_header:
#                     next(csv_reader, None)  # Skip header row
            
#             # Read data rows
#             data = []
#             for i, row in enumerate(csv_reader):
#                 if max_rows is not None and i >= max_rows:
#                     break
                    
#                 # Create dict with row values
#                 row_dict = {}
#                 for j, value in enumerate(row):
#                     if j < len(headers):
#                         row_dict[headers[j]] = value
#                     else:
#                         # Handle case where row has more values than headers
#                         row_dict[f"Column_{j}"] = value
                        
#                 data.append(row_dict)
            
#             return {
#                 "success": True,
#                 "filename": file.filename,
#                 "total_rows": len(data),
#                 "total_columns": len(headers),
#                 "columns": headers,
#                 "data": data[:100],  # Limit initial response to 100 rows
#                 "preview": True if len(data) > 100 else False
#             }
            
#     except UnicodeDecodeError:
#         raise HTTPException(status_code=400, detail="Could not decode file as UTF-8. Try another encoding.")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

# @router.post("/analyze")
# async def analyze_csv(
#     file: UploadFile = File(...),
#     delimiter: str = Form(",", description="CSV delimiter"),
#     has_header: bool = Form(True, description="Whether the CSV has a header row")
# ):
#     """
#     Analyze a CSV file and return statistical information about its contents.
#     """
#     if not file.filename.lower().endswith(('.csv', '.txt')):
#         raise HTTPException(status_code=400, detail="File must be a CSV or TXT file")
    
#     try:
#         # Read file content
#         contents = await file.read()
        
#         # Normalize delimiter
#         if delimiter.lower() in ["tab", "\\t", "t"]:
#             delimiter = "\t"
#         elif delimiter.lower() in ["semicolon", ";"]:
#             delimiter = ";"
        
#         # Use pandas for analysis
#         csv_file = io.StringIO(contents.decode('utf-8'))
#         df = pd.read_csv(
#             csv_file,
#             delimiter=delimiter,
#             header=0 if has_header else None,
#             engine='python'
#         )
        
#         # Generate descriptive statistics
#         analysis = {
#             "row_count": len(df),
#             "column_count": len(df.columns),
#             "columns": {}
#         }
        
#         # Analyze each column
#         for col in df.columns:
#             col_data = {
#                 "type": str(df[col].dtype),
#                 "missing_values": int(df[col].isna().sum()),
#                 "missing_percentage": float(df[col].isna().mean() * 100)
#             }
            
#             # Add numeric statistics if applicable
#             if pd.api.types.is_numeric_dtype(df[col]):
#                 col_data.update({
#                     "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
#                     "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
#                     "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
#                     "median": float(df[col].median()) if not pd.isna(df[col].median()) else None,
#                     "std_dev": float(df[col].std()) if not pd.isna(df[col].std()) else None
#                 })
#             else:
#                 # For non-numeric columns
#                 col_data.update({
#                     "unique_values": int(df[col].nunique()),
#                     "most_common": df[col].value_counts().head(5).to_dict() if not df[col].isna().all() else {}
#                 })
            
#             analysis["columns"][col] = col_data
        
#         return analysis
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error analyzing CSV: {str(e)}")

@router.post("/convert")
async def convert_csv(
    file: UploadFile = File(...),
    output_format: str = Form(..., description="Output format (json, excel, html, xml)"),
    delimiter: str = Form(",", description="Input CSV delimiter"),
    has_header: bool = Form(True, description="Whether the CSV has a header row")
):
    """
    Convert a CSV file to different formats (JSON, Excel, HTML, XML, PDF).
    """
    if not file.filename.lower().endswith(('.csv', '.txt')):
        raise HTTPException(status_code=400, detail="File must be a CSV or TXT file")
    
    if output_format.lower() not in ["json", "excel", "html", "xml"]:
        raise HTTPException(status_code=400, detail="Supported output formats: json, excel, html, xml")
    
    try:
        # Read file content
        contents = await file.read()
        
        # Normalize delimiter
        if delimiter.lower() in ["tab", "\\t", "t"]:
            delimiter = "\t"
        elif delimiter.lower() in ["semicolon", ";"]:
            delimiter = ";"
        
        # Use pandas for conversion
        csv_file = io.StringIO(contents.decode('utf-8'))
        df = pd.read_csv(
            csv_file,
            delimiter=delimiter,
            header=0 if has_header else None,
            engine='python'
        )
        
        # Create output filename
        filename_base = os.path.splitext(file.filename)[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convert to requested format
        output_buffer = io.BytesIO()
        
        if output_format.lower() == "json":
            # Convert to JSON
            json_data = df.to_json(orient="records", date_format="iso")
            output_buffer.write(json_data.encode('utf-8'))
            media_type = "application/json"
            output_filename = f"{filename_base}_{timestamp}.json"
            
        elif output_format.lower() == "excel":
            # Convert to Excel
            df.to_excel(output_buffer, index=False, engine="openpyxl")
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            output_filename = f"{filename_base}_{timestamp}.xlsx"
            
        elif output_format.lower() == "html":
            # Convert to HTML
            html_table = df.to_html(index=False)
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>CSV Data</title>
                <style>
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ padding: 8px; text-align: left; border: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                </style>
            </head>
            <body>
                <h1>CSV Data: {file.filename}</h1>
                {html_table}
            </body>
            </html>
            """
            output_buffer.write(html_content.encode('utf-8'))
            media_type = "text/html"
            output_filename = f"{filename_base}_{timestamp}.html"
            
        elif output_format.lower() == "xml":
            # Convert to XML
            xml_content = df.to_xml(index=False)
            output_buffer.write(xml_content.encode('utf-8'))
            media_type = "application/xml"
            output_filename = f"{filename_base}_{timestamp}.xml"
            
        # Prepare the file for download
        output_buffer.seek(0)
        
        from fastapi.responses import Response
        return Response(
            content=output_buffer.getvalue(),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}",
                "X-Converted-From": file.filename,
                "X-Rows-Count": str(len(df))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting CSV: {str(e)}")