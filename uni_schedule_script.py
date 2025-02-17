import pandas as pd

# Load the Excel file
file_path = "D:\C_DRIVE DATA\DESKTOP\Spring Schedule 2025.xlsx"
df = pd.read_excel(file_path)

# Define a function to determine the day dynamically
def detect_day(column):
    if "Mon" in column["Monday / Wednesday"] or "Wed" in column["Monday / Wednesday"]:
        return "M/W"
    elif "Tue" in column["Tuesday / Thursday"] or "Thu" in column["Tuesday / Thursday"]:
        return "T/Th"
    elif "Fri" in column["Friday / Saturday"] or "Sat" in column["Friday / Saturday"]:
        return "F/S"
    else:
        return "Unknown"

# Assuming there's a column that contains day information, update its name accordingly
df = df.rename(columns={
    "Timings": "Time",
    "Course Name": "Course Name",
    "Class & Program": "Program",
    "UMS ClassNo.": "Class Code",
    "Teacher": "Teacher"
})

# Create a new "Day" column using the function
df["Day"] = df.apply(detect_day, axis=1)

# Select and reorder required columns
df = df[["Course Name", "Program", "Class Code", "Day", "Time", "Teacher"]]

# Save the formatted dataset
df.to_excel("formatted_timetable.xlsx", index=False)

print("Dataset successfully converted and saved as 'formatted_timetable.xlsx'.")


#