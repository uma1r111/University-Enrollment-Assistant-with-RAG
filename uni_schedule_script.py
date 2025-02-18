import pandas as pd

# Load the Excel file
file_path = "Spring Schedule 2025.xlsx"
df = pd.read_excel(file_path, sheet_name=None)  # Load all sheets

# Define the mapping for days
day_mapping = {
    "Monday / Wednesday": "M/W",
    "Tuesday / Thursday": "T/Th",
    "Friday / Saturday": "F/S"
}

# Process each sheet and convert it into a standard format
final_df = pd.DataFrame()

for sheet, data in df.items():
    # Rename columns to match standard format
    data = data.rename(columns={
        "Course Name": "Course Name",
        "Class & Program": "Program",
        "UMS ClassNo.": "Class Code",
        "Timings": "Time",
        "Teacher": "Teacher"
    })

    # Assign the correct day based on the sheet name
    data["Day"] = day_mapping.get(sheet, "Unknown")

    # Keep only relevant columns
    data = data[["Course Name", "Program", "Class Code", "Day", "Time", "Teacher"]]

    # Append to final dataframe
    final_df = pd.concat([final_df, data], ignore_index=True)

# Save the formatted data
final_df.to_excel("Formatted_Schedule.xlsx", index=False)
print("File has been formatted and saved as 'Formatted_Schedule.xlsx'.")
