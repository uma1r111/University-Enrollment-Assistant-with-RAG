import pandas as pd

# Load the Excel file
file_path = "Spring Schedule 2025.xlsx"
xls = pd.ExcelFile(file_path)

# Read the main schedule sheet (adjust the sheet name if necessary)
df = xls.parse("Undergrad Schedule Spring 2025-")

# Drop initial metadata rows (assuming first 5 rows are headers or irrelevant)
df = df.iloc[5:].reset_index(drop=True)

# Load first sheet with correct header row (adjust header index if needed)
df = pd.read_excel(file_path, sheet_name=0, header=2)  # Use header=1 or header=2 based on actual data

# Rename columns based on observed structure
df.columns = [
    "Timings", "Monday/Wednesday", "MW_Course", "MW_Code", "MW_Teacher", "Extra1", 
    "Tuesday/Thursday", "TT_Course", "TT_Code", "TT_Teacher", "Extra2", 
    "Friday/Saturday", "FS_Course", "FS_Code", "FS_Teacher", "Extra3", "code"
]

# Select only relevant columns
df = df[["Timings", "MW_Course", "MW_Code", "MW_Teacher", "TT_Course", "TT_Code", "TT_Teacher", "FS_Course", "FS_Code", "FS_Teacher"]]

# Reshape data to long format
mw = df[["Timings", "MW_Course", "MW_Code", "MW_Teacher"]].dropna()
mw["Day"] = "M/W"
mw.columns = ["Time", "Course Name", "Class Code", "Teacher", "Day"]

tt = df[["Timings", "TT_Course", "TT_Code", "TT_Teacher"]].dropna()
tt["Day"] = "T/Th"
tt.columns = ["Time", "Course Name", "Class Code", "Teacher", "Day"]

fs = df[["Timings", "FS_Course", "FS_Code", "FS_Teacher"]].dropna()
fs["Day"] = "F/S"
fs.columns = ["Time", "Course Name", "Class Code", "Teacher", "Day"]

# Combine all days into a single DataFrame
final_df = pd.concat([mw, tt, fs], ignore_index=True)

# Add a placeholder 'Program' column (update if program info is available)
final_df["Program"] = "BSCS-8"  # Change this if different programs exist

# Reorder columns
final_df = final_df[["Course Name", "Program", "Class Code", "Day", "Time", "Teacher"]]

# Save to a new Excel file
output_file = "Formatted_Schedule.xlsx"
final_df.to_excel(output_file, index=False)

print(f"Formatted schedule saved to: {output_file}")
