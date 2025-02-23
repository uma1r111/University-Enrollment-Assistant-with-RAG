import pandas as pd

# Load the Excel file
file_path = 'Spring Schedule 2025(1).xlsx'
sheet_name = 'Sheet1'

# Read the Excel file and inspect the columns
df = pd.read_excel(file_path, sheet_name=sheet_name, header=[1])  # Assuming the second row is the header

# Print the column names to verify
print("Column Names:", df.columns.tolist())

# Initialize an empty list to store the transformed data
transformed_data = []

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    timings = row['Unnamed: 0']  # Time is in column A, which is labeled as 'Unnamed: 0'
    
    # Monday / Wednesday
    if pd.notna(row['Course Name']):
        transformed_data.append({
            'Course Name': row['Course Name'],
            'Program': row['Class & Program'],
            'Class Code': row[' UMS ClassNo.'],  # Note the leading space
            'Day': 'Monday',
            'Time': timings,
            'Teacher': row['Teacher']
        })
        transformed_data.append({
            'Course Name': row['Course Name'],
            'Program': row['Class & Program'],
            'Class Code': row[' UMS ClassNo.'],  # Note the leading space
            'Day': 'Wednesday',
            'Time': timings,
            'Teacher': row['Teacher']
        })
    
    # Tuesday / Thursday
    if pd.notna(row['Course Name.1']):
        transformed_data.append({
            'Course Name': row['Course Name.1'],
            'Program': row['Class & Program.1'],
            'Class Code': row[' UMS ClassNo..1'],  # Note the leading space
            'Day': 'Tuesday',
            'Time': timings,
            'Teacher': row['Teacher.1']
        })
        transformed_data.append({
            'Course Name': row['Course Name.1'],
            'Program': row['Class & Program.1'],
            'Class Code': row[' UMS ClassNo..1'],  # Note the leading space
            'Day': 'Thursday',
            'Time': timings,
            'Teacher': row['Teacher.1']
        })
    
    # Friday / Saturday
    if pd.notna(row['Course Name.2']):
        transformed_data.append({
            'Course Name': row['Course Name.2'],
            'Program': row['Class & Program.2'],
            'Class Code': row[' UMS ClassNo..2'],  # Note the leading space
            'Day': 'Friday',
            'Time': timings,
            'Teacher': row['Teacher.2']
        })
        transformed_data.append({
            'Course Name': row['Course Name.2'],
            'Program': row['Class & Program.2'],
            'Class Code': row[' UMS ClassNo..2'],  # Note the leading space
            'Day': 'Saturday',
            'Time': timings,
            'Teacher': row['Teacher.2']
        })

# Convert the list to a DataFrame
transformed_df = pd.DataFrame(transformed_data)

# Save the transformed data to a new Excel file
transformed_df.to_excel('Transformed_Schedule.xlsx', index=False)

print("Data transformation complete. Saved to 'Transformed_Schedule.xlsx'")