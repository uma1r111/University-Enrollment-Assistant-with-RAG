import pandas as pd
import re

# Load the Excel file
file_path = "Transformed_Schedule_Final.xlsx"
sheet_name = "Sheet1"  # Change if the sheet name is different

# Read the Excel file
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Function to remove courtesy titles
def clean_teacher_name(name):
    if pd.notna(name):  # Ensure the name is not NaN
        return re.sub(r"^(Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)\s*", "", name).strip()
    return name

# Apply the cleaning function to the "Teacher" column
if "Teacher" in df.columns:
    df["Teacher"] = df["Teacher"].apply(clean_teacher_name)
else:
    print("Column 'Teacher' not found in the dataset.")

# Save the cleaned data to a new Excel file
output_file = "Transformed_Schedule_Cleaned.xlsx"
df.to_excel(output_file, index=False)

print(f"Courtesy titles removed. Cleaned file saved as '{output_file}'.")
